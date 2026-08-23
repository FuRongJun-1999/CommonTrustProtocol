# -*- coding: utf-8 -*-
"""查看 7 个 MISS key 的 DOMAIN 触发词定义 + _assemble 匹配逻辑"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.semantic_translate as st

miss_keys = ['下雨打伞','晚上睡觉','烧水去氯','冬天穿衣','洗澡降温','吃早饭','垃圾入桶']
print('=== DOMAIN_SYNONYM_CLUSTERS 触发词 ===')
for k in miss_keys:
    d = st.DOMAIN_SYNONYM_CLUSTERS.get(k)
    s = st.SYNONYM_CLUSTERS.get(k)
    print(f'{k}: DOMAIN={d} SYNONYM={s}')

# _assemble 匹配逻辑
src = open(r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\chat_engine.py', encoding='utf-8').read()
i = src.find('def _assemble')
print('=== _assemble 签名与匹配段 ===')
print(src[i:i+2500])
