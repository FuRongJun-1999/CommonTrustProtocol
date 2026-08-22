# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
# 找凝华 在 DOMAIN_ROUTE 的行
for line in src.splitlines():
    if '"凝华"' in line and '"物理学"' in line and '[' not in line:
        print("ROUTE line:", line[:80])
# 找凝华 直答结尾
m = re.search(r'"凝华": "为什么冬天窗户上会有霜花(.{0,50})$', src, re.M)
print("凝华 answer line tail:", src[src.index('"凝华": "为什么冬天窗户上会有霜花')+30:src.index('"凝华": "为什么冬天窗户上会有霜花')+120])
