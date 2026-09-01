#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
body.devices.process · 进程设备（BODY-REV1）
==============================================
动作：
- run: 执行命令（list 形式参数，禁 shell；超时终止；输出截断）
- check: 可用性探测

安全边界：
- 命令以参数列表传（不经过 shell，防注入）
- 默认工作目录限制在工作区内
- 超时强制终止 + 输出截断（默认 10KB）
输出为 DeviceResult：进程输出是数据（provenance=device:process）。
"""

import subprocess
import time
from typing import Dict, List, Optional, Union

from ..base import BodyDevice, DeviceResult

DEFAULT_TIMEOUT = 15.0   # 秒
OUTPUT_MAX = 10_000      # 输出截断（字符）
COMMAND_MAX_ARGS = 32


class ProcessDevice(BodyDevice):
    """进程执行设备（行动模态，工作区受限）。"""

    name = "process"
    modality = "action"
    description = "进程执行（list 参数禁 shell，超时终止，输出截断，工作区限制）"

    def check(self) -> Dict:
        return {"available": True, "detail": "subprocess 可用"}

    def invoke(self, action: str, params: Optional[Dict] = None) -> DeviceResult:
        p = params or {}
        if action == "run":
            return self._run(p)
        if action == "list":
            return self._list(p)
        return self._fail(f"未知动作 {action}（可用: run/list）")

    # ---- 动作 ----

    def _run(self, p: Dict) -> DeviceResult:
        command = p.get("command")
        if isinstance(command, str):
            # 禁 shell：字符串命令（含重定向/管道/内建）一律拒绝
            return self._fail("command 必须是参数列表（禁 shell 字符串，防注入）")
        if not isinstance(command, list) or not command:
            return self._fail("command 必须是非空列表（禁 shell 字符串）")
        if len(command) > COMMAND_MAX_ARGS:
            return self._fail(f"命令参数过多（上限 {COMMAND_MAX_ARGS}）")
        timeout = float(p.get("timeout", DEFAULT_TIMEOUT))
        timeout = max(0.5, min(timeout, 120.0))

        # 工作区限制（cwd 必须在工作区内）
        cwd = p.get("cwd") or self.workspace or None
        if cwd:
            ws = self.workspace
            cwd_abs = str(cwd)
            if ws:
                ws_abs = ws
                if not (cwd_abs == ws_abs or cwd_abs.startswith(ws_abs + chr(92))
                        or cwd_abs.startswith(ws_abs + "/")):
                    return self._fail(f"cwd 越出工作区: {cwd}")

        started = time.time()
        try:
            proc = subprocess.run(
                command,
                capture_output=True,
                timeout=timeout,
                cwd=cwd,
                shell=False,  # 禁 shell：参数不走解释器
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except subprocess.TimeoutExpired:
            return self._fail(f"命令超时（{timeout}s）已终止: {command[0]}")
        except FileNotFoundError:
            return self._fail(f"命令不存在: {command[0]}")
        except OSError as exc:
            return self._fail(f"执行失败: {exc}")

        elapsed = round(time.time() - started, 2)
        stdout = proc.stdout[:OUTPUT_MAX] if proc.stdout else ""
        stderr = proc.stderr[:OUTPUT_MAX] if proc.stderr else ""
        data = {
            "command": command,
            "exit_code": proc.returncode,
            "elapsed_s": elapsed,
            "stdout": stdout,
            "stderr": stderr,
            "stdout_truncated": bool(proc.stdout and len(proc.stdout) > OUTPUT_MAX),
            "cwd": cwd or ".",
        }
        summary = f"命令退出码 {proc.returncode}（{elapsed}s）: {' '.join(command)[:80]}"
        return self._r(data, "run", text_summary=summary)

    def _list(self, p: Dict) -> DeviceResult:
        """列出进程（零依赖：Windows tasklist / POSIX ps）。"""
        try:
            if self._is_windows():
                proc = subprocess.run(
                    ["tasklist", "/FO", "CSV", "/NH"],
                    capture_output=True, timeout=10, text=True, encoding="utf-8", errors="replace",
                )
                rows = []
                for line in proc.stdout.splitlines()[:100]:
                    parts = [x.strip('"') for x in line.split('","')]
                    if len(parts) >= 2:
                        rows.append({"name": parts[0], "pid": parts[1]})
            else:
                proc = subprocess.run(
                    ["ps", "-eo", "pid,comm"],
                    capture_output=True, timeout=10, text=True, encoding="utf-8", errors="replace",
                )
                rows = []
                for line in proc.stdout.splitlines()[1:100]:
                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        rows.append({"pid": parts[0], "name": parts[1]})
            summary = f"进程列表: {len(rows)} 项（截断显示）"
            return self._r({"processes": rows, "count": len(rows)}, "list", text_summary=summary)
        except Exception as exc:
            return self._fail(f"进程列表失败: {exc}")

    @staticmethod
    def _is_windows() -> bool:
        import sys

        return sys.platform == "win32"
