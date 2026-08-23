# -*- coding: utf-8 -*-
"""查 应力/短路/混凝土钢筋 3 处定义的具体位置与内容"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
src = open(r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py', encoding='utf-8').read()
lines = src.splitlines()

for k in ['应力', '短路', '混凝土钢筋']:
    print(f'=== {k} ===')
    for i, ln in enumerate(lines):
        if re.search('"' + re.escape(k) + r'"\s*:', ln):
            print(f'  line {i+1}: {ln[:150]}')
