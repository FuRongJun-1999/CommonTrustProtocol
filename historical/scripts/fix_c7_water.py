# -*- coding: utf-8 -*-
"""运动补水 +运动后为什么要喝水（含要字变体）"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
m = re.search(r'"运动补水":\s*\[[^\]]*\]', src)
assert m
lst = ['运动后喝水', '出汗喝水', '出汗后喝水', '补水', '出汗后要喝水', '运动出汗喝水', '运动补水', '电解质', '运动饮料', '补水时机', '水中毒',
       '运动后要喝水', '运动后为什么喝水', '运动完喝水', '运动后为什么要喝水', '为什么要喝水', '为什么要补水']
new = '"运动补水": [%s]' % ", ".join('"%s"' % t for t in lst)
src = src[:m.start()] + new + src[m.end():]
open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK 运动补水(%d)" % len(lst))
