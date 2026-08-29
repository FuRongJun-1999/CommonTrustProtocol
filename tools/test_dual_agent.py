# -*- coding: utf-8 -*-
"""test_dual_agent.py · 最小双智能体验证（V-DA.1~6，2026-08-29）

理论映射（六实例蜂群架构→双智能体）：反思(instance.reflect) ↔ 验证
(instance.verify)，记录/输出=固定功能。
"""
import sys, os, shutil, tempfile, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dual_agent import (FixedRecord, FixedOutput, ReflectAgent,
                        VerifyAgent, DualAgentSystem)

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"[✔] {name}")
    else:
        fail_n += 1
        print(f"[✘] {name} {detail}")


tmp = tempfile.mkdtemp(prefix="dual_")
try:
    task = {"arr": [3, 1, 2]}
    truth = sorted(task["arr"])

    # ============ V-DA.1/2 反思产出 + 验证独立裁决 ============
    record = FixedRecord(os.path.join(tmp, "rec.jsonl"))
    output = FixedOutput(os.path.join(tmp, "out.jsonl"))
    reflect = ReflectAgent(lambda t, att, fail: sorted(t["arr"]))
    verify = VerifyAgent(lambda c: (c == truth, f"独立重算 {truth} vs 候选 {c}"))
    sys_ok = DualAgentSystem(reflect, verify, record, output)
    r = sys_ok.execute("sort-1", task)
    check("V-DA.1 反思产出候选", r["status"] == "accepted" and r["answer"] == [1, 2, 3], str(r))
    check("V-DA.2 验证独立裁决 pass", r["evidence"].startswith("独立重算"), r["evidence"][:40])

    # ============ V-DA.3 fail 重试（反思按失败证据修正） ============
    attempts_log = []
    def bad_then_good(t, att, fail):
        attempts_log.append(att)
        if att == 1:
            return [1, 2, 99]      # 首轮错误候选
        return truth               # 次轮修正
    record2 = FixedRecord(os.path.join(tmp, "rec2.jsonl"))
    output2 = FixedOutput(os.path.join(tmp, "out2.jsonl"))
    sys2 = DualAgentSystem(ReflectAgent(bad_then_good), verify, record2, output2)
    r2 = sys2.execute("sort-2", task)
    check("V-DA.3 fail 后重试成功", r2["status"] == "accepted" and r2["attempts"] == 2, str(r2))

    # ============ V-DA.4 记录完整性（全程事件可追溯） ============
    stages = [e["stage"] for e in record2.events]
    for s in ("task_received", "reflect_proposed", "verify_judged", "output_emitted"):
        check(f"V-DA.4 记录含 {s}", s in stages, f"stages={stages}")
    check("V-DA.4 失败事件留痕", "verify_judged" in stages and stages.count("verify_judged") >= 2)

    # ============ V-DA.5 输出固定 schema（仅 pass 进入输出） ============
    check("V-DA.5 输出 schema 固定", set(output2.emitted[0]) == FixedOutput.SCHEMA,
          str(set(output2.emitted[0])))
    try:
        output2.emit("t", "ans", "")   # evidence 空串 → schema 缺字段路径
        check("V-DA.5 schema 违规报错", False, "未抛异常")
    except ValueError as e:
        check("V-DA.5 schema 违规报错", "缺字段" in str(e), str(e))

    # ============ V-DA.6 独立纪律（验证者不看反思过程） ============
    seen_by_verify = []
    def spy_judge(c):
        seen_by_verify.append(c)
        return (c == truth, "spy")
    verify_spy = VerifyAgent(spy_judge)
    sys3 = DualAgentSystem(ReflectAgent(lambda t, a, f: truth), verify_spy,
                           FixedRecord(os.path.join(tmp, "r3.jsonl")),
                           FixedOutput(os.path.join(tmp, "o3.jsonl")))
    sys3.execute("sort-3", task)
    check("V-DA.6 验证者只接收候选产物", all(isinstance(x, list) for x in seen_by_verify),
          str(seen_by_verify)[:60])

    # ============ 穷尽失败诚实申报 ============
    record4 = FixedRecord(os.path.join(tmp, "r4.jsonl"))
    output4 = FixedOutput(os.path.join(tmp, "o4.jsonl"))
    sys4 = DualAgentSystem(ReflectAgent(lambda t, a, f: [99]), verify,
                           record4, output4, max_attempts=2)
    r4 = sys4.execute("impossible", task)
    check("穷尽失败诚实申报", r4["status"] == "failed" and r4["attempts"] == 2, str(r4))
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n=== 判定 ===")
print(f"最小双智能体验证: {pass_n}/{pass_n + fail_n}")
sys.exit(0 if fail_n == 0 else 1)
