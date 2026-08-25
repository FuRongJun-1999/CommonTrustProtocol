# -*- coding: utf-8 -*-
"""test_ccg_adversarial2.py · 新对抗集（GPT：验证 88% 非补丁）

旧集（test_ccg_adversarial）：同域 head 词重叠最高对 → 28% → 88%。
新集机制不同：
  ① task 语义邻接对（同域 task 词重叠，非 head 词）
  ② 边界条件对（相似功能不同条件：图遍历-BFS vs 加权最短——都遍历但条件不同）
若新集拒绝率仍显著（X→Y 提升），则能力级互斥是结构性升级而非针对旧集打补丁。
"""
import sys, io, os, random, json
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

SEED = 20260828
random.seed(SEED)
G = ccg.build_graph()


def semantic_head(code):
    import re as _re
    lines = [ln.strip().lstrip('#').strip()
             for ln in code.splitlines() if ln.strip().startswith('#')]
    head = next((ln for ln in lines
                 if not ln.startswith(('生效条件', '子功能', '执行',
                                       '不适用条件', '返回', '功能条件'))), '')
    desc = head.split('：', 1)[-1].split(':', 1)[-1].strip()
    return _re.sub(r'[（(][^）)]*[）)]', '', desc).strip()


def make_task(desc):
    return f"写一个{desc}的代码单元" if desc and len(desc) >= 4 else None


def task_jaccard(a, b):
    return ccg._jaccard(a, b)


# ① task 语义邻接对：同域 task 词 Jaccard 最高（非 head）
task_pairs = []
for dname, units in MODS.items():
    uids = list(units.keys())
    for uid in uids:
        best, best_j = None, 0.0
        for oid in uids:
            if oid == uid:
                continue
            j = task_jaccard(units[uid]['task'], units[oid]['task'])
            if j > best_j:
                best, best_j = oid, j
        if best and best_j >= 0.15:
            task_pairs.append((uid, best, best_j, dname))

# ② 边界条件对（人工：相似功能不同条件）
boundary_pairs = [
    ("图遍历-BFS", "图遍历-加权最短", "graph"),
    ("图遍历-最短路径", "图遍历-加权最短", "graph"),
    ("编译-逻辑表达式", "语法-三元表达式", "compiler"),
    ("内存-分页分配", "内存-页置换", "os"),
    ("网络-报文解析", "网络-报文分片", "net"),
    ("浏览器-本地存储", "存储-会话存储", "browser"),
    ("推导式-列表推导", "推导式-字典推导", "pylang"),
]

results = []
# ① task 邻接对抗：任务 = target head 描述，对抗 = 邻接单元 B 的 head → target 应排除
task_ok = task_total = 0
for uid, adv, j, dname in task_pairs:
    u = MODS[dname][uid]
    task = make_task(semantic_head(u['pattern']))
    adv_task = make_task(semantic_head(MODS[dname][adv]['pattern']))
    if not task or not adv_task:
        continue
    task_total += 1
    hits = ccg.search(adv_task, G, top=5)
    reject = uid not in [h[0] for h in hits]
    if reject:
        task_ok += 1
    results.append({'type': 'task-adj', 'unit': uid, 'adv': adv,
                    'j': round(j, 3), 'reject': reject})

# ② 边界条件对抗：任务 = B 功能描述 → A 应排除
bnd_ok = bnd_total = 0
for a, b, dname in boundary_pairs:
    units = MODS[dname]
    if a not in units or b not in units:
        continue
    task = make_task(semantic_head(units[b]['pattern']))
    if not task:
        continue
    bnd_total += 1
    hits = ccg.search(task, G, top=5)
    reject = a not in [h[0] for h in hits]
    if reject:
        bnd_ok += 1
    results.append({'type': 'boundary', 'unit': a, 'adv': b,
                    'reject': reject})

print(f"=== 新对抗集（seed={SEED}，机制不同）===")
print(f"① task 语义邻接对：拒绝 {task_ok}/{task_total}"
      f" ({100.0*task_ok/max(1,task_total):.0f}%)")
print(f"② 边界条件对（相似功能不同条件）：拒绝 {bnd_ok}/{bnd_total}"
      f" ({100.0*bnd_ok/max(1,bnd_total):.0f}%)")
all_ok = task_ok + bnd_ok
all_tot = task_total + bnd_total
print(f"新集合计：拒绝 {all_ok}/{all_tot} ({100.0*all_ok/max(1,all_tot):.0f}%)"
      f"（旧集 88%，机制不同验证）")
print("\n--- 新集未拒绝（前 8）---")
for r in [r for r in results if not r['reject']][:8]:
    print(f"  [{r['type']}] {r['unit']} ← {r['adv']}（J={r.get('j','边界')}）")

check('① task 邻接对抗拒绝率 ≥ 60%（机制不同的新集）',
      task_ok / max(1, task_total) >= 0.6,
      f"{100.0*task_ok/max(1,task_total):.0f}%")
check('② 边界条件对抗拒绝率 ≥ 70%（相似功能不同条件可排除）',
      bnd_ok / max(1, bnd_total) >= 0.7,
      f"{100.0*bnd_ok/max(1,bnd_total):.0f}%")
check('③ 新集合计拒绝率 ≥ 60%（非针对旧集打补丁）',
      all_ok / max(1, all_tot) >= 0.6,
      f"{100.0*all_ok/max(1,all_tot):.0f}%")

report = {
    "experiment": "新对抗集（GPT：验证 88% 非补丁）", "seed": SEED,
    "task_adj": {"n": task_total, "reject": task_ok,
                 "rate": round(task_ok / max(1, task_total), 4)},
    "boundary": {"n": bnd_total, "reject": bnd_ok,
                 "rate": round(bnd_ok / max(1, bnd_total), 4)},
    "conclusion": ("机制不同的新对抗集拒绝率——若显著，能力级互斥为结构性升级"
                   "（非旧集补丁）"),
    "misses": [{"type": r['type'], "unit": r['unit'], "adv": r['adv']}
               for r in results if not r['reject']],
}
rp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ccg_adversarial2_report.json')
json.dump(report, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
check('④ 新对抗集报告落盘', os.path.exists(rp), 'ccg_adversarial2_report.json')

print(f'\n=== 新对抗集: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
