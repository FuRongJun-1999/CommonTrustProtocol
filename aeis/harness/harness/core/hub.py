# -*- coding: utf-8 -*-
"""harness.core.hub · MessageHub 消息总线（三路输入统一通道）
================================================
voice/terminal/web 三路输入 → input 队列 → 主循环 → 回复发布到 history。
- publish(role, content, reply_to=None)：追加历史 + 通知等待者
- wait_for_reply(input_id, timeout)：Web 同步等待该输入的回复
- recent(since_ts)：增量轮询（Web /api/poll）
- send(text)：投递输入（任意线程）
"""
import queue
import threading
import time
import uuid


class MessageHub:
    """线程安全消息总线。"""

    def __init__(self, max_history: int = 200):
        self.max_history = max_history
        self._history = []            # [{role, content, ts, input_id}]
        self._pending = {}            # input_id → 是否已回复
        self._lock = threading.Lock()
        self._cv = threading.Condition(self._lock)
        self.input_queue = queue.Queue()  # 输入投递（voice/terminal/web）

    # ---- 输入侧 ----

    def send(self, text: str, source: str = "web") -> str:
        """投递输入（异步处理），返回 input_id。"""
        input_id = f"in_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"
        with self._lock:
            self._pending[input_id] = False
        self.input_queue.put({"text": text, "source": source,
                              "input_id": input_id})
        return input_id

    def publish(self, role: str, content: str, reply_to: str = None,
                source: str = None):
        """发布消息到历史（role: user/assistant/system）。"""
        with self._cv:
            msg = {"role": role, "content": content,
                   "ts": time.time(), "input_id": reply_to,
                   "source": source}
            self._history.append(msg)
            if len(self._history) > self.max_history:
                self._history = self._history[-self.max_history:]
            if reply_to and reply_to in self._pending:
                self._pending[reply_to] = True
            self._cv.notify_all()

    # ---- 等待侧 ----

    def wait_for_reply(self, input_id: str, timeout: float = 60.0) -> dict:
        """阻塞等待该输入的回复消息。超时返回 None。"""
        deadline = time.time() + timeout
        with self._cv:
            while time.time() < deadline:
                # 找该 input_id 对应的 assistant 回复
                for m in reversed(self._history):
                    if m.get("input_id") == input_id and m["role"] == "assistant":
                        return m
                if self._pending.get(input_id) is False and \
                        not any(m.get("input_id") == input_id
                                for m in self._history):
                    pass
                # 等新消息或超时
                remain = deadline - time.time()
                if remain <= 0:
                    break
                self._cv.wait(timeout=min(remain, 1.0))
            return None

    # ---- 查询侧 ----

    def recent(self, since_ts: float = 0.0, limit: int = 100) -> list:
        """since_ts 之后的消息（Web /api/poll）。"""
        with self._lock:
            return [m for m in self._history
                    if m["ts"] > since_ts][-limit:]

    def history(self, limit: int = 100) -> list:
        with self._lock:
            return self._history[-limit:]

    def mark_reply_failed(self, input_id: str, error: str):
        """输入处理失败时发布失败回复（避免等待者永远阻塞）。"""
        self.publish("assistant", f"处理失败：{error}", reply_to=input_id,
                     source="system")
