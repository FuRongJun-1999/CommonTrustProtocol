# -*- coding: utf-8 -*-
"""harness.scheduler.engine · 调度引擎（tick 循环）
================================================
每 tick：查到期任务 → 执行任务函数（注册表）→ 更新 next_run_at →
写 run 记录（succeeded/failed）。单线程串行执行，任务内异常不杀循环。
"""
import threading
import time


class SchedulerEngine(threading.Thread):
    """调度器线程：注册任务（task 名 → 函数(agent, store, 参数)），到期执行。"""

    def __init__(self, store, agent, tick_seconds: int = 15, log=None):
        super().__init__(daemon=True)
        self.store = store
        self.agent = agent
        self.tick_seconds = max(1, tick_seconds)
        self.log = log or (lambda *a: None)
        self._tasks = {}  # task 名 → fn(agent, ctx) -> (outcome, detail)
        self._stop = threading.Event()
        self._lock = threading.Lock()

    def register(self, task_name: str, fn):
        """注册任务：fn(agent, ctx) -> str（详情，异常时抛错=失败）。"""
        self._tasks[task_name] = fn

    def stop(self):
        self._stop.set()

    def trigger_now(self, auto_id: str) -> str:
        """手动触发一次任务（测试/运维）。返回 run_id。"""
        auto = self.store.get(auto_id)
        if not auto:
            return ""
        return self._execute(auto)

    def run(self):
        self.log(f"调度引擎启动（tick {self.tick_seconds}s，任务 {len(self._tasks)} 个）")
        while not self._stop.is_set():
            try:
                due = self.store.list_due()
                for auto in due:
                    if self._stop.is_set():
                        break
                    try:
                        self._execute(auto)
                    except Exception as exc:
                        self.log(f"任务执行异常 {auto['id']}: {exc}")
            except Exception as exc:
                self.log(f"调度 tick 异常: {exc}")
            self._stop.wait(self.tick_seconds)

    def _execute(self, auto: dict) -> str:
        from harness.scheduler.cron import next_run
        task_name = auto.get("task", "")
        fn = self._tasks.get(task_name)
        schedule = {}
        try:
            import json
            schedule = json.loads(auto.get("schedule") or "{}")
        except Exception:
            pass
        nxt = next_run(time.time(), schedule, auto.get("last_run_at"))
        if fn is None:
            self.store.mark_run(auto["id"], nxt, "failed", f"未知任务: {task_name}")
            return ""
        run_id = self.store.mark_run(auto["id"], nxt, "running")
        try:
            detail = fn(self.agent, {"store": self.store, "automation": auto})
            # 更新 outcome（running → succeeded）
            import sqlite3
            conn = sqlite3.connect(self.store.db_path)
            conn.execute("UPDATE automation_runs SET outcome=?, detail=? WHERE run_id=?",
                         ("succeeded", detail or "", run_id))
            conn.commit()
            conn.close()
            self.log(f"[调度] {auto['title']} 完成（run {run_id}）")
            return run_id
        except Exception as exc:
            import sqlite3
            conn = sqlite3.connect(self.store.db_path)
            conn.execute("UPDATE automation_runs SET outcome=?, error=? WHERE run_id=?",
                         ("failed", str(exc)[:300], run_id))
            conn.commit()
            conn.close()
            self.log(f"[调度] {auto['title']} 失败: {exc}")
            return run_id
