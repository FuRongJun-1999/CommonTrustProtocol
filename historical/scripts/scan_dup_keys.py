# -*- coding: utf-8 -*-
"""扫描 DOMAIN_SYNONYM_CLUSTERS 内重复 key（后覆盖前 bug 检查）"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
lines = src.splitlines()
# 提取 line 114 (DOMAIN_SYNONYM_CLUSTERS) 到第一个行首 } 之间的 key
in_domain = False
keys = []
for i, line in enumerate(lines):
    s = line.strip()
    if s == "DOMAIN_SYNONYM_CLUSTERS = {":
        in_domain = True
        continue
    if in_domain:
        if s == "}":
            break
        m = re.match(r'"([^"]+)"\s*:', s)
        if m and "[" in line:
            keys.append((i + 1, m.group(1)))
# 找重复 key
from collections import Counter
kc = Counter(k for _, k in keys)
dups = {k: v for k, v in kc.items() if v > 1}
print("DOMAIN_SYNONYM_CLUSTERS 重复 key:", dups if dups else "无")
# 同样扫 SYNONYM_CLUSTERS
in_syn = False
keys2 = []
for i, line in enumerate(lines):
    s = line.strip()
    if s == "SYNONYM_CLUSTERS = {":
        in_syn = True
        continue
    if in_syn:
        if s == "}":
            break
        m = re.match(r'"([^"]+)"\s*:', s)
        if m and "[" in line:
            keys2.append((i + 1, m.group(1)))
kc2 = Counter(k for _, k in keys2)
dups2 = {k: v for k, v in kc2.items() if v > 1}
print("SYNONYM_CLUSTERS 重复 key:", dups2 if dups2 else "无")
