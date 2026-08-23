# -*- coding: utf-8 -*-
"""扫描 c12 候选 key 在 REVERSE_DAILY 中的现有定义（防重复 key 覆盖）"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

src = open(r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py', encoding='utf-8').read()

cands = ['节约用水','垃圾入桶','喝水规律','饿了吃饭','夏天出汗','冬天穿衣','洗手防病',
         '手机充电','下雨打伞','晚上睡觉','吃早饭','洗澡降温','开水晾凉','烧水去氯',
         '节水节电','窗户起雾','蔬果营养','天空蓝色','月亮发光','船浮水上']

for k in cands:
    pat = '"' + re.escape(k) + r'"\s*:'
    cnt = len(re.findall(pat, src))
    # 找各出现位置的行号
    lines = []
    for m in re.finditer(pat, src):
        lineno = src[:m.start()].count('\n') + 1
        lines.append(lineno)
    print(f'{k}: {cnt} 处定义 {lines}')

print('总行数:', len(src.splitlines()))
