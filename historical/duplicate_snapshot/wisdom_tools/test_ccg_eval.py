# -*- coding: utf-8 -*-
"""test_ccg_eval.py · CCG 对照评估（现状 route vs ccg_search）

评估集：常规（直接词命中）/ 同义词（中文全称，现状必败或易败）/
多条件（组合词 AND）三类问题，对照命中期望单元的比例。
输出：各类型命中率 + 差异案例（CCG 提升证据）。
"""
import sys, io, json, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import ccg
from code_compose import domain_route

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

G = ccg.build_graph()

# 评估集：{问题: 期望单元}
EVAL = {
    # 常规（直接词）
    "写一个软中断单元（延迟工作）": "中断-软中断",
    "写一个帧解析单元（报文解码）": "网络-帧解析",
    "写一个顶点覆盖单元（边端点选取）": "图算法-顶点覆盖",
    "写一个事件委托单元（祖先分派）": "事件-事件委托",
    "写一个解包赋值单元（多重赋值）": "求值-解包赋值",
    "写一个名实绑定单元（以名举实）": "编译-名实绑定",
    "写一个证书校验单元（有效期检查）": "网络-证书校验",
    "写一个弹窗拦截单元（用户手势）": "浏览器-弹窗拦截",
    "写一个工作窃取单元（空闲核均衡）": "调度-工作窃取",
    "写一个集合推导单元（去重构建）": "推导式-集合推导",
    # 同义词（中文全称——现状易败）
    "写一个广度优先搜索单元": "图遍历-BFS",
    "写一个网页地址解析单元": "URL-解析",
    "写一个虚拟内存页表单元": "内存-页表映射",
    "写一个最小生成树单元": "图算法-最小生成树",
    "写一个最近公共祖先单元": "图算法-最近公共祖先",
    # 多条件（组合词 AND）
    "写一个加权最短路径单元": "图遍历-加权最短",
    "写一个网络帧解析单元": "网络-帧解析",
    "写一个多核任务窃取单元": "调度-工作窃取",
    "写一个浏览器事件委托单元": "事件-事件委托",
}

route_hit = ccg_hit = 0
route_fail_cases = []   # route 失败但 ccg 命中
both_fail = []
detail = []
for q, exp in EVAL.items():
    r = domain_route(q)
    r_ok = r.get('ok') and r.get('unit') == exp
    hits = ccg.search(q, G, top=1)
    c_ok = bool(hits) and hits[0][0] == exp
    if r_ok:
        route_hit += 1
    if c_ok:
        ccg_hit += 1
    if r_ok and not c_ok:
        both_fail.append((q, exp, 'route 中但 ccg 未中'))
    if not r_ok and c_ok:
        route_fail_cases.append((q, exp, r.get('reason', '')[:30]))
    if not r_ok and not c_ok:
        both_fail.append((q, exp, '双未中'))
    detail.append((q, r_ok, c_ok, r.get('unit'), hits[0][0] if hits else None))

n = len(EVAL)
print(f"评估集: {n} 题（常规 10 / 同义词 5 / 多条件 5）")
print(f"现状 route 命中: {route_hit}/{n} ({100.0*route_hit/n:.0f}%)")
print(f"CCG search 命中: {ccg_hit}/{n} ({100.0*ccg_hit/n:.0f}%)")
print(f"\n--- route 失败但 CCG 命中（CCG 提升证据）---")
for q, exp, reason in route_fail_cases:
    print(f"  「{q}」期望 {exp}（route: {reason}）")
print(f"\n--- 双未中 ---")
for q, exp, why in both_fail:
    print(f"  「{q}」期望 {exp}（{why}）")

check('① CCG 命中率 ≥ 现状 route', ccg_hit >= route_hit,
      f"{ccg_hit} vs {route_hit}")
check('② CCG 命中率 ≥ 90%', ccg_hit / n >= 0.9, f"{100.0*ccg_hit/n:.0f}%")
check('③ 同义词类全命中（中文全称检索）',
      all(h and h[2] for q, exp in list(EVAL.items())[10:15]
          for h in [next((d for d in detail if d[0] == q), None)]), '')

# 报告落盘
report = {
    "eval_set": n, "route_hit": route_hit, "ccg_hit": ccg_hit,
    "route_rate": round(100.0 * route_hit / n, 1),
    "ccg_rate": round(100.0 * ccg_hit / n, 1),
    "ccg_improved_cases": len(route_fail_cases),
    "both_fail": [q for q, _, _ in both_fail],
}
rp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ccg_eval_report.json')
json.dump(report, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
check('④ 评估报告落盘', os.path.exists(rp), 'ccg_eval_report.json')

print(f'\n=== CCG 对照评估: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
