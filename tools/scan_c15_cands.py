# -*- coding: utf-8 -*-
"""c15 候选簇审计：RD 长度 + 定义数 + 触发词"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.semantic_translate as st
import importlib
importlib.reload(st)

cands = ['负反馈','香农熵','傅里叶变换','中心极限定理','贝叶斯推断','梯度下降法',
         '正则化','强化学习','黑洞','免疫系统','内稳态','行列式',
         '睡眠记忆巩固','好奇心','朋友吵架','面粉面团','沸点与气压','身份']

src = open(r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py', encoding='utf-8').read()
for k in cands:
    rd = st.REVERSE_DAILY.get(k, '')
    n = len(re.findall('"' + re.escape(k) + r'"\s*:', src))
    d = st.DOMAIN_SYNONYM_CLUSTERS.get(k)
    s = st.SYNONYM_CLUSTERS.get(k)
    trig = d or s
    print(f'{k:<10} RD={len(rd):<4} 定义数={n:<3} 触发词={trig}')
