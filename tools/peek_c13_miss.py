# -*- coding: utf-8 -*-
"""诊断 c13 5 个 MISS：encode 产出 + 应力旧答案位置"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.semantic_translate as st
import importlib
importlib.reload(st)

qs = {
    '为什么一年有12个月？': '一年月数',
    '一天有多少个小时？': '一天小时',
    '什么是应力？': '应力',
    '为什么混凝土要加钢筋？': '混凝土钢筋',
    '为什么声音需要介质？': '介质',
    '一周有几天？': '一周天数',
}
for q, expect in qs.items():
    enc = st.encode(q)
    rd_hits = [t for t in enc if len(t) >= 2 and t in st.REVERSE_DAILY]
    print(f'{q}')
    print(f'  encode: {list(enc.keys())}')
    print(f'  RD 命中: {rd_hits}')

# 应力旧答案位置
src = open(r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py', encoding='utf-8').read()
lines = src.splitlines()
for i, ln in enumerate(lines):
    if '物体单位面积上承受的内力叫应力' in ln:
        print(f'应力旧答案 line {i+1}: {ln[:100]}')
