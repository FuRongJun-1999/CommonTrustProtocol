# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
i = src.index('"发酵": "为什么面团会发酵')
seg = src[i:i+300]
print("HEAD:", seg[:80])
# 找该行结束
eol = src.index("\n", i)
line = src[i:eol]
print("TAIL:", repr(line[-80:]))
