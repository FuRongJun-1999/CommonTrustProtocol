# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
lines = src.splitlines()
for key in ("科学方法论", "自我认知", "记忆"):
    print(f"=== {key} ===")
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith('"%s": [' % key):
            print(f"  L{i+1}: {line[:80]}")
