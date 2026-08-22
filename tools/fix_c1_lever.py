# -*- coding: utf-8 -*-
"""杠杆 补「有哪些杠杆/杠杆有哪些」"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
m = re.search(r'"杠杆":\s*\[[^\]]*\]', src)
assert m
lst = ['跷跷板', '撬东西', '杠杆', '杠杆原理', '支点', '力臂', '撬棍', '省力', '费力杠杆',
       '有哪些杠杆', '杠杆有哪些', '杠杆在哪', '杠杆例子', '杠杆生活']
new = '"杠杆": [%s]' % ", ".join('"%s"' % t for t in lst)
src = src[:m.start()] + new + src[m.end():]
open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK 杠杆(%d)" % len(lst))
