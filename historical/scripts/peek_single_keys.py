# -*- coding: utf-8 -*-
"""查 REVERSE_DAILY 全部单字 key（评估放宽 len>=2 过滤的影响）"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.semantic_translate as st
import importlib
importlib.reload(st)

single = [k for k in st.REVERSE_DAILY if len(k) == 1]
print('单字 key:', single)
for k in single:
    print(f'  {k}: [{len(st.REVERSE_DAILY[k])}ch] {st.REVERSE_DAILY[k][:40]}')
    print(f'    DOMAIN触发词: {st.DOMAIN_SYNONYM_CLUSTERS.get(k)}')
    print(f'    SYNONYM触发词: {st.SYNONYM_CLUSTERS.get(k)}')
