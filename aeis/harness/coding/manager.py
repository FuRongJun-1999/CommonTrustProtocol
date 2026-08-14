# -*- coding: utf-8 -*-
"""harness.coding.manager · 编码任务管理器（异步执行 + 状态查询）
================================================
任务注册表：提交 → 线程执行 → 状态/步骤/回滚/日志查询。
"""
import threading
import time
import uuid

from harness.coding.loop import CodingLoop
from harness.coding.workspace import Workspace


class CodingManager:
    """编码任务管理器（单实例）。"""

    def __init__(self, env: dict = None, log=None):
        self.env = env or {}
        self.log = log or (lambda *a: None)
        self._tasks = {}          # task_id → dict
        self._lock = threading.Lock()
        self._default_ws = None

    def set_default_workspace(self, root: str):
        self._default_ws = root

    def submit(self, task: str, workspace_root: str = None) -> dict:
        """提交编码任务 → 异步执行 → 返回 task_id。"""
        root = workspace_root or self._default_ws
        if not root:
            return {"ok": False, "error": "未设置工作区"}
        task_id = f"code_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"
        ws = Workspace(root)
        loop = CodingLoop(ws, env=self.env, log=self.log)
        entry = {"task_id": task_id, "task": task, "workspace": root,
                 "status": "running", "created_at": time.time(),
                 "finished_at": None, "result": None,
                 "snapshots": ws.list_snapshots(3)}
        with self._lock:
            self._tasks[task_id] = entry

        def _worker():
            try:
                result = loop.run(task)
                entry["result"] = result
                entry["status"] = result.get("status", "done")
            except Exception as exc:
                entry["status"] = "error"
                entry["result"] = {"status": "error", "summary": str(exc)}
            finally:
                entry["finished_at"] = time.time()
                entry["snapshots"] = ws.list_snapshots(5)
                self.log(f"[coding] {task_id} {entry['status']}")

        threading.Thread(target=_worker, daemon=True).start()
        return {"ok": True, "task_id": task_id, "status": "running"}

    def get(self, task_id: str) -> dict:
        with self._lock:
            return self._tasks.get(task_id)

    def list_tasks(self, limit: int = 10) -> list:
        with self._lock:
            items = sorted(self._tasks.values(),
                           key=lambda t: t.get("created_at", 0), reverse=True)
            return [{"task_id": t["task_id"], "task": t["task"][:60],
                     "status": t["status"],
                     "created_at": t["created_at"]} for t in items[:limit]]

    def revert(self, task_id: str, snapshot_id: str = None) -> dict:
        """回滚任务的工作区到快照（能恢复）。"""
        entry = self.get(task_id)
        if entry is None:
            return {"ok": False, "error": f"任务不存在: {task_id}"}
        ws = Workspace(entry["workspace"])
        if snapshot_id:
            return ws.revert(snapshot_id)
        snaps = ws.list_snapshots(1)
        if not snaps:
            return {"ok": False, "error": "无快照"}
        r = ws.revert(snaps[0]["id"])
        if r["ok"]:
            self.log(f"[coding] {task_id} 已回滚 {r['snapshot']}（{r['restored']} 文件）")
        return r
