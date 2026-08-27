# -*- coding: utf-8 -*-
"""状态匹配 补触发词（variant_checker 模式：自然问法）"""
import sys, re, shutil, hashlib
sys.stdout.reconfigure(encoding='utf-8')
SRC = r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py'
src = open(SRC, encoding='utf-8').read()

ADD = ['匹配目标', '怎么让物体匹配目标', '物体怎么匹配目标', '目标状态', '怎么达成目标状态', '状态怎么匹配']

lines = src.splitlines(keepends=True)
out = []
i = 0
done = False
while i < len(lines):
    ln = lines[i]
    m = re.match(r'^(\s*)"状态匹配"\s*:\s*\[', ln)
    if m:
        buf = ln
        j = i + 1
        while ']' not in buf and j < len(lines):
            buf += lines[j]
            j += 1
        elems = re.findall(r'"([^"]+)"', buf)
        add = [t for t in ADD if t not in elems]
        if add:
            indent = m.group(1)
            newbuf = indent + '"状态匹配": ['
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
            done = True
            print(f'状态匹配触发词: {len(elems)} -> {len(all_elems)}')
            continue
    out.append(ln)
    i += 1

if done:
    open(SRC, 'w', encoding='utf-8').write(''.join(out))
    COPIES = [r'D:\Program Files\2_ai\knowledge-base\semantic_translate.py',
              r'D:\Program Files\2_ai\CommonTrustProtocol\aeis\wisdom\semantic_translate.py',
              r'D:\Program Files\1_ai\lingshu-wisdom\wisdom\semantic_translate.py',
              r'D:\Program Files\3_ai\lingshu-wisdom\wisdom\semantic_translate.py']
    for c in COPIES:
        shutil.copy2(SRC, c)
    print('五副本同步 OK')
else:
    print('未找到状态匹配簇')
