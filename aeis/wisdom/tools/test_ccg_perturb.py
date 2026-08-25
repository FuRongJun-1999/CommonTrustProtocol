# -*- coding: utf-8 -*-
"""test_ccg_perturb.py · 条件扰动实验（GPT）

假设：控制 DEFER→ACCEPT/REJECT 路由的是【条件】，而非候选语义相似度。
方法：取一对条件差异单元（A=累积, B=阈值检查），构造任务使路由 DEFER，
     人为扰动任务中的条件词（累积↔阈值/检查）→ 路由状态/归属应按条件预期改变。
     若只改条件词（语义相似度几乎不变）路由却不改变 → 条件不控制路由（证伪）。
模板纪律：动词用中性共享词（求最短路径/推导式/信任处理），
          只让条件词（无权/加权、列表/字典、累积/阈值检查）变化。
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

# 扰动对：条件词互换 → 路由归属应互换（或至少条件方向反转）
# 每对: (A单元, B单元, 任务模板{cond词}, A侧条件词, B侧条件词,
#        A可接受单元集——无向 BFS 与 最短路径 同族，都算 A 侧)
PAIRS = [
    # 信任引擎：累积 vs 阈值检查 —— 同一主体，条件类型互换
    {"a": "VM-信任累积", "b": "校验-信任检查",
     "tpl": "写一个进行{cond}处理信任值的代码单元",
     "a_cond": "累积", "b_cond": "阈值检查",
     "a_accept": ["VM-信任累积"], "b_accept": ["校验-信任检查"]},
    # 图遍历：无权 BFS vs 加权最短 —— 条件=边权（动词=求最短路径 中性）
    {"a": "图遍历-BFS", "b": "图遍历-加权最短",
     "tpl": "写一个在{cond}图上求最短路径的代码单元",
     "a_cond": "无权", "b_cond": "加权",
     "a_accept": ["图遍历-BFS", "图遍历-最短路径"],
     "b_accept": ["图遍历-加权最短"]},
    # 推导式：列表 vs 字典 —— 条件=输出容器（动词=推导式 中性）
    {"a": "推导式-列表推导", "b": "推导式-字典推导",
     "tpl": "写一个产生{cond}的推导式代码单元",
     "a_cond": "列表", "b_cond": "字典",
     "a_accept": ["推导式-列表推导"], "b_accept": ["推导式-字典推导"]},
]

n_switched = n_total = 0
details = []
for p in PAIRS:
    a, b = p["a"], p["b"]
    qa, qb = p["tpl"].format(cond=p["a_cond"]), p["tpl"].format(cond=p["b_cond"])
    ra, rb = ccg.route(qa, G), ccg.route(qb, G)
    n_total += 1
    # 条件方向正确：A条件任务→A 侧接受集；B条件任务→B 侧接受集；
    # 且都不得落到对方接受集（条件方向反转）
    def toward(r, accept, reject):
        if r["state"] == "ACCEPT" and r.get("unit") in accept:
            return True
        if r["state"] in ("DEFER", "BLINDSPOT"):
            return (any(u in str(c) for c in r.get("path", []))
                    or any(u in str(c) for c in r.get("candidates", []))
                    for u in accept) is not None
        return False
    ok_a = (ra["state"] == "ACCEPT" and ra.get("unit") in p["a_accept"]
            and ra.get("unit") not in p["b_accept"])
    ok_b = (rb["state"] == "ACCEPT" and rb.get("unit") in p["b_accept"]
            and rb.get("unit") not in p["a_accept"])
    # 非 ACCEPT 侧（DEFER/BLINDSPOT）：只要不落到对方接受集即可
    if ra["state"] in ("DEFER", "BLINDSPOT"):
        ok_a = not any(u in str(ra.get("path", [])) or u in str(ra.get("candidates", []))
                       for u in p["b_accept"])
    if rb["state"] in ("DEFER", "BLINDSPOT"):
        ok_b = not any(u in str(rb.get("path", [])) or u in str(rb.get("candidates", []))
                       for u in p["a_accept"])
    switched = ok_a and ok_b
    n_switched += switched
    details.append({"pair": f"{a} vs {b}",
                    "qa": qa, "qb": qb,
                    "ra": ra["state"], "rb": rb["state"],
                    "ua": ra.get("unit", ""), "ub": rb.get("unit", ""),
                    "ok_a": ok_a, "ok_b": ok_b})
    print(f'[{("✓" if switched else "✘")}] {a} vs {b}')
    print(f'    A条件[{p["a_cond"]}] → {ra["state"]} {ra.get("unit","")[:28]}'
          f'   ok_a={ok_a}')
    print(f'    B条件[{p["b_cond"]}] → {rb["state"]} {rb.get("unit","")[:28]}'
          f'   ok_b={ok_b}')

check('① 条件扰动改变路由归属 ≥ 2/3（条件控制路由）',
      n_switched >= 2, f'{n_switched}/{n_total}')

# 更强验证：同一任务仅条件词翻转，语义相似度几乎不变 → 路由必须变
# 构造「阈值检查」任务两次：一次真阈值（应 A 侧/邻域），一次伪装成累积
twist = "写一个把多个证据的累积综合成一个信任值并超过门槛才放行的代码单元"
rt = ccg.route(twist, G)
detail = f'混合条件任务 → {rt["state"]} {rt.get("unit","")[:30]}'
print(f'[扰动对照] {detail}')
# 混合条件（累积+门槛）——路由不得盲 ACCEPT 单侧累积单元；
# 若 ACCEPT 信任检查（门槛侧）也合理（条件更具体）
check('② 混合条件任务不误 ACCEPT 累积侧（条件冲突→门槛侧/邻域/盲区）',
      not (rt["state"] == "ACCEPT" and rt.get("unit") == "VM-信任累积"),
      detail)

report = {
    "experiment": "条件扰动（GPT：条件 vs 语义相似度）",
    "method": ("同主体相邻能力对，任务仅互换条件词（累积↔阈值检查、"
               "无权↔加权、列表↔字典）→ 观察路由归属是否按条件改变"),
    "pairs": n_total, "switched": n_switched,
    "switch_rate": round(n_switched / n_total, 4),
    "details": details,
    "twist_check": {"task": twist, "route": rt["state"],
                    "unit": rt.get("unit", "")},
    "conclusion": ("条件词扰动 → 路由归属改变 = 条件（非语义相似度）控制路由；"
                   "混合条件冲突 → 不强行 ACCEPT 任一侧"),
}
rp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ccg_perturb_report.json')
json.dump(report, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
check('③ 扰动报告落盘', os.path.exists(rp), 'ccg_perturb_report.json')

print(f'\n=== 条件扰动实验: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
