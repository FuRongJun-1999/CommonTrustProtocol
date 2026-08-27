# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
old = '"冰是", "冰怎么"]'
new = '"冰是", "冰怎么", "冰能浮", "冰浮", "冰浮在水"]'
assert old in src, "anchor not found"
src = src.replace(old, new)
open(p, "w", encoding="utf-8").write(src)
print("added ice-float triggers OK")
