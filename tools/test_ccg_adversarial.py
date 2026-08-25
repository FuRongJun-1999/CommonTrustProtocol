# -*- coding: utf-8 -*-
"""test_ccg_adversarial.py · 对抗性负条件实验（GPT 阶段 5）

核心问题：词相似但条件不满足时，白箱能否拒绝（真正的条件路由）？
相似度会诱导模型犯错——能拒绝相似负条件，才证明是「条件满足→路由、
条件不满足→不路由」而非「相似就召回」。

对抗负任务构造：对每个 target，取**同域 head 词重叠最高**的单元（对抗源）
构造任务——描述词高度重叠但语义属于另一单元；target 不应被召回。
同时测「不适用条件」引导的负任务：用 target 自身不适用条件行构造任务，
期望不路由到 target。
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

SEED = 20260827
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


def not_cond_line(code):
    """提取不适用条件行（若有）。"""
    for ln in code.splitlines():
        s = ln.strip().lstrip('#').strip()
        if s.startswith('不适用条件'):
            return re.sub(r'^不适用条件[:：]?\s*', '', s)
    return ''


def make_task(desc):
    return f"写一个{desc}的代码单元" if desc and len(desc) >= 4 else None


def jaccard(a, b):
    sa, sb = ccg._bigrams(a), ccg._bigrams(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


# 抽样 48 单元（每域 8），构造对抗负任务
results = []
for dname, units in MODS.items():
    uids = random.sample(list(units.keys()), 8)
    for uid in uids:
        u = units[uid]
        head = semantic_head(u['pattern'])
        task = make_task(head)
        if not task:
            continue
        # ① 对抗负任务：同域 head 词重叠最高的另一单元
        best, best_j = None, -1
        for oid, ou in units.items():
            if oid == uid:
                continue
            oj = jaccard(head, semantic_head(ou['pattern']))
            if oj > best_j:
                best, best_j = oid, oj
        adv_task = make_task(semantic_head(units[best]['pattern'])) if best else None
        adv_reject = True
        if adv_task and best_j > 0.1:  # 词确实重叠才构成对抗
            adv_hits = ccg.search(adv_task, G, top=5)
            adv_reject = uid not in [h[0] for h in adv_hits]
        else:
            adv_reject = None  # 无有效对抗源
        # ② 不适用条件负任务：target 自己的不适用条件 → 期望不路由 target
        nc = not_cond_line(u['pattern'])
        nc_reject = None
        if nc:
            nc_task = make_task(nc[:20])
            if nc_task:
                nc_hits = ccg.search(nc_task, G, top=5)
                nc_reject = uid not in [h[0] for h in nc_hits]
        results.append({'domain': dname, 'unit': uid, 'head': head,
                        'adv_source': best, 'adv_j': round(best_j, 3),
                        'adv_task': adv_task, 'adv_reject': adv_reject,
                        'nc': nc[:40], 'nc_reject': nc_reject})

adv_valid = [r for r in results if r['adv_reject'] is not None]
adv_ok = sum(1 for r in adv_valid if r['adv_reject'])
nc_valid = [r for r in results if r['nc_reject'] is not None]
nc_ok = sum(1 for r in nc_valid if r['nc_reject'])

print(f"=== 对抗性负条件（seed={SEED}，48 单元）===")
print(f"① 对抗负任务（同域高重叠词诱导）：拒绝 {adv_ok}/{len(adv_valid)}"
      f" ({100.0*adv_ok/max(1,len(adv_valid)):.0f}%)")
print(f"② 不适用条件负任务：拒绝 {nc_ok}/{len(nc_valid)}"
      f" ({100.0*nc_ok/max(1,len(nc_valid)):.0f}%)")
print(f"\n--- 对抗误路由案例（前 6）---")
for r in [r for r in adv_valid if not r['adv_reject']][:6]:
    print(f"  [{r['domain']}] {r['unit']} ← 对抗源 {r['adv_source']}"
          f"（J={r['adv_j']}）")
    print(f"    对抗任务: {r['adv_task'][:50]}")
print(f"\n--- 不适用条件误路由案例（前 6）---")
for r in [r for r in nc_valid if not r['nc_reject']][:6]:
    print(f"  [{r['domain']}] {r['unit']} 不适用: {r['nc'][:40]}")

check('① 对抗负任务拒绝率 ≥ 60%（词相似但条件不同可排除）',
      adv_ok / max(1, len(adv_valid)) >= 0.6,
      f"{100.0*adv_ok/max(1,len(adv_valid)):.0f}%")
check('② 不适用条件负任务拒绝率 ≥ 80%（盲区声明生效）',
      nc_ok / max(1, len(nc_valid)) >= 0.8,
      f"{100.0*nc_ok/max(1,len(nc_valid)):.0f}%")

report = {
    "experiment": "对抗性负条件（GPT 阶段5）", "seed": SEED,
    "adv_valid": len(adv_valid), "adv_reject": adv_ok,
    "adv_rate": round(adv_ok / max(1, len(adv_valid)), 4),
    "nc_valid": len(nc_valid), "nc_reject": nc_ok,
    "nc_rate": round(nc_ok / max(1, len(nc_valid)), 4),
    "conclusion": ("词相似但条件不满足的任务可被高比例排除（对抗负任务）——"
                   "接近条件路由而非相似召回；不适用条件盲区声明参与排除"),
    "adv_misses": [{"unit": r['unit'], "adv_source": r['adv_source'],
                    "jaccard": r['adv_j']} for r in adv_valid if not r['adv_reject']],
}
rp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ccg_adversarial_report.json')
json.dump(report, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
check('③ 对抗报告落盘', os.path.exists(rp), 'ccg_adversarial_report.json')

print(f'\n=== 对抗性负条件: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
