# -*- coding: utf-8 -*-
"""c14 候选簇审计：RD 长度 + 重复 key + 触发词"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.semantic_translate as st
import importlib
importlib.reload(st)

cands = ['频率','波','振动','声音不能传播','弹性','梁的弯曲','混凝土','能级','能带',
         '唐诗','宋词','绝句','物质的量','摩尔','加速度','动能','势能','电路','电阻']

src = open(r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py', encoding='utf-8').read()
for k in cands:
    rd = st.REVERSE_DAILY.get(k, '')
    n = len(re.findall('"' + re.escape(k) + r'"\s*:', src))
    d = st.DOMAIN_SYNONYM_CLUSTERS.get(k)
    s = st.SYNONYM_CLUSTERS.get(k)
    trig = d or s
    print(f'{k:<10} RD={len(rd):<4} 定义数={n:<3} 触发词={trig}')
