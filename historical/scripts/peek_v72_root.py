# -*- coding: utf-8 -*-
"""定位 v72 失败根因：检查 REVERSE_DAILY/DOMAIN_TABLE/encode 实际状态"""
import sys, importlib
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.semantic_translate as st
importlib.reload(st)

print('REVERSE_DAILY 有 储能:', '储能' in st.REVERSE_DAILY, len(st.REVERSE_DAILY.get('储能', '')))
print('REVERSE_DAILY 有 碳中和:', '碳中和' in st.REVERSE_DAILY)
print('DOMAIN_TABLE 有 什么是储能:', '什么是储能' in st.DOMAIN_TABLE)
print('DOMAIN_TABLE 有 储能:', '储能' in st.DOMAIN_TABLE)
print('DOMAIN_TABLE 有 什么是碳中和:', '什么是碳中和' in st.DOMAIN_TABLE)
print('DOMAIN_TABLE 有 碳中和:', '碳中和' in st.DOMAIN_TABLE)
print()
print('encode(什么是储能):', list(st.encode('什么是储能').keys()))
print('encode(什么是碳中和):', list(st.encode('什么是碳中和').keys()))
print('encode(什么是锂电池):', list(st.encode('什么是锂电池').keys()))
print()
# chat 测试
import wisdom.chat_engine as ce
importlib.reload(ce)
for q in ['什么是储能？', '什么是碳中和？', '什么是锂电池？']:
    r = ce.chat(dex=None, message=q)
    print(f'  {q} -> route={r.get("route","?")} [{len(r["reply"])}ch]')
