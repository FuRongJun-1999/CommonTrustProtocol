# -*- coding: utf-8 -*-
"""ledger.py 前置检查：确认 semantic_translate.py 可解析结构（四表 + 条件词）"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.semantic_translate as st
import importlib
importlib.reload(st)

src = open(r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py', encoding='utf-8').read()

print('REVERSE_DAILY keys:', len(st.REVERSE_DAILY))
print('DOMAIN_SYNONYM_CLUSTERS keys:', len(st.DOMAIN_SYNONYM_CLUSTERS))
print('SYNONYM_CLUSTERS keys:', len(st.SYNONYM_CLUSTERS))
print('DOMAIN_ROUTE keys:', len(st.DOMAIN_ROUTE))

# 测试结果文件（trust 来源）
import os, glob
kb = r'D:\Program Files\2_ai\knowledge-base'
res = sorted(glob.glob(os.path.join(kb, 'conflict_testset_v*_results.json')))
print('测试结果文件:', len(res), '个')
if res:
    import json
    d = json.load(open(res[-1], encoding='utf-8'))
    print('最新 results 结构:', list(d.keys()))
    if d.get('results'):
        print('首条:', {k: d['results'][0].get(k) for k in ['domain', 'bad', 'route']})

# 条件词来源：_cond_guard 与触发词中的条件词
print('_cond_guard 检查:', '潜水' in src and '深海' in src)
