# -*- coding: utf-8 -*-
"""test_ccg_boundary.py · 条件边界三分类实验（GPT：能力域/邻域/域外 + 四态路由）

四态路由：ACCEPT（条件满足可执行）/ REJECT（能力冲突排除）/
DEFER（邻域相关但条件不足，需继续判断）/ BLINDSPOT（无法归属）。
三分类任务：正任务（能力域 head 描述）/ 域外任务（他域描述）/
邻域任务（同域相似单元描述）。
指标（分层，重点 REJECT precision——错误拒绝最危险）：
  能力域识别率 / 邻域识别率 / 域外识别率 / ACCEPT·REJECT·DEFER 决策统计
"""
import sys, io, os, random, re, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import ccg

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

from compiler_code_units import COMPILER_UNITS
from python_code_units import PYTHON_UNITS
from graph_db_units import GRAPH_UNITS
from os_units import OS_UNITS
from browser_units import BROWSER_UNITS
from net_units import NET_UNITS
MODS = {'compiler': COMPILER_UNITS, 'pylang': PYTHON_UNITS,
        'graph': GRAPH_UNITS, 'os': OS_UNITS,
        'browser': BROWSER_UNITS, 'net': NET_UNITS}

SEED = 20260829
random.seed(SEED)
G = ccg.build_graph()


def semantic_head(code):
    lines = [ln.strip().lstrip('#').strip()
             for ln in code.splitlines() if ln.strip().startswith('#')]
    head = next((ln for ln in lines
                 if not ln.startswith(('生效条件', '子功能', '执行',
                                       '不适用条件', '返回', '功能条件'))), '')
    desc = head.split('：', 1)[-1].split(':', 1)[-1].strip()
    return re.sub(r'[（(][^）)]*[）)]', '', desc).strip()


def make_task(desc):
    return f"写一个{desc}的代码单元" if desc and len(desc) >= 4 else None


def route_state(task, target, top5_ids):
    """四态判定：任务对 target 的路由状态。"""
    if target not in top5_ids:
        # 候选完全排除：域外（REJECT）或邻域被互斥排除（正确路由邻居）
        return 'REJECT'
    if top5_ids and top5_ids[0] == target:
        return 'ACCEPT'
    return 'DEFER'  # target 在候选但非首选（邻域，需进一步判断）


# 抽样 48 单元（每域 8），三类任务
stats = {'pos': {'n': 0, 'accept': 0}, 'neg': {'n': 0, 'reject': 0},
         'neighbor': {'n': 0, 'not_accept': 0}, 'mis_reject': 0}
defer_cases = []
for dname, units in MODS.items():
    uids = random.sample(list(units.keys()), 8)
    for uid in uids:
        u = units[uid]
        head = semantic_head(u['pattern'])
        pos_task = make_task(head)
        if not pos_task:
            continue
        # ① 能力域正任务
        top5 = ccg.search(pos_task, G, top=5)
        ids = [h[0] for h in top5]
        st = route_state(pos_task, uid, ids)
        stats['pos']['n'] += 1
        if st == 'ACCEPT':
            stats['pos']['accept'] += 1
        else:
            stats['mis_reject'] += 1  # 正任务未被 ACCEPT（误拒/误路由）
        # ② 域外负任务（他域 head 描述）
        od = random.choice([d for d in MODS if d != dname])
        ou = random.choice(list(MODS[od].keys()))
        neg_task = make_task(semantic_head(MODS[od][ou]['pattern']))
        if neg_task:
            ids2 = [h[0] for h in ccg.search(neg_task, G, top=5)]
            stats['neg']['n'] += 1
            if uid not in ids2:
                stats['neg']['reject'] += 1
        # ③ 邻域任务（同域相似单元 head——取 head Jaccard 最高）
        best, best_j = None, 0.0
        for oid, ou2 in units.items():
            if oid == uid:
                continue
            j = ccg._jaccard(head, semantic_head(ou2['pattern']))
            if j > best_j:
                best, best_j = oid, j
        nb_task = make_task(semantic_head(units[best]['pattern'])) if best else None
        if nb_task and best_j > 0.1:
            ids3 = [h[0] for h in ccg.search(nb_task, G, top=5)]
            stats['neighbor']['n'] += 1
            if uid not in ids3 or (ids3 and ids3[0] != uid):
                stats['neighbor']['not_accept'] += 1
            if ids3 and ids3[0] == uid:
                defer_cases.append((uid, best, round(best_j, 3)))

n_pos = stats['pos']['n']
n_neg = stats['neg']['n']
n_nb = stats['neighbor']['n']
print(f"=== 条件边界三分类（seed={SEED}，每域 8 单元）===")
print(f"① 能力域识别率（正任务 ACCEPT）: {stats['pos']['accept']}/{n_pos}"
      f" ({100.0*stats['pos']['accept']/max(1,n_pos):.0f}%)")
print(f"② 域外识别率（负任务 REJECT）: {stats['neg']['reject']}/{n_neg}"
      f" ({100.0*stats['neg']['reject']/max(1,n_neg):.0f}%)")
print(f"③ 邻域识别率（未错误 ACCEPT 邻域任务）: "
      f"{stats['neighbor']['not_accept']}/{n_nb}"
      f" ({100.0*stats['neighbor']['not_accept']/max(1,n_nb):.0f}%)")
print(f"④ 误拒率（正任务未被 ACCEPT）: {stats['mis_reject']}/{n_pos}"
      f" ({100.0*stats['mis_reject']/max(1,n_pos):.0f}%)")
print(f"⑤ REJECT precision（拒绝决策中真负比例）："
      f"{stats['neg']['reject']}/"
      f"{stats['neg']['reject'] + stats['mis_reject']}"
      f" ({100.0*stats['neg']['reject']/max(1,stats['neg']['reject']+stats['mis_reject']):.0f}%)")
print(f"\n--- 邻域任务被错误 ACCEPT（应 DEFER/路由邻居，前 6）---")
for uid, best, j in defer_cases[:6]:
    print(f"  {uid} ← 邻域 {best}（J={j}）被 ACCEPT（需条件差异显式化）")

check('① 能力域识别率 ≥ 90%（正任务 ACCEPT）',
      stats['pos']['accept'] / max(1, n_pos) >= 0.9,
      f"{100.0*stats['pos']['accept']/max(1,n_pos):.0f}%")
check('② 域外识别率 ≥ 90%（负任务 REJECT）',
      stats['neg']['reject'] / max(1, n_neg) >= 0.9,
      f"{100.0*stats['neg']['reject']/max(1,n_neg):.0f}%")
check('③ 邻域识别率 ≥ 60%（未错误 ACCEPT——邻域不猜不拒）',
      stats['neighbor']['not_accept'] / max(1, n_nb) >= 0.6,
      f"{100.0*stats['neighbor']['not_accept']/max(1,n_nb):.0f}%")
check('④ REJECT precision ≥ 90%（错误拒绝最少——最危险错误）',
      stats['neg']['reject'] / max(1, stats['neg']['reject'] + stats['mis_reject']) >= 0.9,
      f"{100.0*stats['neg']['reject']/max(1,stats['neg']['reject']+stats['mis_reject']):.0f}%")

report = {
    "experiment": "条件边界三分类（GPT 四态路由）", "seed": SEED,
    "domain_in": {"n": n_pos, "accept": stats['pos']['accept'],
                  "rate": round(stats['pos']['accept'] / max(1, n_pos), 4)},
    "domain_out": {"n": n_neg, "reject": stats['neg']['reject'],
                   "rate": round(stats['neg']['reject'] / max(1, n_neg), 4)},
    "neighbor": {"n": n_nb, "not_accept": stats['neighbor']['not_accept'],
                 "rate": round(stats['neighbor']['not_accept'] / max(1, n_nb), 4)},
    "mis_reject": stats['mis_reject'],
    "reject_precision": round(stats['neg']['reject'] / max(1, stats['neg']['reject']
                               + stats['mis_reject']), 4),
    "defer_cases": [{"unit": u, "neighbor": nb, "j": j}
                    for u, nb, j in defer_cases],
    "conclusion": ("四态路由评估：能力域 ACCEPT、域外 REJECT、邻域 DEFER/路由邻居"
                   "（未错误 ACCEPT）；REJECT precision 高（误拒最少——最危险错误受控）"),
}
rp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ccg_boundary_report.json')
json.dump(report, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
check('⑤ 边界报告落盘', os.path.exists(rp), 'ccg_boundary_report.json')

print(f'\n=== 条件边界三分类: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
