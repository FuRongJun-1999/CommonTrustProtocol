# -*- coding: utf-8 -*-
"""ALL_TABLE 构建来源 + 触发词是否进入 ALL_TABLE"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
src = open(r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py', encoding='utf-8').read()

for pat in ['ALL_TABLE', 'PHRASE_TABLE']:
    i = src.find(pat + ' =')
    print(f'=== {pat} 定义 @ {i} ===')
    if i >= 0:
        print(src[i:i+1200])
