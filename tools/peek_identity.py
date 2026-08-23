# -*- coding: utf-8 -*-
"""检查身份簇现状：RD 内容 + 触发词 + 是否角色应答"""
import sys, importlib
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.semantic_translate as st
importlib.reload(st)

print('身份 RD:', st.REVERSE_DAILY.get('身份', '')[:200])
print('身份 DOMAIN 触发词:', st.DOMAIN_SYNONYM_CLUSTERS.get('身份'))
# 检查「你是谁」当前路由
import wisdom.chat_engine as ce
importlib.reload(ce)
r = ce.chat(dex=None, message='你是谁？')
print('「你是谁」回答:', r['reply'][:150])
