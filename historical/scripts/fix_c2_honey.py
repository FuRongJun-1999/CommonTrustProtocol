# -*- coding: utf-8 -*-
"""蜂蜜防腐 +会变质/变质"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
m = re.search(r'"蜂蜜防腐":\s*\[[^\]]*\]', src)
assert m
lst = ['蜂蜜不易变质', '蜂蜜不会坏', '蜂蜜防腐', '蜂蜜变质', '蜂蜜不坏', '蜂蜜为什么', '蜂蜜结晶', '蜂蜜保存', '高渗透压',
       '蜂蜜放', '不会坏', '蜂蜜会坏', '放很久', '蜂蜜水', '会变质', '变质']
new = '"蜂蜜防腐": [%s]' % ", ".join('"%s"' % t for t in lst)
src = src[:m.start()] + new + src[m.end():]
open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK 蜂蜜防腐(%d)" % len(lst))
