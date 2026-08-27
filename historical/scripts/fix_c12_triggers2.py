# -*- coding: utf-8 -*-
"""c12 触发词补丁 2：6 个 v61 错题（反题/合题问法）补触发词
纪律：触发词必须是问法里的连续子串"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

SRC = r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py'
src = open(SRC, encoding='utf-8').read()

NEW_TRIGGERS = {
    '下雨打伞': ['伞为什么能挡雨','为什么伞能挡雨','伞能挡住雨','能挡住雨','雨伞为什么','伞为什么能挡住雨'],
    '晚上睡觉': ['睡多久','睡多长时间','睡眠时长','睡几个小时','睡几小时','睡眠时间'],
    '开水晾凉': ['太烫的水','喝太烫','水太烫','喝烫水','烫水'],
    '烧水去氯': ['烧水能去掉','水烧开能去掉','烧水去什么','水烧开去','烧开去掉'],
    '蔬果营养': ['果汁','代替水果','果汁能代替','果汁代替水果','鲜榨果汁'],
    '节水节电': ['待机','待机耗电','待机也耗电','待机也费电','电器待机'],
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
