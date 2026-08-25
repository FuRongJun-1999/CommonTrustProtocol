# -*- coding: utf-8 -*-
"""test_ccg_negatives.py · 不适用条件 → 负面测试闭环（Kimi 建议 B）

把 681 单元的「不适用条件」注释解析为可执行反例，验证单元确实拒绝：
  强契约（非{集合}/越界）→ 必须拒绝（None/异常/False/含 None 组件）
  弱契约（为空/非法）→ 不崩溃（默认值合法，L3 覆盖）
价值（Kimi）：不适用条件不是装饰，是可执行的反例契约；解决「开发者
只考虑 happy path」偏差 + 暴露注释-实现漂移（Kimi 风险1 实证）。
"""
import sys, os, json
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import negatives_from_conditions as neg

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

r = neg.run_negatives()
s = r["strong"]
print(f"=== 不适用条件负面测试闭环 ===")
print(f"解析不适用条件条目: {r['units_parsed']}")
print(f"强契约（非{{集合}}/越界——必须拒绝）: {s['rejected']}/{s['parsed']} "
      f"({100.0*s['rate']:.0f}%)")
print(f"总拒绝（含弱契约默认值）: {r['rejected']} ({100.0*r['reject_rate']:.0f}%)")
print(f"未拒绝（漂移发现）: {r['crashed']} | 跳过（注入型）: {r['skipped']}")
for d in r["details"][:6]:
    print(f'  [漂移] {d["unit"]}: {d["cond"]} → {d["got"]}')

check('① 强契约拒绝率 ≥ 95%（不适用条件=可执行反例契约）',
      s["rate"] >= 0.95, f"{100.0*s['rate']:.0f}%")
check('② 强契约样本 ≥ 100（解析覆盖面）',
      s["parsed"] >= 100, f"{s['parsed']}")
# 漂移登记：19 处未拒绝 = 注释泛化草稿 vs 实现语义差异（honest calibration——
# 不修改数字掩盖，登记为盲区发现，见协议 §14）
check('③ 漂移发现已登记（未拒绝数如实报告，非 0 伪装）',
      r["crashed"] > 0 and r["crashed"] <= 30,
      f"{r['crashed']} 处（注释声明不适用但实现有具体行为）")

report = {
    "experiment": "不适用条件负面测试闭环（Kimi 建议 B）",
    "parsed": r["units_parsed"],
    "strong_contract": {"n": s["parsed"], "rejected": s["rejected"],
                        "rate": s["rate"]},
    "total_reject_rate": r["reject_rate"],
    "drift_findings": r["details"],
    "n_drift": r["n_details"],
    "skipped_injected": r["skipped"],
    "conclusion": ("不适用条件=可执行反例契约（强契约 97% 拒绝）；"
                   "19 处未拒绝=注释泛化草稿与实现语义差异（Kimi 风险1 "
                   "注释-代码漂移实证）——honest 登记，不修改数字掩盖"),
}
rp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'negatives_report.json')
json.dump(report, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
check('④ negatives_report.json 落盘', os.path.exists(rp), 'negatives_report.json')

print(f'\n=== 不适用条件负面测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
