# -*- coding: utf-8 -*-
"""深挖：一天小时 encode 空 + DOMAIN_ROUTE 现状"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.semantic_translate as st
import importlib
importlib.reload(st)

# DOMAIN_ROUTE line 1255 现状
src = open(r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py', encoding='utf-8').read()
lines = src.splitlines()
for i in range(1250, 1260):
    print(f'{i+1}: {lines[i][:80]}')

print()
print('DOMAIN_SYNONYM_CLUSTERS[一天小时]:', st.DOMAIN_SYNONYM_CLUSTERS.get('一天小时'))
print('ALL_TABLE 含 一天有多少小时:', '一天有多少小时' in st.ALL_TABLE)
print('ALL_TABLE 含 一天几个小时:', '一天几个小时' in st.ALL_TABLE)
print('ALL_TABLE 含 一年有多少个月:', '一年有多少个月' in st.ALL_TABLE)
# 直接手工模拟 encode
t = '一天有多少个小时？'
hits = []
for phrase, term in st.ALL_TABLE.items():
    if phrase in t:
        hits.append((phrase, term))
print('手工匹配 一天有多少个小时？:', hits[:10])
t2 = '为什么一年有12个月？'
hits2 = [(p, te) for p, te in st.ALL_TABLE.items() if p in t2]
print('手工匹配 为什么一年有12个月？:', hits2[:10])
