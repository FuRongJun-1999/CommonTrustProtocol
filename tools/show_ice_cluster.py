# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
import re
m = re.search(r'"结冰":\s*\[([^\]]*)\]', src)
print("current 结冰 cluster:")
print(m.group(0)[:2000])
