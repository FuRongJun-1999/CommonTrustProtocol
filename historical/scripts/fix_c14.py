# -*- coding: utf-8 -*-
"""c14 修复：①_assemble 的 _long 过滤去掉 len>=2（REVERSE_DAILY 即白名单，
单字 key 仅 饿/波 两个，放宽无误伤——此前「什么是波」encode 产出『波』被 len>=2 过滤致 fp 不触发）
②补「声音不能传播」触发词（太空问法）"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

# ---- 1. chat_engine.py ----
CE = r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\chat_engine.py'
ce_src = open(CE, encoding='utf-8').read()
old = '_long = [t for t in _fp if len(t) >= 2 and t in _st.REVERSE_DAILY]'
new = ('_long = [t for t in _fp if t in _st.REVERSE_DAILY]\n'
       '            # c14：去掉 len>=2 过滤——REVERSE_DAILY 本身是白名单，单字 key\n'
       '            # 仅 饿/波 两个，「什么是波」encode 产出『波』此前被 len>=2 过滤\n'
       '            # 致 fp 直答不触发（单字误伤由 encode 的 SINGLE_CHAR_EXCLUDE 负责）')
if old in ce_src:
    ce_src = ce_src.replace(old, new)
    open(CE, 'w', encoding='utf-8').write(ce_src)
    print('[1] chat_engine _long 过滤已放宽')
else:
    print('[1] !! 未找到 _long 过滤行，检查实际代码')
    for m in re.finditer(r'_long = .*', ce_src):
        print('  现有:', m.group(0)[:100])

# ---- 2. semantic_translate.py 补触发词 ----
SRC = r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py'
src = open(SRC, encoding='utf-8').read()
NEW_TRIGGERS = {
    '声音不能传播': ['太空', '听不到声音', '为什么太空听不到声音', '太空没有声音',
                 '为什么太空中没有声音', '真空中为什么没声音', '月球听不到声音', '宇宙没有声音'],
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
src = ''.join(out)
open(SRC, 'w', encoding='utf-8').write(src)
for k, old_n, new_n in changed:
    print(f'[2] OK {k}: 触发词 {old_n} -> {new_n}')
