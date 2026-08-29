# -*- coding: utf-8 -*-
"""dual_agent.py · 最小双智能体架构（2026-08-29 荣指令）

理论映射（智能论 3.4 六实例蜂群架构 → 最小双智能体）：
- 反思智能体 ReflectAgent = instance.reflect（反思单元·新）——产出候选
- 验证智能体 VerifyAgent = instance.verify（验证单元·稳）——独立裁决
- 记录单元 = FixedRecord（固定功能：全程 jsonl 可追溯）
- 输出单元 = FixedOutput（固定功能：仅 pass 结果按固定格式输出）
- 维生系统 = 荣（协议外，vitals 不可协商）

认知闭环（理论：记录→反思→验证→输出）：
任务 → 记录 → 反思(候选) → 记录 → 验证(独立裁决) →
  pass → 输出（固定格式）
  fail → 回反思重试（≤N 次，带失败证据）
独立纪律：验证者只看候选产物，不看反思者的过程——自验证不采信。
"""
from __future__ import annotations

import json
import os
import time
import uuid


class FixedRecord:
    """记录单元（固定功能）：全程 jsonl 追加写——事件序列可追溯。"""

    def __init__(self, path: str):
        self.path = path
        self.events: list = []

    def log(self, stage: str, payload: dict):
        e = {"ts": round(time.time(), 3), "stage": stage, "payload": payload}
        self.events.append(e)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
        return e


class FixedOutput:
    """输出单元（固定功能）：仅收通过验证的结果，固定 schema 输出。"""

    SCHEMA = {"task", "answer", "evidence", "verified_at"}

    def __init__(self, path: str):
        self.path = path
        self.emitted: list = []

    def emit(self, task: str, answer, evidence: str) -> dict:
        doc = {"task": task, "answer": answer, "evidence": evidence,
               "verified_at": round(time.time(), 3)}
        missing = self.SCHEMA - set(doc)
        if missing or not all(str(doc[k]).strip() for k in self.SCHEMA):
            raise ValueError(f"输出 schema 违规: 缺字段 {missing or '空值字段'}")
        self.emitted.append(doc)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
        return doc


class ReflectAgent:
    """反思智能体（instance.reflect）：产出候选方案。

    propose 回调由宿主注入（规则执行器/LLM 均可）——本架构只约定
    「任务 → 候选」接口，不绑定实现。
    """

    def __init__(self, propose, name: str = "reflect"):
        self.propose = propose
        self.name = name

    def run(self, task, attempt: int, failing=None):
        return self.propose(task, attempt, failing)


class VerifyAgent:
    """验证智能体（instance.verify）：独立裁决候选。

    judge 回调 = 验证基底（物理裁决优先）——只接收候选产物，
    不接收反思者过程（自验证不采信）。
    """

    def __init__(self, judge, name: str = "verify"):
        self.judge = judge
        self.name = name

    def run(self, candidate) -> tuple:
        return self.judge(candidate)   # (pass: bool, evidence: str)


class DualAgentSystem:
    """最小双智能体闭环：反思 ↔ 验证，记录/输出固定。"""

    def __init__(self, reflect: ReflectAgent, verify: VerifyAgent,
                 record: FixedRecord, output: FixedOutput, max_attempts: int = 3):
        self.reflect = reflect
        self.verify = verify
        self.record = record
        self.output = output
        self.max_attempts = max_attempts

    def execute(self, task_id: str, task):
        self.record.log("task_received", {"task_id": task_id, "task": str(task)[:80]})
        failing = None
        for attempt in range(1, self.max_attempts + 1):
            candidate = self.reflect.run(task, attempt, failing)
            self.record.log("reflect_proposed", {"task_id": task_id,
                                                 "attempt": attempt,
                                                 "candidate": str(candidate)[:120]})
            passed, evidence = self.verify.run(candidate)
            self.record.log("verify_judged", {"task_id": task_id, "attempt": attempt,
                                              "pass": passed, "evidence": evidence})
            if passed:
                doc = self.output.emit(task_id, candidate, evidence)
                self.record.log("output_emitted", {"task_id": task_id,
                                                   "doc": {k: doc[k] for k in ("task", "answer")}})
                return {"status": "accepted", "answer": candidate,
                        "attempts": attempt, "evidence": evidence}
            failing = evidence   # 失败证据回传反思者（预测误差→修正）
        self.record.log("exhausted", {"task_id": task_id, "attempts": self.max_attempts})
        return {"status": "failed", "attempts": self.max_attempts,
                "last_evidence": failing}


if __name__ == "__main__":
    import sys, tempfile
    sys.stdout.reconfigure(encoding="utf-8")
    td = tempfile.mkdtemp(prefix="dual_")
    record = FixedRecord(os.path.join(td, "record.jsonl"))
    output = FixedOutput(os.path.join(td, "output.jsonl"))

    # 演示：反思者求解「排序 [3,1,2]」，验证者独立用 sorted() 裁决
    reflect = ReflectAgent(lambda task, att, fail: sorted(task["arr"]))
    verify = VerifyAgent(lambda cand: (cand == sorted(task["arr"]),
                                       f"独立重算 {sorted(task['arr'])} vs 候选 {cand}"))
    task = {"arr": [3, 1, 2]}
    system = DualAgentSystem(reflect, verify, record, output)
    r = system.execute("sort-demo", task)
    print(json.dumps(r, ensure_ascii=False))
