# -*- coding: utf-8 -*-
"""ledger.py · 进化台账（记录单元落地 · 自迭代机制工程化阶段1）
解析 semantic_translate.py 四表 + 测试结果 → 持久化进化台账 JSON
命令：
  ledger.py --refresh   重建台账（解析语义文件 + 测试结果）
  ledger.py --thin      薄簇清单（<80 字，待升级）
  ledger.py --gaps      条件路由缺口（有答案无条件 / 有条件无答案）
  ledger.py --trust     信任衰减复审队列（p_trust 低/无验证的已升级簇）
"""
import sys, os, json, re, argparse
sys.stdout.reconfigure(encoding='utf-8')

SITE = r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages'
SRC = os.path.join(SITE, r'wisdom\semantic_translate.py')
KB = r'D:\Program Files\2_ai\knowledge-base'
LEDGER_DIR = r'D:\Program Files\2_ai\CommonTrustProtocol\ledger'
LEDGER = os.path.join(LEDGER_DIR, 'evolution_ledger.json')

THIN_THRESHOLD = 80      # 薄答案阈值（字）
UPGRADED_THRESHOLD = 800 # 已升级答案阈值（字，c 系列完整直答均 >800）

# 条件词（从触发词/答案中识别条件路由链线索）
CONDITION_WORDS = ['高原', '海拔', '气压', '真空', '低温', '高温', '潮湿', '干燥',
                   '冬天', '夏天', '雨天', '夜间', '空腹', '饭后', '运动后', '睡前',
                   '过热', '过冷', '超载', '缺水', '高压', '低压', '深海', '潜水']


def load_semantic():
    sys.path.insert(0, SITE)
    import wisdom.semantic_translate as st
    import importlib
    importlib.reload(st)
    return st


def load_test_stats():
    """从 conflict_testset_v*_results.json 统计每簇测试覆盖（p_trust 语义）"""
    import glob
    stats = {}
    for path in sorted(glob.glob(os.path.join(KB, 'conflict_testset_v*_results.json'))):
        try:
            d = json.load(open(path, encoding='utf-8'))
        except Exception:
            continue
        ver = os.path.basename(path).replace('conflict_testset_', '').replace('_results.json', '')
        for r in d.get('results', []):
            dom = r.get('domain', '')
            if not dom:
                continue
            s = stats.setdefault(dom, {'tests': 0, 'bad': 0, 'versions': []})
            s['tests'] += 1
            if r.get('bad'):
                s['bad'] += 1
            if ver not in s['versions']:
                s['versions'].append(ver)
    return stats


def build_ledger(st, stats):
    ledger = {}
    for key, answer in st.REVERSE_DAILY.items():
        dom = st.DOMAIN_ROUTE.get(key, '')
        triggers = list(st.DOMAIN_SYNONYM_CLUSTERS.get(key, [])) + \
                   list(st.SYNONYM_CLUSTERS.get(key, []))
        # 触发词中的条件线索（条件路由链的初步线索）
        cond_hints = [t for t in triggers if any(w in t for w in CONDITION_WORDS)]
        tstat = stats.get(key, {'tests': 0, 'bad': 0, 'versions': []})
        p_trust = round(1.0 - tstat['bad'] / tstat['tests'], 3) if tstat['tests'] else None
        ledger[key] = {
            'domain': dom,
            'rd_len': len(answer),
            'trigger_count': len(triggers),
            'condition_hints': cond_hints,
            'upgraded': len(answer) >= UPGRADED_THRESHOLD,
            'p_trust': p_trust,
            'test_versions': tstat['versions'],
            'change_log': [],   # 变更日志（记录单元·不可静默修改）
            'status': 'upgraded' if len(answer) >= UPGRADED_THRESHOLD else 'pending',
        }
    # 触发词簇中无 REVERSE_DAILY 答案的（有条件无答案）
    for key in list(st.DOMAIN_SYNONYM_CLUSTERS.keys()) + list(st.SYNONYM_CLUSTERS.keys()):
        if key not in ledger:
            triggers = list(st.DOMAIN_SYNONYM_CLUSTERS.get(key, [])) + \
                       list(st.SYNONYM_CLUSTERS.get(key, []))
            ledger[key] = {
                'domain': st.DOMAIN_ROUTE.get(key, ''),
                'rd_len': 0,
                'trigger_count': len(triggers),
                'condition_hints': [],
                'upgraded': False,
                'p_trust': None,
                'test_versions': [],
                'change_log': [],
                'status': 'no_answer',
            }
    return ledger


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--refresh', action='store_true')
    ap.add_argument('--thin', action='store_true')
    ap.add_argument('--gaps', action='store_true')
    ap.add_argument('--trust', action='store_true')
    args = ap.parse_args()

    os.makedirs(LEDGER_DIR, exist_ok=True)
    if args.refresh or not os.path.exists(LEDGER):
        st = load_semantic()
        stats = load_test_stats()
        ledger = build_ledger(st, stats)
        with open(LEDGER, 'w', encoding='utf-8') as f:
            json.dump({'version': 1, 'entries': ledger}, f, ensure_ascii=False, indent=1)
        print(f'台账已重建: {len(ledger)} 簇 (LEDGER: {LEDGER})')
        print(f'  已升级(>={UPGRADED_THRESHOLD}字): {sum(1 for e in ledger.values() if e["upgraded"])}')
        print(f'  薄簇(<{THIN_THRESHOLD}字): {sum(1 for e in ledger.values() if 0 < e["rd_len"] < THIN_THRESHOLD)}')
        print(f'  无条件答案簇(no_answer): {sum(1 for e in ledger.values() if e["status"] == "no_answer")}')
        return

    ledger = json.load(open(LEDGER, encoding='utf-8'))['entries']

    if args.thin:
        thin = [(k, e['rd_len'], e['domain']) for k, e in ledger.items()
                if 0 < e['rd_len'] < THIN_THRESHOLD]
        thin.sort(key=lambda x: x[1])
        print(f'薄簇清单 (<{THIN_THRESHOLD}字): {len(thin)}')
        for k, n, d in thin:
            print(f'  {k}: {n}ch domain={d or "?"}')

    if args.gaps:
        # 有条件无答案：触发词在但无答案
        no_ans = [(k, e['trigger_count']) for k, e in ledger.items() if e['status'] == 'no_answer']
        no_ans.sort(key=lambda x: -x[1])
        print(f'条件路由缺口·有条件无答案: {len(no_ans)}')
        for k, t in no_ans[:30]:
            print(f'  {k}: {t} 触发词')
        # 有答案无条件链：已升级但 condition_hints 空（条件链线索缺失）
        no_cond = [(k, e['rd_len']) for k, e in ledger.items()
                   if e['upgraded'] and not e['condition_hints']]
        print(f'条件路由缺口·有答案无条件链线索: {len(no_cond)}')

    if args.trust:
        # 已升级但无测试覆盖 或 p_trust < 0.95 的
        queue = []
        for k, e in ledger.items():
            if not e['upgraded']:
                continue
            if e['p_trust'] is None:
                queue.append((k, None, '无测试覆盖'))
            elif e['p_trust'] < 0.95:
                queue.append((k, e['p_trust'], f"p_trust={e['p_trust']}"))
        print(f'信任复审队列 (已升级但验证不足): {len(queue)}')
        for k, p, why in sorted(queue, key=lambda x: (x[1] if x[1] is not None else -1))[:40]:
            print(f'  {k}: {why}')


if __name__ == '__main__':
    main()
