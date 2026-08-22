# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
i = src.index('"凝华": "为什么冬天窗户上会有霜花')
# 找该行结束
eol = src.index("\n", i)
line = src[i:eol]
print("凝华 answer line tail:", repr(line[-60:]))
