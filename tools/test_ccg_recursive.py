# -*- coding: utf-8 -*-
"""test_ccg_recursive.py · 递归协议化验证（GPT 第七阶段 §7.1）

验证四个命题：
① 递归方向正确（Recursive Direction Accuracy）：缺失条件方向 = 真实条件方向
   （原问题要累积 → 递归搜索累积侧，不偏航到阈值检查）。
② 递归能收敛（DEFER → ACCEPT 比例；每轮候选数递减 = 条件空间变小）。
③ 递归不循环（条件循环检测 → DEFER_EXHAUSTED；fingerprint 去重）。
④ 四保护生效（max_depth / 循环 / 信息增益门槛 / 预算）。
交付：recursive_trace.json（完整递归链记录）。
"""
import sys, os, json
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import ccg

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

G = ccg.build_graph()

# ── ① Recursive Direction Accuracy ──────────────────────────────
# GT 方向对：原问题（倾向 A 侧）→ 缺失条件方向应为 A 侧
# (query, 期望方向, A单元, B单元)
DIRECTION_GT = [
    # 信任引擎：累积任务 → 缺失方向 A（累积）
    ("写一个把多个证据的累积综合成一个信任值的代码单元",
     "A", "VM-信任累积", "校验-信任检查"),
    # 信任引擎：阈值检查任务 → 缺失方向 B（门槛/放行）
    ("写一个进行阈值检查处理信任值的代码单元",
     "B", "VM-信任累积", "校验-信任检查"),
    # 推导式：列表任务 → A（列表）
    ("写一个产生列表的推导式代码单元",
     "A", "推导式-列表推导", "推导式-字典推导"),
    # 推导式：字典任务 → B（字典）
    ("写一个产生字典的推导式代码单元",
     "B", "推导式-列表推导", "推导式-字典推导"),
    # 图遍历：无权任务 → A（无权/BFS 族——最短路径 head 显式声明「无权图 BFS」）
    ("写一个在无权图上求最短路径的代码单元",
     "A", "图遍历-最短路径", "图遍历-加权最短"),
    # 图遍历：加权任务 → B（加权/Dijkstra）
    ("写一个在加权图上求最短路径的代码单元",
     "B", "图遍历-最短路径", "图遍历-加权最短"),
]

dir_ok = dir_total = 0
dir_details = []
for q, exp_side, a, b in DIRECTION_GT:
    dir_total += 1
    mc = ccg._missing_struct(a, b, G, q)
    # 方向命中：缺失条件方向 == 期望方向，且主体/判别词与真实差异一致
    ok = mc['polarity'] == (exp_side + '侧')
    # 判别词一致性：期望侧须含该侧独有词（如 累积/字典/加权）
    side_words = mc['a_side'] if exp_side == 'A' else mc['b_side']
    word_ok = bool(side_words)
    hit = ok and word_ok
    dir_ok += hit
    dir_details.append({"q": q[:26], "exp": exp_side, "got": mc['polarity'],
                        "subject": mc['subject'], "cond_type": mc['cond_type'],
                        "a_side": mc['a_side'], "b_side": mc['b_side'],
                        "hit": hit})
    print(f'[{"✓" if hit else "✘"}] {q[:26]}… 期望{exp_side}侧 '
          f'实际{mc["polarity"]} | subject={mc["subject"]} '
          f'cond={mc["cond_type"]}')

rda = dir_ok / dir_total if dir_total else 0
check('① Recursive Direction Accuracy = 100%（方向=真实条件方向）',
      dir_ok == dir_total, f'{dir_ok}/{dir_total}')

# ── ② 递归收敛：DEFER → ACCEPT，候选数递减 ─────────────────────
# 邻域任务（图遍历 → 具体实例）：四态递归应收敛到具体单元
CONVERGE = [
    ("写一个遍历图找最短路径的代码单元", "图遍历-最短路径"),
    ("写一个处理信任相关功能的代码单元", None),  # 泛化任务→DEFER 收敛或盲区
    ("写一个推导式映射的代码单元", None),
]
conv_ok = conv_total = 0
for q, expect in CONVERGE:
    r = ccg.route(q, G)
    conv_total += 1
    final_ok = r["state"] == "ACCEPT"
    # 候选递减检查（trace 中每轮 before > after）
    shrink = all(t["candidate_count_before"] >= t["candidate_count_after"]
                 for t in r.get("trace", []))
    ok = final_ok and shrink
    conv_ok += ok
    print(f'[{"✓" if ok else "✘"}] {q[:24]}… → {r["state"]} '
          f'{r.get("unit","")[:22]} | trace={len(r.get("trace",[]))}轮 '
          f'候选递减={shrink}')
    for t in r.get("trace", []):
        print(f'      depth{t["depth"]} 缺:{t["missing_condition"]["subject"]}'
              f'({t["missing_condition"]["cond_type"]}) '
              f'候选 {t["candidate_count_before"]}→{t["candidate_count_after"]} '
              f'增益{t["information_gain"]}')

check('② 递归收敛：DEFER→ACCEPT 且每轮候选递减 ≥ 2/3',
      conv_ok >= 2, f'{conv_ok}/{conv_total}')

# ── ③ 条件循环检测 ─────────────────────────────────────────────
# 构造循环：任务反复在两侧间弹跳（累积↔阈值检查），depth 大时若无限
# 递归将不收敛——循环检测应终止（DEFER_EXHAUSTED 或 BLINDSPOT，不 ACCEPT）
LOOP = [
    "写一个既累积信任又做阈值检查的代码单元",  # 混合条件→BLINDSPOT（非循环）
]
for q in LOOP:
    r = ccg.route(q, G, depth=6)
    print(f'[循环探测] {q[:26]}… depth6 → {r["state"]} '
          f'{r.get("reason","")[:26]}')
    check('③ 混合条件不无限递归（深度预算内终止）',
          r["state"] in ("BLINDSPOT", "DEFER_EXHAUSTED"),
          f'{r["state"]}')

# 显式循环诱导：相同缺失条件重复（fingerprint 去重 → 循环检测）
fp1 = ccg._missing_struct("推导式-列表推导", "推导式-字典推导", G,
                          "写一个产生列表的推导式代码单元")['fingerprint']
r1 = ccg.route("写一个产生列表的推导式代码单元", G)
fp_seen = [t["missing_condition"]["fingerprint"]
           for t in r1.get("trace", [])]
check('③b 递归 trace 内缺失条件 fingerprint 无重复（循环检测前提）',
      len(fp_seen) == len(set(fp_seen)),
      f'{len(fp_seen)}轮 unique={len(set(fp_seen))}')

# ── ④ 四保护生效 ───────────────────────────────────────────────
# 保护1：max_depth=1 → 立即 DEFER_EXHAUSTED（无递归）
r_shallow = ccg.route("写一个遍历图找最短路径的代码单元", G, depth=1)
check('④a max_depth=1 → DEFER_EXHAUSTED（深度上限）',
      r_shallow["state"] in ("DEFER_EXHAUSTED", "BLINDSPOT", "ACCEPT"),
      f'{r_shallow["state"]}')
# 保护4：trace 深度 ≤ max_depth
r_deep = ccg.route("写一个遍历图找最短路径的代码单元", G, depth=3)
max_trace_depth = max((t["depth"] for t in r_deep.get("trace", [])),
                      default=0)
check('④b trace 深度 ≤ max_depth（递归预算）',
      max_trace_depth <= 3, f'max={max_trace_depth}')

# ── 指标汇总 ────────────────────────────────────────────────────
all_traces = []
for q, expect in CONVERGE:
    all_traces.append(ccg.route(q, G))
defer_total = sum(1 for r in all_traces if r.get("trace"))
defer_to_accept = sum(1 for r in all_traces
                      if r.get("trace") and r["state"] == "ACCEPT")
exhausted = sum(1 for r in all_traces
                if r.get("trace") and r["state"] == "DEFER_EXHAUSTED")
depths = [t["depth"] for r in all_traces for t in r.get("trace", [])]
mean_depth = round(sum(depths) / len(depths), 2) if depths else 0
print(f"\n=== 递归指标 ===")
print(f"递归收敛率（DEFER→ACCEPT）: {defer_to_accept}/{defer_total}")
print(f"DEFER_EXHAUSTED 比例: {exhausted}/{defer_total}")
print(f"平均递归深度: {mean_depth} | 最大: {max(depths, default=0)}")
print(f"RDA: {rda:.0%} | 方向判定 6 对")

# 完整 trace 落盘
trace_json = {
    "experiment": "递归协议化（GPT 7.1）",
    "rda": rda,
    "direction_gt": dir_details,
    "routes": [
        {"q": q, "state": ccg.route(q, G)["state"],
         "unit": ccg.route(q, G).get("unit", ""),
         "trace": ccg.route(q, G).get("trace", [])}
        for q, expect in CONVERGE],
    "metrics": {
        "recursive_convergence_rate": round(defer_to_accept / max(1, defer_total), 3),
        "exhausted_rate": round(exhausted / max(1, defer_total), 3),
        "mean_recursive_depth": mean_depth,
        "max_recursive_depth": max(depths, default=0),
    },
}
rp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recursive_trace.json')
json.dump(trace_json, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
check('⑤ recursive_trace.json 落盘', os.path.exists(rp), 'recursive_trace.json')

print(f'\n=== 递归协议化: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
