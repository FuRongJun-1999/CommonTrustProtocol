# -*- coding: utf-8 -*-
"""c13 触发词补丁 3：v62 3 个反题错题补触发词"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

SRC = r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py'
src = open(SRC, encoding='utf-8').read()

NEW_TRIGGERS = {
    '一年月数': ['2月', '28天', '二月', '2月28天', '为什么2月只有28天', '为什么二月短'],
    '一周天数': ['星期', '星期怎么来', '星期几', '为什么叫星期', '一周为什么7天', '周一到周日'],
    '天空蓝色': ['傍晚', '天空变红', '晚霞', '为什么傍晚天空变红', '傍晚天为什么红', '朝霞'],
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
