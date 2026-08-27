# -*- coding: utf-8 -*-
"""测试 encode token 产出，定位 MISS 根因"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.semantic_translate as st

qs = {
    'OK 手机充电': '为什么手机没电了要充电',
    'MISS 下雨打伞': '下雨天为什么要打伞',
    'MISS 晚上睡觉': '为什么要晚上睡觉',
    'MISS 烧水去氯': '水为什么要烧开了喝',
    'MISS 冬天穿衣': '冬天为什么要穿厚衣服',
    'MISS 洗澡降温': '夏天冲凉能降温吗',
    'MISS 吃早饭': '为什么吃早饭很重要',
    'MISS 垃圾入桶': '为什么要垃圾分类入桶',
    'OK 洗手防病': '为什么要洗手',
    'OK 喝水规律': '为什么要按时喝水',
}
for label, q in qs.items():
    enc = st.encode(q)
    # token 中在 REVERSE_DAILY 的
    long_toks = [t for t in enc if len(t) >= 2 and t in st.REVERSE_DAILY]
    print(f'== {label}: {q}')
    print(f'   encode tokens: {list(enc.keys())[:20]}')
    print(f'   REVERSE_DAILY 命中: {long_toks}')
