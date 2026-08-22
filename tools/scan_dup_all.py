# -*- coding: utf-8 -*-
"""全局重复 key 审计：DOMAIN_SYNONYM_CLUSTERS/DOMAIN_ROUTE/REVERSE_DAILY 的重复 key
（上一轮发现惯性重复 key 覆盖 bug——升级版被旧版覆盖失效；全量扫描同类问题）
"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
lines = src.splitlines()

def scan_dict(dict_name, pattern, value_check):
    in_dict = False
    keys = []
    for i, line in enumerate(lines):
        s = line.strip()
        if s == "%s = {" % dict_name:
            in_dict = True
            continue
        if in_dict:
            if s == "}":
                break
            m = re.match(r'"([^"]+)"\s*:', s)
            if m and value_check in line:
                keys.append((i + 1, m.group(1)))
    from collections import Counter
    kc = Counter(k for _, k in keys)
    dups = {k: v for k, v in kc.items() if v > 1}
    print(f"{dict_name} 重复 key ({len(keys)} 项):", dups if dups else "无")
    if dups:
        for k in dups:
            locs = [ln for ln, kk in keys if kk == k]
            print(f"  {k}: 出现在行 {locs}")

scan_dict("DOMAIN_SYNONYM_CLUSTERS", r'\[', "[")
scan_dict("DOMAIN_ROUTE", r'\"', '"')
scan_dict("REVERSE_DAILY", r'\"', '"')
