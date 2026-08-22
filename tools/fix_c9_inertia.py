# -*- coding: utf-8 -*-
"""惯性 触发词补全"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
m = re.search(r'"惯性":\s*\[[^\]]*\]', src)
assert m
lst = ['什么是惯性', '惯性是什么', '惯性定律', '惯性', '急刹车', '刹车前冲', '保持运动', '惯性是', '质量惯性',
       '急刹车人前冲', '人前冲', '惯性是力', '惯性不是力', '惯性大小', '急刹车为什么', '惯性力', '物体保持']
new = '"惯性": [%s]' % ", ".join('"%s"' % t for t in lst)
src = src[:m.start()] + new + src[m.end():]
open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK 惯性(%d)" % len(lst))
