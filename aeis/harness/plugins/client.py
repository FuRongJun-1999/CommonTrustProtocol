# -*- coding: utf-8 -*-
"""harness.plugins.client · MCP Client 协议层（stdio，零依赖）
================================================
设计规格（v1.0-verified）：
- 状态机：IDLE → CONNECTING(spawn+initialize) → READY → CALLING → CLOSED / FAILED
- 版本协商：默认 2024-11-05，可降级，最多兼容 2 版本
- 单请求在途（同 client 串行）；不同 client 并行
- 流式缓冲：STREAM_BUFFER_MAX=20480，超限截断 + STREAM_TRUNCATED
- 通知忽略；非法 JSON 行跳过；超时 kill 重建（幂等重试 1 次）
"""
import json
import os
import queue
import subprocess
import threading
import time

PROTOCOL_VERSION = "2024-11-05"
PROTOCOL_ALT_VERSION = "2025-03-26"  # 兼容降级候选
STREAM_BUFFER_MAX = 20480            # 流式缓冲上限（决议 Q2）
STREAM_TRUNCATED = "STREAM_TRUNCATED"

# 状态常量
IDLE, CONNECTING, READY, CALLING, CLOSED, FAILED = (
    "idle", "connecting", "ready", "calling", "closed", "failed")


class MCPClient:
    """MCP Client：spawn 外部 server 进程，stdio JSON-RPC 2.0 通信。"""

    def __init__(self, name: str, command: list, env: dict = None,
                 cwd: str = None, timeout: float = 30.0, log=None):
        self.name = name
        self.command = list(command)
        self.env = env or {}
        self.cwd = cwd
        self.timeout = timeout
        self.log = log or (lambda *a: None)
        self.state = IDLE
        self.error = ""
        self._proc = None
        self._write_lock = threading.Lock()
        self._responses = queue.Queue()   # (id, line)
        self._reader = None
        self._id_counter = 0
        self._tools = []                  # 缓存 tools/list 结果

    # ---- 生命周期 ----

    def start(self) -> bool:
        """spawn + initialize 握手。失败返回 False（记录原因，不抛异常）。"""
        if self.state in (READY, CALLING):
            return True
        if self.state == CONNECTING:
            return False
        # 环境白名单注入（继承最小环境 + 显式 env）
        env = {}
        for k in ("PATH", "SystemRoot", "TEMP", "TMP", "LANG"):
            if os.environ.get(k):
                env[k] = os.environ[k]
        env.update(self.env)
        try:
            self._proc = subprocess.Popen(
                self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, cwd=self.cwd, env=env,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except Exception as exc:
            self.state = FAILED
            self.error = f"spawn 失败: {exc}"
            return False
        self.state = CONNECTING
        self._responses = queue.Queue()
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()
        # initialize（版本协商：默认 2024-11-05）
        ok = self._request("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "lingshu-harness", "version": "1.0"},
        }, timeout=self.timeout)
        if not ok:
            # 降级重试（最多兼容 2 版本）
            ok = self._request("initialize", {
                "protocolVersion": PROTOCOL_ALT_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "lingshu-harness", "version": "1.0"},
            }, timeout=self.timeout)
        if not ok:
            self.close()
            self.state = FAILED
            return False
        self.state = READY
        # 预取工具清单（失败不致命）
        try:
            self.list_tools()
        except Exception:
            pass
        return True

    def close(self):
        """优雅关闭：shutdown 通知 + terminate + 超时 kill。"""
        if self._proc is not None and self._proc.poll() is None:
            try:
                self._send_notify("shutdown")
            except Exception:
                pass
            try:
                self._proc.terminate()
                self._proc.wait(timeout=3)
            except Exception:
                try:
                    self._proc.kill()
                except Exception:
                    pass
        self.state = CLOSED
        self._proc = None

    def health(self) -> bool:
        """进程存活 + 状态可用。"""
        if self._proc is None or self._proc.poll() is not None:
            return False
        return self.state in (READY, CALLING)

    # ---- 工具 ----

    def list_tools(self) -> list:
        """tools/list → [{name, description, inputSchema}]；未就绪返回 []。"""
        if self.state not in (READY, CALLING):
            return []
        ok, result = self._request("tools/list", {})
        if ok and isinstance(result, dict):
            self._tools = result.get("tools", []) or []
        return self._tools

    def call(self, tool: str, params: dict, timeout: float = 60.0) -> dict:
        """tools/call → {"ok": bool, "data": Any, "error": str|None}。
        流式/分段 content 缓冲为完整字符串，超限截断 + STREAM_TRUNCATED。"""
        if self.state not in (READY, CALLING):
            return {"ok": False, "data": None,
                    "error": f"插件未就绪（state={self.state}）"}
        ok, result = self._request("tools/call", {
            "name": tool, "arguments": params or {}}, timeout=timeout)
        if not ok:
            return {"ok": False, "data": None, "error": result}
        # content 归一化（缓冲流式，截断保护）
        try:
            content = result.get("content", []) or []
            parts = []
            total = 0
            truncated = False
            for item in content:
                text = str(item.get("text", "")) if isinstance(item, dict) else str(item)
                if total + len(text) > STREAM_BUFFER_MAX:
                    remain = STREAM_BUFFER_MAX - total
                    parts.append(text[:remain] if remain > 0 else "")
                    truncated = True
                    break
                parts.append(text)
                total += len(text)
            text = "".join(parts)
            if truncated:
                text += f"[{STREAM_TRUNCATED}]"
            return {"ok": not result.get("isError", False),
                    "data": text if text else result,
                    "error": None if not result.get("isError") else text[:500]}
        except Exception as exc:
            return {"ok": False, "data": None, "error": f"结果解析失败: {exc}"}

    # ---- 内部 ----

    def _request(self, method: str, params: dict, timeout: float = None) -> tuple:
        """同步请求 → (ok, result)。超时 kill 重建（幂等重试 1 次）。"""
        timeout = timeout or self.timeout
        for attempt in range(2):
            if self._proc is None or self._proc.poll() is not None:
                return False, f"进程已退出（attempt {attempt}）"
            rid = self._next_id()
            line = json.dumps({"jsonrpc": "2.0", "id": rid,
                               "method": method, "params": params}) + "\n"
            try:
                with self._write_lock:
                    self._proc.stdin.write(line.encode("utf-8"))
                    self._proc.stdin.flush()
            except Exception as exc:
                return False, f"写入失败: {exc}"
            try:
                resp_id, resp_line = self._responses.get(timeout=timeout)
            except queue.Empty:
                # 超时：kill 重建（幂等）
                self.log(f"[plugin:{self.name}] {method} 超时，重建进程")
                self.close()
                if attempt == 0 and self.start():
                    continue
                return False, f"{method} 超时（{timeout}s）"
            if resp_id == rid:
                return self._parse_response(resp_line)
            return False, f"响应 id 不匹配: {resp_id} != {rid}"
        return False, f"{method} 重试失败"

    def _parse_response(self, line: str) -> tuple:
        try:
            msg = json.loads(line)
        except Exception:
            return False, "非法 JSON 响应"
        if "result" in msg:
            return True, msg["result"]
        err = msg.get("error") or {}
        return False, err.get("message", "未知错误")

    def _send_notify(self, method: str):
        line = json.dumps({"jsonrpc": "2.0", "method": method, "params": {}}) + "\n"
        with self._write_lock:
            self._proc.stdin.write(line.encode("utf-8"))
            self._proc.stdin.flush()

    def _next_id(self) -> int:
        self._id_counter += 1
        return self._id_counter

    def _read_loop(self):
        """后台读行：响应 → 队列；通知/非法行跳过。"""
        try:
            while True:
                raw = self._proc.stdout.readline()
                if not raw:
                    break  # EOF
                line = raw.decode("utf-8", "replace").strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except Exception:
                    continue  # 非法 JSON 行跳过
                if isinstance(msg, dict) and "id" in msg:
                    self._responses.put((msg["id"], line))
                # 通知（无 id）忽略
        except Exception:
            pass
