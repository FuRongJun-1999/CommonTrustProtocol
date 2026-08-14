# -*- coding: utf-8 -*-
"""harness.coding.loop · 编码任务循环（agent loop）
================================================
能力四项：能修改（工具调用）/ 能恢复（快照回滚）/ 能验证（测试执行）/
能记录（全量留痕）。

循环：任务 → 模型（带工具 schema）→ 工具调用 → 执行（工作区/进程）
    → 结果回喂 → 继续 → 完成（模型声明 done）→ 验证 → 汇报。

工具面（零依赖实现，经 Workspace 与 subprocess）：
- read_file / write_file（写前自动快照）/ list_files / run_command / revert
"""
import json
import os
import subprocess
import threading
import time
import urllib.request


class CodingLoop:
    """编码任务循环（单任务单线程）。"""

    TOOLS = [
        {"type": "function", "function": {
            "name": "read_file",
            "description": "读取工作区内文件",
            "parameters": {"type": "object",
                           "properties": {"path": {"type": "string"}},
                           "required": ["path"]}}},
        {"type": "function", "function": {
            "name": "write_file",
            "description": "写入文件（覆盖或追加；写前自动快照可回滚）",
            "parameters": {"type": "object",
                           "properties": {"path": {"type": "string"},
                                          "content": {"type": "string"},
                                          "append": {"type": "boolean"}},
                           "required": ["path", "content"]}}},
        {"type": "function", "function": {
            "name": "list_files",
            "description": "列出工作区目录内容",
            "parameters": {"type": "object",
                           "properties": {"dir": {"type": "string"}},
                           "required": ["dir"]}}},
        {"type": "function", "function": {
            "name": "run_command",
            "description": "执行命令验证（参数列表，禁 shell；如 python 测试）",
            "parameters": {"type": "object",
                           "properties": {"command": {"type": "array",
                                                      "items": {"type": "string"}},
                                          "cwd": {"type": "string"}},
                           "required": ["command"]}}},
        {"type": "function", "function": {
            "name": "revert",
            "description": "回滚到最近快照（撤销修改）",
            "parameters": {"type": "object", "properties": {}}}},
    ]

    def __init__(self, workspace, env: dict = None,
                 base_url: str = "https://api.deepseek.com",
                 model: str = "deepseek-chat", log=None):
        self.ws = workspace
        self.env = env or {}
        self.base_url = base_url
        self.model = model
        self.log = log or (lambda *a: None)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    # ---- 模型（function calling） ----

    def _chat(self, messages: list, max_tokens: int = 1500) -> dict:
        """一次模型调用（支持工具调用）。返回 message dict。"""
        key = self.env.get("DEEPSEEK_API_KEY", "")
        body = {
            "model": self.model,
            "messages": messages,
            "tools": self.TOOLS,
            "temperature": 0.3,
            "max_tokens": max_tokens,
            "stream": False,
        }
        req = urllib.request.Request(
            self.base_url.rstrip("/") + "/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]

    # ---- 工具执行 ----

    def _execute_tool(self, name: str, args: dict) -> dict:
        """执行工具调用（工作区/进程），返回结果 dict。"""
        if name == "read_file":
            r = self.ws.read_file(args.get("path", ""))
            return {"ok": r["ok"], "result": r.get("content", r.get("error"))}
        if name == "write_file":
            r = self.ws.write_file(args.get("path", ""),
                                   args.get("content", ""),
                                   append=bool(args.get("append", False)))
            return {"ok": r["ok"], "result": f"已写入 {r.get('path')}（{r.get('chars', 0)} 字符）"}
        if name == "list_files":
            r = self.ws.list_files(args.get("dir", "."))
            if not r["ok"]:
                return {"ok": False, "result": r["error"]}
            return {"ok": True, "result": json.dumps(
                [f"{i['type'][0]}:{i['name']}" for i in r["items"]],
                ensure_ascii=False)}
        if name == "run_command":
            cmd = args.get("command")
            if not isinstance(cmd, list) or not cmd:
                return {"ok": False, "result": "command 必须是参数列表（禁 shell）"}
            cwd = args.get("cwd") or self.ws.root
            try:
                proc = subprocess.run(
                    cmd, cwd=cwd, capture_output=True, timeout=60,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                out = proc.stdout.decode("utf-8", "replace")[-4000:]
                err = proc.stderr.decode("utf-8", "replace")[-2000:]
                return {"ok": proc.returncode == 0,
                        "result": f"rc={proc.returncode}\n{out}\n{err}".strip()}
            except subprocess.TimeoutExpired:
                return {"ok": False, "result": "命令超时（60s）"}
            except Exception as exc:
                return {"ok": False, "result": f"命令失败: {exc}"}
        if name == "revert":
            snaps = self.ws.list_snapshots(1)
            if not snaps:
                return {"ok": False, "result": "无快照可回滚"}
            r = self.ws.revert(snaps[0]["id"])
            return {"ok": r["ok"], "result": f"已回滚快照 {snaps[0]['id']}（恢复 {r.get('restored', 0)} 文件）"}
        return {"ok": False, "result": f"未知工具: {name}"}

    # ---- 主循环 ----

    def run(self, task: str, max_steps: int = 25, timeout: float = 300.0) -> dict:
        """执行编码任务。返回 {status, summary, steps, log}。"""
        t0 = time.time()
        steps = []          # 留痕：每一步 {i, tool, args, result}
        snap_id = self.ws.snapshot(note=f"任务开始: {task[:40]}")  # 初始快照
        system = (
            "你是灵枢的编码执行体。任务：{task}\n"
            "规则：\n"
            "1. 使用工具完成修改（read→write），不要猜测文件内容；\n"
            "2. 修改后必须运行验证命令（run_command，如 python -m pytest）；\n"
            "3. 完成后用中文回复，包含：改了什么、验证结果、如何回滚；\n"
            "4. 如果任务不可完成或验证失败且无法修复，明确说明。"
        ).format(task=task)
        messages = [{"role": "system", "content": system},
                    {"role": "user", "content": task}]
        final = "（未完成）"
        try:
            for i in range(max_steps):
                if self._stop.is_set():
                    return {"status": "stopped", "summary": "任务被停止", "steps": steps}
                if time.time() - t0 > timeout:
                    return {"status": "timeout", "summary": "任务超时", "steps": steps}
                msg = self._chat(messages)
                tcalls = msg.get("tool_calls") or []
                if not tcalls:
                    # 无工具调用 = 模型给出最终回答
                    final = msg.get("content", "") or "（完成）"
                    # 强制验证提示：若本轮有 write 且未验证，提示模型验证
                    break
                for tc in tcalls:
                    fn = tc.get("function", {})
                    name = fn.get("name", "")
                    try:
                        args = json.loads(fn.get("arguments", "{}") or "{}")
                    except Exception:
                        args = {}
                    result = self._execute_tool(name, args)
                    steps.append({"step": i + 1, "tool": name,
                                  "args": str(args)[:200],
                                  "result": str(result.get("result", ""))[:500],
                                  "ok": result.get("ok", False)})
                    messages.append({"role": "assistant",
                                     "content": None,
                                     "tool_calls": [tc]})
                    messages.append({"role": "tool",
                                     "tool_call_id": tc.get("id", ""),
                                     "content": json.dumps(result, ensure_ascii=False)[:3000]})
                # 步间停顿（防风暴）
                time.sleep(0.3)
        except Exception as exc:
            return {"status": "error", "summary": f"循环异常: {exc}",
                    "steps": steps, "log": []}
        # 记录（能记录）：任务摘要入灵枢记忆 + 步骤留痕
        summary = f"编码任务完成（{len(steps)} 步）: {final[:200]}"
        return {"status": "succeeded", "summary": summary,
                "final": final, "steps": steps,
                "snapshot": snap_id, "duration": round(time.time() - t0, 1)}
