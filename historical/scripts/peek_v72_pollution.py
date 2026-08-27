# -*- coding: utf-8 -*-
"""检查 DOMAIN_ROUTE 污染范围：16 个环境 key 的 DOMAIN_ROUTE 行现状"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
src = open(r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py', encoding='utf-8').read()
lines = src.splitlines()

keys = ['碳中和','碳达峰','温室效应','全球变暖','碳排放','温室气体','气候变化','新能源',
        '可再生能源','光伏','风力发电','电动汽车','锂电池','储能','绿色能源','双碳']
for i, ln in enumerate(lines):
    for k in keys:
        if re.search('"' + k + r'"\s*:\s*"', ln) and len(ln) > 60:
            print(f'line {i+1} [{k}]: {ln[:80]}...')
            break
