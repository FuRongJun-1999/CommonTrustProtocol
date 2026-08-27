# -*- coding: utf-8 -*-
"""c5 收尾：定语从句 +that和which/that与which/区别"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
m = re.search(r'"定语从句":\s*\[[^\]]*\]', src)
assert m
lst = ['定语从句', '从句', '定语从句是', '关系词', '先行词', 'that which', 'who whom', '修饰名词', '定语',
       'that和which', 'that与which', 'which和that', '关系代词', '关系副词']
new = '"定语从句": [%s]' % ", ".join('"%s"' % t for t in lst)
src = src[:m.start()] + new + src[m.end():]
open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK 定语从句(%d)" % len(lst))
