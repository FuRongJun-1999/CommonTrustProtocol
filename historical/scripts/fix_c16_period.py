# -*- coding: utf-8 -*-
"""周期触发词补丁（variant_checker 预警缺口 + v65 测试 2 错题）"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
SRC = r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py'
src = open(SRC, encoding='utf-8').read()

# 确认当前触发词
import wisdom.semantic_translate as st
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import importlib
importlib.reload(st)
print('周期当前触发词:', st.DOMAIN_SYNONYM_CLUSTERS.get('周期'))

NEW = ['周期有什么用', '周期作用', '周期的用处', '周期是干嘛的',
       '没有周期会怎样', '没有周期怎么办', '周期没了',
       '周期是怎么来的', '周期的原理', '周期规律', '周期现象']

lines = src.splitlines(keepends=True)
out = []
changed = False
i = 0
while i < len(lines):
    ln = lines[i]
    m = re.match(r'^(\s*)"周期"\s*:\s*\[', ln)
    if m:
        buf = ln
        j = i + 1
        while ']' not in buf and j < len(lines):
            buf += lines[j]
            j += 1
        elems = re.findall(r'"([^"]+)"', buf)
        add = [t for t in NEW if t not in elems]
        if add:
            indent = m.group(1)
            newbuf = indent + '"周期": ['
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
            changed = True
            print(f'周期触发词: {len(elems)} -> {len(all_elems)}')
            continue
    out.append(ln)
    i += 1

if changed:
    open(SRC, 'w', encoding='utf-8').write(''.join(out))
    print('已写入')
else:
    print('无变更或未找到')
