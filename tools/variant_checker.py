# -*- coding: utf-8 -*-
"""variant_checker.py · 问法变异器 + 触发词预检（反思单元落地 · 自迭代机制工程化阶段2）
理论：条件论七操作（逆转=反题/组合=合题/循环=复合条件）→ 问法变异；
反思单元预测生成（§3.1）→ 变异候选；验证单元确定性检查 → 触发词覆盖预检。
命令：
  variant_checker.py --audit                全部已升级簇的触发词覆盖预检（输出缺口清单）
  variant_checker.py --check <簇1,簇2>      指定簇预检
  variant_checker.py --replay <json>        历史错题回溯：检查给定问法当前是否命中（补丁一致性验证）
"""
import sys, os, json, re, argparse
sys.stdout.reconfigure(encoding='utf-8')

SITE = r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages'
KB = r'D:\Program Files\2_ai\knowledge-base'
LEDGER = r'D:\Program Files\2_ai\CommonTrustProtocol\ledger\evolution_ledger.json'

# 问法模板族（正/反/合/复合——条件论七操作）
TEMPLATES = [
    # 正题（声明条件）
    ('正题', '什么是{x}'),
    ('正题', '{x}是什么'),
    ('正题', '为什么{x}'),
    ('正题', '{x}是怎么来的'),
    ('正题', '{x}的原理是什么'),
    # 反题（逆转条件）
    ('反题', '{x}能…吗'),
    ('反题', '没有{x}会怎样'),
    ('反题', '是不是{x}就…'),
    ('反题', '别以为{x}…'),
    ('反题', '没有{x}怎么办'),
    # 合题（组合条件）
    ('合题', '{x}有什么用'),
    ('合题', '怎么用{x}'),
    ('合题', '{x}要注意什么'),
    ('合题', '{x}错了会怎样'),
    ('合题', '怎么提高{x}'),
]


def load_semantic():
    sys.path.insert(0, SITE)
    import wisdom.semantic_translate as st
    import importlib
    importlib.reload(st)
    return st


def fp_hits(st, text):
    """fp 确定性直答命中：encode 产出的 token 中在 REVERSE_DAILY 的"""
    try:
        enc = st.encode(text)
        return [t for t in enc if t in st.REVERSE_DAILY]
    except Exception:
        return []


def gen_variants(key, cond_hints=None):
    """生成问法变体（含复合条件：X在C条件下会怎样）"""
    vs = []
    for stage, tpl in TEMPLATES:
        v = tpl.format(x=key)
        vs.append((stage, v))
    # 复合条件（递归路由深度≥2）：用条件线索
    for c in (cond_hints or []):
        vs.append(('复合', f'{key}在{c}条件下会怎样'))
        vs.append(('复合', f'为什么{c}时{key}'))
    return vs


def check_cluster(st, key, cond_hints=None):
    """检查一簇：生成变体 → 触发词覆盖预检 → 缺口清单"""
    gaps = []
    for stage, v in gen_variants(key, cond_hints):
        hits = fp_hits(st, v)
        if key not in hits:
            other = [h for h in hits if h != key][:3]
            gaps.append({'variant': v, 'stage': stage, 'hits': other})
    return gaps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--audit', action='store_true')
    ap.add_argument('--check', type=str, default='')
    ap.add_argument('--replay', type=str, default='')
    args = ap.parse_args()

    st = load_semantic()
    ledger = json.load(open(LEDGER, encoding='utf-8'))['entries']

    if args.replay:
        # 历史错题回溯：加载错题 JSON [{q, domain}], 检查当前命中
        items = json.load(open(args.replay, encoding='utf-8'))
        ok = miss = 0
        for it in items:
            hits = fp_hits(st, it['q'])
            dom = it.get('domain', it.get('theme', ''))
            hit_ok = dom in hits or (hits and dom in str(hits))
            if hit_ok:
                ok += 1
                print(f'  OK  {it["q"]} -> {hits[:3]}')
            else:
                miss += 1
                print(f'  MISS {it["q"]} -> {hits[:3]} (期望 {dom})')
        print(f'历史回溯: {ok}/{len(items)} 命中')
        return

    if args.check:
        keys = [k.strip() for k in args.check.split(',') if k.strip()]
    else:
        keys = [k for k, e in ledger.items() if e['upgraded']]

    total_gaps = 0
    for key in sorted(keys):
        e = ledger.get(key, {})
        gaps = check_cluster(st, key, e.get('condition_hints'))
        if gaps:
            total_gaps += len(gaps)
            print(f'== {key} ({len(gaps)} 缺口):')
            for g in gaps[:8]:
                print(f'  [{g["stage"]}] {g["variant"]} -> hits={g["hits"]}')
        else:
            print(f'== {key}: 全覆盖 ✓')
    print(f'\n预检完成: {len(keys)} 簇, {total_gaps} 个问法变体缺口')


if __name__ == '__main__':
    main()
