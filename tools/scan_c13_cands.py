# -*- coding: utf-8 -*-
"""c13 候选簇审计：当前定义 + REVERSE_DAILY 长度 + 重复 key 扫描"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.semantic_translate as st
import importlib
importlib.reload(st)

cands = ['一年月数','一周天数','一天小时','天空蓝色','月亮发光','船浮水上',
         '应力','短路','混凝土钢筋','细胞','原子','介质','弹性','梁的弯曲',
         '频率','波','振动','能级','能带','声音不能传播','吃早饭','米饭','面条']

src = open(r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py', encoding='utf-8').read()
print(f"{'key':<8} {'RD_len':<7} {'定义数':<4} {'DOMAIN触发词'}")
for k in cands:
    rd = st.REVERSE_DAILY.get(k, '')
    n = len(re.findall('"' + re.escape(k) + r'"\s*:', src))
    d = st.DOMAIN_SYNONYM_CLUSTERS.get(k)
    s = st.SYNONYM_CLUSTERS.get(k)
    trig = d or s
    print(f"{k:<8} {len(rd):<7} {n:<4} {trig}")
