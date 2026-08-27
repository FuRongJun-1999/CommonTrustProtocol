# -*- coding: utf-8 -*-
"""检查 v72b 进度"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
p = r'D:\Program Files\2_ai\knowledge-base\conflict_testset_v72b_results.json'
if os.path.exists(p):
    d = json.load(open(p, encoding='utf-8'))
    print('v72b results:', d.get('ok'), '/', d.get('total'))
    for x in d['results']:
        if x['bad']:
            print(f"  [{x['domain']}/{x['stage']}] {x['q']} | {x['route']}")
else:
    print('v72b 尚未完成')
