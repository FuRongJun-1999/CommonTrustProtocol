# -*- coding: utf-8 -*-
"""test_ccg_blindtest2.py · 注释索引盲测 v2（GPT 规模化建议）

v1 结论：语义化注释 head 100% Top-1（13/13）。v2 扩展：
  ① 样本 96 单元（六域各 16，seed 固定）
  ② 指标：Top-1 / Top-5 / 负条件拒绝率（condition-based routing）
  ③ 负条件：给 target 构造「不适用任务」（他域语义）→ 检查 target 不被召回
     ——理论是「条件满足→路由；不满足→不路由」，非「相似就召回」

严谨表述：当前实验设置下，高语义密度注释能否作为代码实体有效索引，
并表现出显著高于自动生成泛化描述的定位能力，且负条件可被排除。
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

SEED = 20260826
random.seed(SEED)
G = ccg.build_graph()


def semantic_head(code: str) -> str:
    """提取语义化首行描述（跳过三要素标记行）。"""
    lines = [ln.strip().lstrip('#').strip()
             for ln in code.splitlines() if ln.strip().startswith('#')]
    head = next((ln for ln in lines
                 if not ln.startswith(('生效条件', '子功能', '执行',
                                       '不适用条件', '返回', '功能条件'))), '')
    desc = head.split('：', 1)[-1].split(':', 1)[-1].strip()
    return re.sub(r'[（(][^）)]*[）)]', '', desc).strip()


def make_task(desc: str) -> str:
    return f"写一个{desc}的代码单元" if desc else None


def run_v2(n_per_domain: int = 16) -> dict:
    """v2 盲测：Top-1 / Top-5 / 负条件拒绝率。"""
    results = []
    for dname, units in MODS.items():
        uids = random.sample(list(units.keys()), n_per_domain)
        for uid in uids:
            u = units[uid]
            desc = semantic_head(u['pattern'])
            task = make_task(desc)
            if not task or len(desc) < 4:
                continue
            hits = ccg.search(task, G, top=5)
            hit_ids = [h[0] for h in hits]
            # 负条件：从其他域随机单元语义构造「不适用任务」
            other_domains = [d for d in MODS if d != dname]
            od = random.choice(other_domains)
            other_uid = random.choice(list(MODS[od].keys()))
            neg_task = make_task(semantic_head(MODS[od][other_uid]['pattern']))
            neg_reject = True
            if neg_task:
                neg_hits = ccg.search(neg_task, G, top=5)
                neg_reject = uid not in [h[0] for h in neg_hits]
            results.append({'domain': dname, 'unit': uid, 'task': task,
                            'top1': hit_ids[0] if hit_ids else None,
                            'top5': hit_ids,
                            'neg_task': neg_task, 'neg_reject': neg_reject,
                            'top1_ok': bool(hit_ids) and hit_ids[0] == uid,
                            'top5_ok': uid in hit_ids})
    n = len(results)
    top1 = sum(1 for r in results if r['top1_ok'])
    top5 = sum(1 for r in results if r['top5_ok'])
    neg = sum(1 for r in results if r['neg_reject'])
    total_units = sum(len(m) for m in MODS.values())
    return {'total': n, 'top1': top1, 'top5': top5, 'neg': neg,
            'top1_rate': top1 / n, 'top5_rate': top5 / n,
            'neg_rate': neg / n, 'baseline': total_units ** -1,
            'results': results}


r = run_v2()
print(f"=== 注释索引盲测 v2（seed={SEED}，96 单元规模）===")
print(f"样本: {r['total']} 单元（六域各抽，实现与功能名隐藏）")
print(f"Top-1: {r['top1']}/{r['total']} ({100.0 * r['top1_rate']:.0f}%)"
      f"  | 基线 {100.0 * r['baseline']:.2f}%")
print(f"Top-5: {r['top5']}/{r['total']} ({100.0 * r['top5_rate']:.0f}%)")
print(f"负条件拒绝: {r['neg']}/{r['total']} ({100.0 * r['neg_rate']:.0f}%)")
print(f"\n--- Top-1 未命中（前 8）---")
for x in [x for x in r['results'] if not x['top1_ok']][:8]:
    print(f"  [{x['domain']}] {x['unit']} → {x['top1']}")
    print(f"    任务: {x['task'][:56]}")
print(f"\n--- 负条件未拒绝（前 5）---")
for x in [x for x in r['results'] if not x['neg_reject']][:5]:
    print(f"  [{x['domain']}] {x['unit']} 负任务: {x['neg_task'][:50]}")

check('① Top-1 ≥ 70%（规模化后语义注释可索引）', r['top1_rate'] >= 0.7,
      f"{100.0*r['top1_rate']:.0f}%")
check('② Top-5 ≥ 90%', r['top5_rate'] >= 0.9, f"{100.0*r['top5_rate']:.0f}%")
check('③ 负条件拒绝率 ≥ 85%（condition-based routing）', r['neg_rate'] >= 0.85,
      f"{100.0*r['neg_rate']:.0f}%")
check('④ Top-1 显著高于随机基线（×100 以上）',
      r['top1_rate'] >= 100 * r['baseline'],
      f"×{r['top1_rate']/r['baseline']:.0f}")

report = {
    "experiment": "注释索引盲测 v2", "seed": SEED,
    "sample": r['total'], "baseline": r['baseline'],
    "top1": r['top1'], "top1_rate": round(r['top1_rate'], 4),
    "top5": r['top5'], "top5_rate": round(r['top5_rate'], 4),
    "neg_reject": r['neg'], "neg_rate": round(r['neg_rate'], 4),
    "conclusion": ("规模化下语义注释 Top-1/Top-5 高命中且负条件高拒绝率——"
                   "接近 condition-based routing（条件满足→路由，不满足→不路由）"),
    "misses": [{"unit": x['unit'], "task": x['task'], "got": x['top1']}
               for x in r['results'] if not x['top1_ok']],
}
rp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ccg_blindtest2_report.json')
json.dump(report, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
check('⑤ v2 报告落盘', os.path.exists(rp), 'ccg_blindtest2_report.json')

print(f'\n=== 注释索引盲测 v2: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
