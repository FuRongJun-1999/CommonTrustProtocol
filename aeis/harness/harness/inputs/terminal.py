# -*- coding: utf-8 -*-
"""harness.inputs.terminal · 终端输入（开发/调试通道）
================================================
标准输入循环，每行触发回调；exit/quit 可退出运行时。
"""
import threading


class TerminalInput(threading.Thread):
    """终端输入线程：每行 on_line(text)。"""

    def __init__(self, on_line, log=None):
        super().__init__(daemon=True)
        self.on_line = on_line
        self.log = log or (lambda *a: None)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def run(self):
        try:
            while not self._stop.is_set():
                line = input()
                if line:
                    self.on_line(line.strip())
        except EOFError:
            pass
        except Exception as exc:
            self.log(f"终端输入异常: {exc}")
