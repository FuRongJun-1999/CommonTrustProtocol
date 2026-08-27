# -*- coding: utf-8 -*-
"""看「鸟的飞行」及其他 c 系列簇的触发词模式（含为什么/怎么的问法）"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.semantic_translate as st

for k in ['鸟的飞行', '惯性', '考试', '发烧', '地球公转', '信任', '记忆']:
    d = st.DOMAIN_SYNONYM_CLUSTERS.get(k)
    s = st.SYNONYM_CLUSTERS.get(k)
    print(f'{k}: DOMAIN={d}')
    if s: print(f'        SYNONYM={s}')
