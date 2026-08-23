# -*- coding: utf-8 -*-
"""阶段1验证：ledger 薄簇清单 vs 人工审计(audit_remaining_c15) 一致性 diff"""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')

ledger = json.load(open(r'D:\Program Files\2_ai\CommonTrustProtocol\ledger\evolution_ledger.json', encoding='utf-8'))['entries']
ledger_thin = {k for k, e in ledger.items() if 0 < e['rd_len'] < 80}

# 人工审计快照（audit_remaining_c15.py 逻辑重建：<80 且在 DOMAIN/SYNONYM 簇中）
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.semantic_translate as st
import importlib
importlib.reload(st)
manual_thin = set()
for k, v in st.REVERSE_DAILY.items():
    if len(v) < 80 and (k in st.DOMAIN_SYNONYM_CLUSTERS or k in st.SYNONYM_CLUSTERS):
        manual_thin.add(k)

print(f'ledger 薄簇: {len(ledger_thin)}')
print(f'人工审计薄簇: {len(manual_thin)}')
only_ledger = ledger_thin - manual_thin
only_manual = manual_thin - ledger_thin
print(f'\n仅在 ledger（不在人工审计）: {len(only_ledger)}')
for k in sorted(only_ledger):
    print(f'  {k} ({ledger[k]["rd_len"]}ch)')
print(f'\n仅在人工审计（不在 ledger）: {len(only_manual)}')
for k in sorted(only_manual):
    print(f'  {k} ({len(st.REVERSE_DAILY[k])}ch)')
print(f'\n一致数: {len(ledger_thin & manual_thin)}')
