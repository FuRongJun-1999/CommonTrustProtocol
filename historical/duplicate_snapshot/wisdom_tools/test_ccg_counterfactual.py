# -*- coding: utf-8 -*-
"""test_ccg_counterfactual.py · 反事实条件实验（GPT §七/§7.4）

核心验证：候选能力不变、规则不变，只修改【条件】→ 观察
  ① 路由是否改变（不同单元）
  ② 执行计划是否改变（rule/expected_result 不同）
  ③ 执行结果是否改变（同输入域输出不同）
三结果都随条件对应变化 → 条件不仅决定路由，还决定规则和执行计划。

七类对抗（GPT §7.4）：
  1 同主体不同条件 / 2 同条件不同主体 / 3 词面相似条件不同
  4 条件冲突 / 5 缺少前置条件 / 6 伪造条件 / 7 递归循环诱导
"""
import sys, os, json
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import ccg
import execution_plan as ep

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

G = ccg.build_graph()

# ── 核心反事实：条件变体 → 三结果全变 ──────────────────────────
# (任务模板{cond}, 条件A, 条件B, 期望单元A, 期望单元B, 同一输入, 断言)
CF_PAIRS = [
    # 信任引擎：同一主体「信任处理」，条件=累积 vs 阈值检查
    {"tpl": "写一个{cond}处理信任值的代码单元",
     "a_cond": "累积", "b_cond": "阈值检查",
     "a_unit": "VM-信任累积", "b_unit": "校验-信任检查",
     "input": (0.5, 0.4),  # 同输入：累积 0.5+0.4 / 检查 0.5≥0.4
     "a_out": 0.9, "b_out": "pass"},
    # 推导式：同一主体「推导式」，条件=容器类型 列表 vs 字典
    {"tpl": "写一个产生{cond}的推导式代码单元",
     "a_cond": "列表", "b_cond": "字典",
     "a_unit": "推导式-列表推导", "b_unit": "推导式-字典推导",
     # 同输入域：列表 [2,4,6] / 字典 {1:2, 2:4, 3:6}
     "input": ([1, 2, 3], lambda x: x * 2),
     "input_b": ([1, 2, 3], lambda x: x, lambda x: x * 2),
     "a_out": [2, 4, 6], "b_out": {1: 2, 2: 4, 3: 6}},
]

flip = total = 0
cf_details = []
for p in CF_PAIRS:
    total += 1
    qa = p["tpl"].format(cond=p["a_cond"])
    qb = p["tpl"].format(cond=p["b_cond"])
    # ① 路由改变
    ra = ccg.route(qa, G)
    rb = ccg.route(qb, G)
    route_flip = (ra["state"] == "ACCEPT" and ra["unit"] == p["a_unit"]
                  and rb["state"] == "ACCEPT" and rb["unit"] == p["b_unit"])
    # ② 执行计划改变（rule/expected 不同）
    pa = ep.build_plan(qa, G)
    pb = ep.build_plan(qb, G)
    plan_flip = (pa["selected_capability"] == p["a_unit"]
                 and pb["selected_capability"] == p["b_unit"]
                 and pa["rule"] != pb["rule"])
    # ③ 执行结果改变（同输入域，输出不同）
    code_a = ep._lookup_code(p["a_unit"])
    code_b = ep._lookup_code(p["b_unit"])
    out_a = out_b = None
    try:
        ns = {}
        exec(compile(code_a, "<cf>", "exec"), ns)
        fn = next(n for n in ns if callable(ns[n]) and n[0] != '_')
        out_a = ns[fn](*p["input"]) if isinstance(p["input"], tuple) else ns[fn](p["input"])
    except Exception:
        pass
    try:
        ns = {}
        exec(compile(code_b, "<cf>", "exec"), ns)
        fn = next(n for n in ns if callable(ns[n]) and n[0] != '_')
        inp_b = p.get("input_b", p["input"])
        out_b = ns[fn](*inp_b) if isinstance(inp_b, tuple) else ns[fn](inp_b)
    except Exception:
        pass
    res_flip = (out_a == p["a_out"] and out_b == p["b_out"]
                and out_a != out_b)
    three_flip = route_flip and plan_flip and res_flip
    flip += three_flip
    cf_details.append({"qa": qa, "qb": qb,
                       "route": (ra["unit"], rb["unit"]),
                       "rule": (pa["rule"][:30], pb["rule"][:30]),
                       "output": (out_a, out_b),
                       "three_flip": three_flip})
    print(f'[{"✓" if three_flip else "✘"}] 反事实 {p["a_cond"]}↔{p["b_cond"]}')
    print(f'    路由: {ra["unit"][:14]} ↔ {rb["unit"][:14]} '
          f'| 计划rule不同={plan_flip} | 输出 {out_a} ↔ {out_b}')

check('① 反事实三结果全变（路由∧计划∧执行结果随条件改变）',
      flip == total, f'{flip}/{total}')

# ── 七类对抗 ────────────────────────────────────────────────────
# 1 同主体不同条件（已在上核心验证）✓
# 2 同条件不同主体：加权 图 vs 加权 调度（条件词相同，主体不同 → 不同域单元）
q_w_graph = "写一个在加权图上求最短路径的代码单元"
q_w_sched = "写一个加权轮询调度的代码单元"
r_wg = ccg.route(q_w_graph, G)
r_ws = ccg.route(q_w_sched, G)
ok2 = (r_wg["state"] == "ACCEPT" and "加权" in r_wg["unit"]
       and r_ws["state"] == "ACCEPT" and "调度" in r_ws["unit"]
       and r_wg["unit"] != r_ws["unit"])
print(f'[{"✓" if ok2 else "✘"}] 2 同条件不同主体: 加权图→{r_wg.get("unit","")[:14]} '
      f'vs 加权调度→{r_ws.get("unit","")[:14]}')
check('② 同条件不同主体：路由到各自主体单元（非条件词垄断）', ok2)

# 3 词面相似但条件不同：BFS vs 可达性判定（都遍历，条件边界不同）
q_bfs = "写一个 BFS 遍历的代码单元"
q_reach = "写一个可达性判定的代码单元"
r_bfs = ccg.route(q_bfs, G)
r_reach = ccg.route(q_reach, G)
ok3 = (r_bfs["state"] == "ACCEPT" and r_reach["state"] == "ACCEPT"
       and r_bfs["unit"] != r_reach["unit"]
       and "BFS" in r_bfs["unit"] and "可达" in r_reach["unit"])
print(f'[{"✓" if ok3 else "✘"}] 3 词面相似条件不同: BFS→{r_bfs.get("unit","")[:14]} '
      f'vs 可达性→{r_reach.get("unit","")[:14]}')
check('③ 词面相似但条件不同：BFS vs 可达性判定 不混路由', ok3)

# 4 条件冲突：无权 BFS 求带权图 → BLINDSPOT
r_cf4 = ccg.route("写一个用无权 BFS 求带权图最小总代价路径的代码单元", G)
ok4 = r_cf4["state"] == "BLINDSPOT"
print(f'[{"✓" if ok4 else "✘"}] 4 条件冲突: → {r_cf4["state"]} '
      f'{r_cf4.get("reason","")[:20]}')
check('④ 条件冲突：BLINDSPOT 不强行路由', ok4)

# 5 缺少前置条件：注入型独立执行 → 拒绝（诚实声明）
r_inj = ep.run_execution("写一个 BFS 遍历的代码单元", G)
inj_ev = r_inj.get("execution", {}).get("evidence", "")
ok5 = ("注入" in inj_ev or r_inj["plan"]["route_state"] != "ACCEPT")
print(f'[{"✓" if ok5 else "✘"}] 5 缺少前置条件: 注入型 → '
      f'{r_inj["plan"]["route_state"]} {inj_ev[:30]}')
check('⑤ 缺少前置条件：注入型拒绝独立执行（诚实）', ok5)

# 6 伪造条件：任务声称不存在的条件 → BLINDSPOT（判别力不足）
r_cf6 = ccg.route("写一个超光速引擎驱动信任累积的代码单元", G)
ok6 = r_cf6["state"] == "BLINDSPOT"
print(f'[{"✓" if ok6 else "✘"}] 6 伪造条件: → {r_cf6["state"]} '
      f'{r_cf6.get("reason","")[:24]}')
check('⑥ 伪造条件：BLINDSPOT（不假装存在该能力）', ok6)

# 7 递归循环诱导：深度预算内终止
r_cf7 = ccg.route("写一个既累积信任又做阈值检查的代码单元", G, depth=6)
ok7 = r_cf7["state"] in ("BLINDSPOT", "DEFER_EXHAUSTED")
print(f'[{"✓" if ok7 else "✘"}] 7 递归循环诱导: depth6 → {r_cf7["state"]}')
check('⑦ 递归循环诱导：预算内终止不无限递归', ok7)

report = {
    "experiment": "反事实条件实验（GPT §七/7.4）",
    "three_result_flip": {"flip": flip, "n": total,
                          "rate": round(flip / total, 3)},
    "adversarial": {
        "same_subject_diff_condition": "核心验证(①)",
        "same_condition_diff_subject": ok2,
        "similar_words_diff_condition": ok3,
        "condition_conflict": ok4,
        "missing_precondition": ok5,
        "fabricated_condition": ok6,
        "recursion_loop_induce": ok7,
    },
    "details": cf_details,
    "conclusion": ("只改条件词 → 路由/执行计划/执行结果三结果对应变化 = "
                   "条件（非语义相似度）决定路由、规则与执行计划"),
}
rp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'counterfactual_report.json')
json.dump(report, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
check('⑧ counterfactual_report.json 落盘', os.path.exists(rp), 'counterfactual_report.json')

print(f'\n=== 反事实条件实验: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
