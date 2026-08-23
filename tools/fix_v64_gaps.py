# -*- coding: utf-8 -*-
"""v64 错题修复：负反馈/贝叶斯推断 补触发词（variant_checker 预检驱动的补丁）
覆盖：①v64 2 个错题问法 ②variant_checker 预检出的模板缺口"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

SRC = r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py'
src = open(SRC, encoding='utf-8').read()

NEW_TRIGGERS = {
    '负反馈': [
        # v64 错题问法 + variant_checker 模板缺口
        '生活里有哪些负反馈', '负反馈的例子', '生活中的负反馈', '负反馈有哪些',
        '负反馈在生活', '恒温器', '空调怎么恒温',
        '为什么负反馈', '负反馈怎么来的', '负反馈的原理', '负反馈能',
        '没有负反馈会怎样', '没有负反馈怎么办', '负反馈有什么用', '怎么用负反馈',
        '负反馈要注意', '负反馈错了会怎样', '负反馈作用',
    ],
    '贝叶斯推断': [
        # v64 错题问法（下位概念，不含 key）
        '检测阳性', '阳性就一定有病', '假阳性', '阳性说明什么', '检测准确率',
        '阳性率', '体检阳性',
    ],
}

lines = src.splitlines(keepends=True)
out = []
changed = []
i = 0
while i < len(lines):
    ln = lines[i]
    m = re.match(r'^(\s*)"([^"]+)"\s*:\s*\[', ln)
    if m and m.group(2) in NEW_TRIGGERS:
        key = m.group(2)
        buf = ln
        j = i + 1
        while ']' not in buf and j < len(lines):
            buf += lines[j]
            j += 1
        elems = re.findall(r'"([^"]+)"', buf)
        add = [t for t in NEW_TRIGGERS[key] if t not in elems]
        if add:
            indent = m.group(1)
            newbuf = indent + '"' + key + '": ['
            all_elems = elems + add
            rows = [all_elems[k:k+5] for k in range(0, len(all_elems), 5)]
            for r_i, row in enumerate(rows):
                if r_i == 0:
                    newbuf += ', '.join('"' + e + '"' for e in row)
                else:
                    newbuf = newbuf.rstrip() + ',\n' + indent + '    ' + ', '.join('"' + e + '"' for e in row)
            newbuf += '],\n'
            out.append(newbuf)
            i = j
            changed.append((key, len(elems), len(all_elems)))
            continue
    out.append(ln)
    i += 1

open(SRC, 'w', encoding='utf-8').write(''.join(out))
for k, old_n, new_n in changed:
    print(f'OK {k}: 触发词 {old_n} -> {new_n}')
if not changed:
    print('无变更')
