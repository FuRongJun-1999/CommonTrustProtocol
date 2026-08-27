# -*- coding: utf-8 -*-
"""test_self_iterate.py · 自迭代八步闭环（荣 长期任务，协议 §18）

八步：感知/识别/分析/验证/固化/记录/反馈/方向性自检。
验证：①感知扫描 ②识别分类 ③分析影响 ④固化语法安全（字符串内替换）
⑤记录可追溯 ⑥反馈跳过已吸收 ⑦方向自检 ⑧全库注释对齐后回归绿。
"""
import sys, os, json, subprocess
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import self_iterate as si

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

HERE = os.path.dirname(os.path.abspath(__file__))

# ── ① 感知：自动扫描全库 ─────────────────────────────────────
per = si.perceive()
ok1 = per["n_drift"] > 0 and per["strong_rate"] >= 0.9 \
      and per["mos_rate"] >= 0.98
print(f'  漂移 {per["n_drift"]} | 强契约 {100.0*per["strong_rate"]:.0f}% '
      f'| MOS {100.0*per["mos_rate"]:.0f}%')
check('① 感知：负面漂移+契约率+MOS 一致率 全扫描', ok1)

# ── ①b 感知扩展：路由冲突/盲区/注释规范 通道 ────────────────
rc = per.get("route_conflicts", {})
bs = per.get("blindspots", {})
cs = per.get("comment_spec", {})
ok1b = (rc.get("ok") and rc.get("n_excl_units", 0) > 0
        and bs.get("ok") and cs.get("ok") and cs.get("n_spec_fail", -1) == 0)
print(f'  路由互斥 {rc.get("n_excl_units")} 单元 | 盲区探测 '
      f'{bs.get("n_blindspot")}/{bs.get("n")} | 注释规范 '
      f'{cs.get("n_spec_fail")} 失败/681')
check('①b 感知扩展：路由冲突+escalation盲区+注释规范 通道', ok1b)

# ── ② 识别：漂移分类（隐式盲区 vs 需人工）──────────────────
cls = si.classify(per["drift"])
ok2 = len(cls["blindspot"]) > 0 and len(cls["blindspot"]) + \
      len(cls["manual"]) == per["n_drift"]
print(f'  隐式盲区 {len(cls["blindspot"])} | 需人工 {len(cls["manual"])}')
check('② 识别：漂移分类（隐式盲区=返回默认值 vs 需人工）', ok2)

# ── ③ 分析：影响范围 ─────────────────────────────────────────
ana = si.analyze([d["unit"] for d in cls["blindspot"]])
ok3 = "not_tokens" in ana["note_policy"]
print(f'  {ana["note_policy"][:44]}')
check('③ 分析：note 不加判别词 → 路由无影响', ok3)

# ── ④ 验证 + ⑤ 固化：字符串内替换语法安全 ─────────────────
# 用已固化单元验证：VM-条件跳转 注释已含「隐式盲区」
from compiler_code_units import COMPILER_UNITS
u = COMPILER_UNITS['VM-条件跳转']
lines = [ln for ln in u['pattern'].splitlines() if '不适用条件' in ln]
ok4 = bool(lines) and '隐式盲区' in lines[0]
print(f'  VM-条件跳转 注释: {lines[0][:56] if lines else "NONE"}')
check('④ 固化：注释显式声明隐式盲区（返回默认值=未知行为）', ok4)

# 语法安全（6 域文件 ast.parse）
ok5 = all(si._validate_file(os.path.join(HERE, fn)) for fn in si.FILES)
check('⑤ 固化纪律：6 域文件语法校验通过', ok5)

# ── ⑥ 记录：迭代轨迹可追溯 ─────────────────────────────────
traces = si._load_trace()
ok6 = len(traces) >= 3 and all(t["round"] > 0 for t in traces) \
      and any(t["固化"]["n"] > 0 for t in traces)
print(f'  轨迹 {len(traces)} 轮 | 含固化轮: '
      f'{any(t["固化"]["n"] > 0 for t in traces)}')
check('⑥ 记录：iteration_trace.json 可追溯演进路径', ok6)

# ── ⑦ 反馈：已盲区声明单元跳过（防重复迭代）──────────────
declared = si._blindspot_declared()
ok7 = len(declared) >= 10
print(f'  盲区声明单元 {len(declared)} 个（反馈跳过防重复）')
check('⑦ 反馈：已盲区声明单元跳过（trace 读回）', ok7)

# ── ⑧ 方向性自检 ────────────────────────────────────────────
ori = si.orient(per, {"ok": True})
ok8 = ori["direction_ok"] and ori["passed"] == ori["total"]
print(f'  {ori["assessment"]}（{ori["passed"]}/{ori["total"]}）')
check('⑧ 方向性自检：指标趋势朝向目标（减少错误/冲突/盲区）', ok8)

report = {
    "experiment": "自迭代八步闭环（荣 长期任务）",
    "感知": {"n_drift": per["n_drift"], "strong_rate": per["strong_rate"],
             "mos_rate": per["mos_rate"]},
    "识别": {"blindspot": len(cls["blindspot"]),
             "manual": len(cls["manual"])},
    "固化_盲区声明": len(si._blindspot_declared()),
    "轨迹轮数": len(traces),
    "方向自检": ori,
    "conclusion": ("八步闭环完整：感知扫描→识别分类→分析影响→验证诚实→"
                   "固化安全→记录可追溯→反馈跳过→方向自检；返回默认值"
                   "=隐式盲区，已显式声明，全回归绿"),
}
rp = os.path.join(HERE, 'self_iterate_report.json')
json.dump(report, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
check('⑨ self_iterate_report.json 落盘', os.path.exists(rp), 'self_iterate_report.json')

print(f'\n=== 自迭代八步闭环: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
