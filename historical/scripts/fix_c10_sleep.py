# -*- coding: utf-8 -*-
"""早睡早起 +熬夜坏处/熬夜有什么坏处（与熬夜簇共存，长短语赢回）"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
m = re.search(r'"早睡早起":\s*\[[^\]]*\]', src)
assert m
lst = ['早睡早起', '早睡', '早起', '熬夜', '熬夜坏处', '为什么要早睡', '作息规律', '几点睡',
       '熬夜有什么坏处', '熬夜的危害', '晚睡晚起']
new = '"早睡早起": [%s]' % ", ".join('"%s"' % t for t in lst)
src = src[:m.start()] + new + src[m.end():]
open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK 早睡早起(%d)" % len(lst))
