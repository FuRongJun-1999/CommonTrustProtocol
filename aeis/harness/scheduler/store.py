# -*- coding: utf-8 -*-
"""harness.scheduler.store · 自动化存储
================================================
data/automations.db：
- automations:      id/title/schedule(JSON)/prompt/enabled/next_run_at/
                    run_count/last_run_at/created_at/updated_at
- automation_runs:  run_id/automation_id/trigger/started_at/outcome/error

语义对齐 ZCode：next_run_at 到期 → 认领执行 → 更新 next_run_at/run_count
→ 写 run 记录。零依赖 sqlite3。
"""
import json
import os
import sqlite3
import time

DEFAULT_DB = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "automations.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS automations (
    id TEXT PRIMARY KEY,
    title TEXT,
    schedule TEXT,            -- JSON: {"type":"interval","minutes":30} | {"type":"daily","hour":1,"minute":0} | {"type":"cron","expr":"*/30 * * * *"}
    prompt TEXT,              -- 任务描述（task 注册名或描述）
    task TEXT,                -- 任务名（engine 注册表键）
    enabled INTEGER DEFAULT 1,
    next_run_at REAL,
    run_count INTEGER DEFAULT 0,
    last_run_at REAL,
    created_at REAL,
    updated_at REAL
);
CREATE TABLE IF NOT EXISTS automation_runs (
    run_id TEXT PRIMARY KEY,
    automation_id TEXT,
    trigger TEXT,
    started_at REAL,
    outcome TEXT,             -- succeeded | failed
    error TEXT,
    detail TEXT
);
"""


class AutomationStore:
    """自动化存储（零依赖）。"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DEFAULT_DB
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def _row(self, r):
        return None if r is None else dict(zip([d[0] for d in self._conn.execute(
            "SELECT * FROM automations LIMIT 0").description], r))

    def add(self, auto_id: str, title: str, schedule: dict, task: str,
            prompt: str = "", enabled: int = 1, next_run_at: float = None) -> None:
        now = time.time()
        self._conn.execute(
            "INSERT OR REPLACE INTO automations "
            "(id, title, schedule, prompt, task, enabled, next_run_at, "
            "run_count, last_run_at, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?,?,0,NULL,?,?)",
            (auto_id, title, json.dumps(schedule, ensure_ascii=False), prompt,
             task, enabled, next_run_at if next_run_at is not None else now,
             now, now))
        self._conn.commit()

    def list_due(self, now: float = None) -> list:
        """到期任务：enabled=1 且 next_run_at <= now。"""
        now = now if now is not None else time.time()
        rows = self._conn.execute(
            "SELECT * FROM automations WHERE enabled=1 AND next_run_at IS NOT NULL "
            "AND next_run_at <= ? ORDER BY next_run_at", (now,)).fetchall()
        return [self._row(r) for r in rows]

    def list_all(self) -> list:
        rows = self._conn.execute("SELECT * FROM automations ORDER BY created_at").fetchall()
        return [self._row(r) for r in rows]

    def get(self, auto_id: str) -> dict:
        r = self._conn.execute("SELECT * FROM automations WHERE id=?", (auto_id,)).fetchone()
        return self._row(r)

    def mark_run(self, auto_id: str, next_run_at: float, outcome: str = "succeeded",
                 error: str = "", detail: str = "") -> str:
        """执行后记录：更新 next_run_at/run_count + 写 run 记录。"""
        now = time.time()
        run_id = f"{auto_id}:{int(now*1000)}"
        self._conn.execute(
            "UPDATE automations SET next_run_at=?, run_count=run_count+1, "
            "last_run_at=?, updated_at=? WHERE id=?",
            (next_run_at, now, now, auto_id))
        self._conn.execute(
            "INSERT INTO automation_runs (run_id, automation_id, trigger, "
            "started_at, outcome, error, detail) VALUES (?,?,?,?,?,?,?)",
            (run_id, auto_id, "schedule", now, outcome, error or None, detail or None))
        self._conn.commit()
        return run_id

    def set_enabled(self, auto_id: str, enabled: int) -> None:
        self._conn.execute("UPDATE automations SET enabled=?, updated_at=? WHERE id=?",
                           (enabled, time.time(), auto_id))
        self._conn.commit()

    def update_schedule(self, auto_id: str, schedule: dict, title: str = None) -> None:
        """更新调度计划（互维 v1.1 迁移：心跳 30min → 10min）。"""
        if title is not None:
            self._conn.execute(
                "UPDATE automations SET schedule=?, title=?, updated_at=? WHERE id=?",
                (json.dumps(schedule, ensure_ascii=False), title, time.time(), auto_id))
        else:
            self._conn.execute("UPDATE automations SET schedule=?, updated_at=? WHERE id=?",
                               (json.dumps(schedule, ensure_ascii=False), time.time(), auto_id))
        self._conn.commit()

    def delete(self, auto_id: str) -> None:
        self._conn.execute("DELETE FROM automations WHERE id=?", (auto_id,))
        self._conn.commit()

    def recent_runs(self, limit: int = 10) -> list:
        rows = self._conn.execute(
            "SELECT * FROM automation_runs ORDER BY started_at DESC LIMIT ?",
            (limit,)).fetchall()
        cols = [d[0] for d in self._conn.execute("SELECT * FROM automation_runs LIMIT 0").description]
        return [dict(zip(cols, r)) for r in rows]

    def running_tasks(self) -> int:
        """执行中的任务数（outcome='running' 的记录数）。
        互维协议 v1.1：心跳戳 task_running 字段——任务执行中戳不更新 ≠ 失联。"""
        try:
            return self._conn.execute(
                "SELECT COUNT(*) FROM automation_runs WHERE outcome='running'"
            ).fetchone()[0]
        except Exception:
            return 0

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass
