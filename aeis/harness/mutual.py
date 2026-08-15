#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""harness.mutual · 互维邮箱客户端（沙箱 A 侧 · W3）
====================================================
互维协议 v1.1（docs/mutual-sustain-loop.md §3）：
- submit_verify()  提交 verify 任务（task-<id>.json → B 轮询）
- collect_results() 读取 B 侧写回的 result（result-<id>.json）
- handle_result()  按 verdict 处理：pass 采纳 / needs_revision 修订 / fail 挂起等荣终裁

与 guardian.py 共用互维目录常量与协议字段校验（TASK_FIELDS/RESULT_FIELDS）。
"""
import json
import os
import time
import uuid

from harness.guardian import (NET_DIR, TASK_FIELDS, RESULT_FIELDS,
                              validate_task, validate_result)

TASKS_DIR = os.path.join(NET_DIR, "tasks")


def _ensure_dirs():
    os.makedirs(TASKS_DIR, exist_ok=True)


def submit_verify(claim: str, evidence: str = "", expected: str = "",
                  source_ref: str = "", task_id: str = None) -> str:
    """提交 verify 任务（A→B）。返回 task id。
    协议 v1.1 §3.1：{id, type=verify, from=A, to=B, payload{claim,evidence,expected,source_ref},
    status=pending, created_at}。"""
    _ensure_dirs()
    tid = task_id or f"task-{int(time.time() * 1000)}"
    task = {
        "id": tid, "type": "verify", "from": "A", "to": "B",
        "payload": {"claim": claim, "evidence": evidence,
                    "expected": expected, "source_ref": source_ref},
        "status": "pending", "created_at": time.time(),
    }
    errs = validate_task(task)
    if errs:
        raise ValueError(f"任务格式非法: {errs}")
    fname = tid if tid.startswith("task-") else f"task-{tid}"
    path = os.path.join(TASKS_DIR, f"{fname}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    print(f"[互维] A→B verify 任务已提交: {tid}")
    return tid


def collect_results(verifier: str = "B") -> list:
    """读取验证方写回的 result 列表（按协议字段校验过滤）。"""
    _ensure_dirs()
    results = []
    if not os.path.isdir(TASKS_DIR):
        return results
    for fn in sorted(os.listdir(TASKS_DIR)):
        if not (fn.startswith("result-") and fn.endswith(".json")):
            continue
        try:
            with open(os.path.join(TASKS_DIR, fn), encoding="utf-8") as f:
                r = json.load(f)
            if not validate_result(r):
                if verifier is None or r.get("verifier") == verifier:
                    results.append(r)
        except Exception:
            continue
    return results


def handle_result(result: dict, log_path: str = None) -> str:
    """按 verdict 处理（协议 v1.1 §3.3）：
    pass → 采纳（adopted）；needs_revision → 修订（revision）；fail → 挂起等荣终裁（pending_designer）。
    返回处理动作；记录到互维日志。"""
    verdict = result.get("verdict", "")
    task_id = result.get("task_id", "?")
    action = {"pass": "adopted", "needs_revision": "revision",
              "fail": "pending_designer"}.get(verdict, "unknown")
    line = (f"[A {time.strftime('%Y-%m-%d %H:%M:%S')}] 任务 {task_id} 结果处理: "
            f"verdict={verdict} → {action}"
            f"（白箱: {result.get('whitebox', {}).get('judgment', '?')}"
            f" 复核: {result.get('llm_review', {}).get('conclusion', '?')}）")
    print(line)
    if log_path is None:
        log_path = os.path.join(NET_DIR, "mutual.log")
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass
    return action


def poll_and_handle() -> list:
    """轮询所有 B 侧 result 并处理。返回处理动作列表。"""
    return [handle_result(r) for r in collect_results()]


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--poll":
        actions = poll_and_handle()
        print(f"处理完成: {actions}")
    elif len(sys.argv) > 2 and sys.argv[1] == "--submit":
        tid = submit_verify(sys.argv[2])
        print(f"已提交: {tid}")
    else:
        print("用法: python -m harness.mutual --poll | --submit '<claim>'")
