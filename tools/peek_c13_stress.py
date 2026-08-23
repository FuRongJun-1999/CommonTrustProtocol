# -*- coding: utf-8 -*-
"""排查：①chat_engine.py 里的应力旧答案 ②DOMAIN_TABLE 是否含一天小时触发词 ③RD['应力'] 当前值"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

# 1. chat_engine.py 与 wisdom 目录全部 .py 搜应力旧答案
import os
roots = [r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom',
         r'D:\Program Files\2_ai\knowledge-base']
for root in roots:
    for fn in os.listdir(root):
        if not fn.endswith('.py'): continue
        p = os.path.join(root, fn)
        src = open(p, encoding='utf-8').read()
        if '物体单位面积上承受的内力叫应力' in src:
            i = src.find('物体单位面积上承受的内力叫应力')
            ln = src[:i].count('\n') + 1
            print(f'FOUND {p}:{ln}')
        # 也搜「应力」短答案（16ch 带句号版本在 chat_engine?）
        for m in re.finditer(r'"应力"\s*:\s*"([^"]{5,40})"', src):
            print(f'  {p} 应力key: {m.group(1)[:40]!r}')

# 2. DOMAIN_TABLE 检查
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.semantic_translate as st
import importlib
importlib.reload(st)
dt = st.DOMAIN_TABLE
for k in ['一天有多少小时', '一天几个小时', '一年有多少个月', '一周有几天']:
    print(f'DOMAIN_TABLE[{k!r}] = {dt.get(k)}')
print('RD[应力] len:', len(st.REVERSE_DAILY.get('应力', '')))
print('RD[应力] head:', st.REVERSE_DAILY.get('应力', '')[:60])
print('RD[一天小时] len:', len(st.REVERSE_DAILY.get('一天小时', '')))
