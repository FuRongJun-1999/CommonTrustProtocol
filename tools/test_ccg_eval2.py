# -*- coding: utf-8 -*-
"""test_ccg_eval2.py · CCG 扩展对照评估（54 题：六域各 6 常规 + 3 变体）

常规：task 权威名直中；变体：同义词/功能词描述（现状 route 易败）。
对照：现状 route vs ccg_search 命中率 + 提升案例。
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

# 变体问题（同义词/功能词，每域 3）
VARIANTS = {
    "compiler": [("写一个字节码编码单元", "字节码-序列化"),
                 ("写一个虚拟机执行循环单元", "VM-执行循环"),
                 ("写一个条件跳转编译单元", "编译-若则")],
    "pylang": [("写一个列表推导式单元", "推导式-列表推导"),
               ("写一个字典推导式单元", "推导式-字典推导"),
               ("写一个迭代器协议单元", "迭代器-协议")],
    "graph": [("写一个广度优先遍历单元", "图遍历-BFS"),
              ("写一个最小生成树单元", "图算法-最小生成树"),
              ("写一个拓扑排序单元", "图算法-拓扑排序")],
    "os": [("写一个虚拟内存缺页处理单元", "内存-缺页处理"),
           ("写一个进程调度单元", "进程-调度"),
           ("写一个文件系统路径解析单元", "文件-路径解析")],
    "browser": [("写一个网页请求构建单元", "HTTP-请求构建"),
                ("写一个本地存储单元", "存储-本地存储"),
                ("写一个动画帧单元", "渲染-动画帧")],
    "net": [("写一个TCP握手单元", "网络-TCP握手"),
            ("写一个数据包解析单元", "网络-报文解析"),
            ("写一个网络地址划分子网单元", "网络-CIDR")],
}

# 常规问题：每域取 6 个单元（task 直中）
from compiler_code_units import COMPILER_UNITS
from python_code_units import PYTHON_UNITS
from graph_db_units import GRAPH_UNITS
from os_units import OS_UNITS
from browser_units import BROWSER_UNITS
from net_units import NET_UNITS
MODS = {"compiler": COMPILER_UNITS, "pylang": PYTHON_UNITS,
        "graph": GRAPH_UNITS, "os": OS_UNITS,
        "browser": BROWSER_UNITS, "net": NET_UNITS}

EVAL = []
for dname, units in MODS.items():
    picks = [uid for uid in units if uid not in {v[1] for v in VARIANTS[dname]}][:6]
    for uid in picks:
        EVAL.append((f"写一个{units[uid]['task']}单元", uid))
    for q, exp in VARIANTS[dname]:
        EVAL.append((q, exp))

route_hit = ccg_hit = 0
route_fail_cases = []
both_fail = []
for q, exp in EVAL:
    r = domain_route(q)
    r_ok = r.get('ok') and r.get('unit') == exp
    hits = ccg.search(q, G, top=1)
    c_ok = bool(hits) and hits[0][0] == exp
    if r_ok:
        route_hit += 1
    if c_ok:
        ccg_hit += 1
    if not r_ok and c_ok:
        route_fail_cases.append((q, exp, r.get('reason', '')[:28]))
    if not r_ok and not c_ok:
        both_fail.append((q, exp))

n = len(EVAL)
print(f"扩展评估集: {n} 题（六域各 6 常规 + 3 变体）")
print(f"现状 route 命中: {route_hit}/{n} ({100.0*route_hit/n:.0f}%)")
print(f"CCG search 命中: {ccg_hit}/{n} ({100.0*ccg_hit/n:.0f}%)")
print(f"\n--- route 失败但 CCG 命中（{len(route_fail_cases)} 例）---")
for q, exp, reason in route_fail_cases:
    print(f"  「{q}」期望 {exp}（route: {reason}）")
print(f"\n--- 双未中（{len(both_fail)}）---")
for q, exp in both_fail:
    print(f"  「{q}」期望 {exp}")

check('① CCG 命中率 ≥ 现状 route', ccg_hit >= route_hit,
      f"{ccg_hit} vs {route_hit}")
check('② CCG 命中率 ≥ 85%（扩展集）', ccg_hit / n >= 0.85,
      f"{100.0*ccg_hit/n:.0f}%")
check('③ 变体类（同义词/功能词）CCG 全命中',
      all(ccg.search(q, G, top=1) and ccg.search(q, G, top=1)[0][0] == exp
          for q, exp in [v for vs in VARIANTS.values() for v in vs]))

report = {
    "eval_set": n, "route_hit": route_hit, "ccg_hit": ccg_hit,
    "route_rate": round(100.0 * route_hit / n, 1),
    "ccg_rate": round(100.0 * ccg_hit / n, 1),
    "ccg_improved": len(route_fail_cases),
    "both_fail": [q for q, _ in both_fail],
}
rp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ccg_eval2_report.json')
json.dump(report, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
check('④ 扩展评估报告落盘', os.path.exists(rp), 'ccg_eval2_report.json')

print(f'\n=== CCG 扩展对照评估: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
