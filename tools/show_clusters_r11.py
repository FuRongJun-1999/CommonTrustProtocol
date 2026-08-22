# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
for theme in ("影子", "回声"):
    m = re.search(r'"%s":\s*\[([^\]]*)\]' % theme, src)
    print(f"--- {theme} ---")
    print(m.group(1)[:1500])
