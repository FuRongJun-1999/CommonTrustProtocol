# -*- coding: utf-8 -*-
"""auto_blind_fix.py · 自动补盲（反思单元变异 → 触发词自动补丁）
读取 variant_checker 预检缺口 → 提取自然问法变体（非省略号模板）→ 自动并入触发词 → 五副本同步
命令：
  auto_blind_fix.py --all        全部已升级簇自动补盲
  auto_blind_fix.py --check 簇   指定簇补盲
"""
import sys, os, re, argparse, shutil, hashlib
sys.stdout.reconfigure(encoding='utf-8')

SITE = r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages'
SRC = os.path.join(SITE, r'wisdom\semantic_translate.py')
COPIES = [
    r'D:\Program Files\2_ai\knowledge-base\semantic_translate.py',
    r'D:\Program Files\2_ai\CommonTrustProtocol\aeis\wisdom\semantic_translate.py',
    r'D:\Program Files\1_ai\lingshu-wisdom\wisdom\semantic_translate.py',
    r'D:\Program Files\3_ai\lingshu-wisdom\wisdom\semantic_translate.py',
]
LEDGER = r'D:\Program Files\2_ai\CommonTrustProtocol\ledger\evolution_ledger.json'

# 可自动补的稳定模板（自然问法；省略号模板跳过）
AUTO_TEMPLATES = ['什么是{x}', '{x}是什么', '为什么{x}', '{x}是怎么来的',
                  '{x}的原理是什么', '{x}有什么用', '没有{x}会怎样', '没有{x}怎么办']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--check', type=str, default='')
    args = ap.parse_args()

    sys.path.insert(0, SITE)
    import wisdom.semantic_translate as st
    import importlib
    importlib.reload(st)
    import variant_checker as vc

    if args.check:
        keys = [k.strip() for k in args.check.split(',') if k.strip()]
    else:
        ledger = json.load(open(LEDGER, encoding='utf-8'))['entries']
        keys = [k for k, e in ledger.items() if e['upgraded']]

    # 收集每簇缺口（只保留 AUTO_TEMPLATES 生成的变体）
    plan = {}   # key -> [触发词候选]
    for key in sorted(keys):
        e = {}
        if os.path.exists(LEDGER):
            ledger = json.load(open(LEDGER, encoding='utf-8'))['entries']
            e = ledger.get(key, {})
        cond = e.get('condition_hints') if e else None
        for stage, tpl in vc.TEMPLATES:
            if tpl not in AUTO_TEMPLATES:
                continue
            variant = tpl.format(x=key)
            hits = vc.fp_hits(st, variant)
            if key not in hits:
                # 触发词候选 = 变体本身（连续子串匹配：用户这样问就能命中）
                if len(variant) <= 10:
                    plan.setdefault(key, []).append(variant)

    # 应用补丁（并入 DOMAIN_SYNONYM_CLUSTERS 触发词）
    src = open(SRC, encoding='utf-8').read()
    lines = src.splitlines(keepends=True)
    out = []
    changed = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        m = re.match(r'^(\s*)"([^"]+)"\s*:\s*\[', ln)
        if m and m.group(2) in plan:
            key = m.group(2)
            buf = ln
            j = i + 1
            while ']' not in buf and j < len(lines):
                buf += lines[j]
                j += 1
            elems = re.findall(r'"([^"]+)"', buf)
            add = [t for t in plan[key] if t not in elems]
            if add:
                indent = m.group(1)
                newbuf = indent + '"' + key + '": ['
                all_elems = elems + add
                rows = [all_elems[k:k+5] for k in range(0, len(all_elems), 5)]
                for r_i, row in enumerate(rows):
                    if r_i == 0:
                        newbuf += ', '.join('"' + e2 + '"' for e2 in row)
                    else:
                        newbuf = newbuf.rstrip() + ',\n' + indent + '    ' + ', '.join('"' + e2 + '"' for e2 in row)
                newbuf += '],\n'
                out.append(newbuf)
                i = j
                changed.append((key, len(elems), len(all_elems), add))
                continue
        out.append(ln)
        i += 1

    if not changed:
        print('无自动补盲变更')
        return
    open(SRC, 'w', encoding='utf-8').write(''.join(out))

    # 五副本同步
    h0 = hashlib.sha256(open(SRC, 'rb').read()).hexdigest()[:12]
    for c in COPIES:
        shutil.copy2(SRC, c)
    print(f'自动补盲完成: {len(changed)} 簇, 五副本同步 [{h0}]')
    for k, old_n, new_n, add in changed:
        print(f'  {k}: 触发词 {old_n} -> {new_n} +{add}')


if __name__ == '__main__':
    import json
    main()
