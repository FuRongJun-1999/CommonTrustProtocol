# -*- coding: utf-8 -*-
"""感知：32 个 no_answer 簇的真实路由状态（哪些走情感路由=设计使然，哪些是知识缺口）"""
import sys, json, importlib
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.semantic_translate as st
importlib.reload(st)
import wisdom.chat_engine as ce
importlib.reload(ce)

ledger = json.load(open(r'D:\Program Files\2_ai\CommonTrustProtocol\ledger\evolution_ledger.json', encoding='utf-8'))['entries']
no_ans = [k for k, e in ledger.items() if e['status'] == 'no_answer']
print(f'no_answer 簇: {len(no_ans)}')

# 对每个 no_answer 簇，用其第一个触发词问 chat，看路由
for k in sorted(no_ans):
    triggers = list(st.DOMAIN_SYNONYM_CLUSTERS.get(k, [])) + list(st.SYNONYM_CLUSTERS.get(k, []))
    q = triggers[0] if triggers else k
    try:
        r = ce.chat(dex=None, message=q)
        txt = r['reply'][:60] if isinstance(r, dict) else str(r)[:60]
        route = r.get('route', '?') if isinstance(r, dict) else '?'
        print(f'  {k}: [{route}] {txt!r}')
    except Exception as e:
        print(f'  {k}: ERR {e}')
