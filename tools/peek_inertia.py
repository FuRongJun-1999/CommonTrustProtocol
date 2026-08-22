# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
m = re.search(r'"惯性":\s*\[[^\]]*\]', src)
print("found:", m.group(0)[:100] if m else "NONE")
