# -*- coding: utf-8 -*-
"""harness.agents.supervisor · 编排器（任务派发/结果聚合/记忆沉淀）
================================================
- 线程池（concurrent.futures，零依赖），并发上限 pool_size（默认 3）
- submit 异步入队 / dispatch 同步执行
- 结果沉淀（决议 Q6）：任务完成后统一写主记忆 task_report 节点
  （标签 subagent:{role}+task_id，importance 0.5–0.9 按步数比）
- 事件兼容（决议 Q4）：事件格式 event_type/source/payload（未来桥接蜂群）
"""
import concurrent.futures
import threading
import time


class Supervisor:
    """子智能体编排器。"""

    def __init__(self, main_agent=None, pool_size: int = 3, log=None):
        self.main_agent = main_agent
        self.log = log or (lambda *a: None)
        self.pool_size = max(1, pool_size)
        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.pool_size)
        self._tasks = {}           # task_id → AgentTask
        self._lock = threading.Lock()
        self._events = []          # 事件流（event_type/source/payload）

    # ---- 任务提交 ----

    def submit(self, task, env: dict = None) -> str:
        """异步派发 → 返回 task_id。"""
        from harness.agents.child import ChildAgent
        with self._lock:
            self._tasks[task.task_id] = task
        child = ChildAgent(identity=task.agent_role, db_path=task.db_path,
                           log=self.log)
        fut = self._executor.submit(child.run, task, env)
        fut.add_done_callback(lambda f: self._on_done(task, child, f))
        self._emit("task.submitted", task.agent_role,
                   {"task_id": task.task_id, "prompt": task.prompt[:60]})
        return task.task_id

    def dispatch(self, task, env: dict = None, timeout: float = None) -> object:
        """同步执行（阻塞直到完成/超时）。超时 → task.status=timed_out。"""
        tid = self.submit(task, env)
        deadline = timeout or task.timeout
        t0 = time.time()
        while time.time() - t0 < deadline:
            with self._lock:
                t = self._tasks.get(tid)
            if t is not None and t.status not in ("pending", "running"):
                return t
            time.sleep(0.1)
        with self._lock:
            t = self._tasks.get(tid)
        if t is not None:
            t.status = "timed_out"
            t.error = f"总超时（{deadline}s）"
            t.finished_at = time.time()
        return t

    # ---- 查询 ----

    def status(self, task_id: str):
        """查询任务状态（task_id → 状态/进度信息）。"""
        with self._lock:
            return self._tasks.get(task_id)

    def results(self, since: float = 0.0) -> list:
        """取指定时间戳之后的结果列表。"""
        with self._lock:
            return [t for t in self._tasks.values()
                    if t.finished_at and t.finished_at >= since]

    # ---- 聚合与沉淀（决议 Q6） ----

    def aggregate(self, task_ids: list = None) -> dict:
        """聚合多个子任务结果 → 结构化摘要；统一写入主记忆 task_report。"""
        with self._lock:
            items = list(self._tasks.values())
        if task_ids:
            items = [t for t in items if t.task_id in task_ids]
        summary = []
        for t in items:
            entry = {"task_id": t.task_id, "role": t.agent_role,
                     "status": t.status, "title": t.title,
                     "result": (t.result or "")[:200],
                     "error": t.error}
            summary.append(entry)
            # 记忆沉淀：task_report 节点
            if self.main_agent is not None and t.status == "succeeded":
                try:
                    ratio = min(0.9, 0.5 + 0.4 * min(1.0, t.steps_used / max(1, t.max_steps)))
                    self.main_agent.remember(
                        f"[任务报告:{t.title}] {str(t.result)[:200]}",
                        importance=round(ratio, 2),
                        tags=["task_report", f"subagent:{t.agent_role}",
                              f"task_id:{t.task_id}"])
                except Exception:
                    pass
        self._emit("task.aggregated", "supervisor", {"count": len(summary)})
        return {"count": len(summary), "tasks": summary}

    # ---- 事件（决议 Q4：兼容蜂群 schema） ----

    def _emit(self, event_type: str, source: str, payload: dict):
        self._events.append({"event_type": event_type, "source": source,
                             "payload": payload, "ts": time.time()})
        if len(self._events) > 100:
            self._events = self._events[-50:]

    def events(self, limit: int = 20) -> list:
        """取最近事件流（默认 20 条）。"""
        return self._events[-limit:]

    # ---- 生命周期 ----

    def shutdown(self):
        """关闭执行器（不等待、取消未开始任务）。"""
        self._executor.shutdown(wait=False, cancel_futures=True)

    def _on_done(self, task, child, fut):
        try:
            fut.result(timeout=1)
        except Exception as exc:
            with self._lock:
                t = self._tasks.get(task.task_id)
                if t is not None and t.status == "running":
                    t.status = "failed"
                    t.error = str(exc)[:200]
                    t.finished_at = time.time()
        try:
            child.close()
        except Exception:
            pass
        self._emit("task.done", task.agent_role,
                   {"task_id": task.task_id, "status": task.status})
