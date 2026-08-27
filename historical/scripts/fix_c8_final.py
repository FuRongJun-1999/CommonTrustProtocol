# -*- coding: utf-8 -*-
"""c8 收尾：饭后不能马上运动 + 类和对象什么区别"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

m = re.search(r'"饭后运动":\s*\[[^\]]*\]', src)
assert m
lst = ['饭后运动', '饭后跑步', '刚吃完饭运动', '饭后剧烈运动', '饭后不宜运动', '饭后不能运动', '吃完饭运动', '饭后多久', '饭后散步',
       '饭后马上运动', '吃完饭马上', '刚吃完饭', '饭后可以运动', '饭后不能马上运动', '饭后马上', '马上运动']
src = src[:m.start()] + '"饭后运动": [%s]' % ", ".join('"%s"' % t for t in lst) + src[m.end():]

m2 = re.search(r'"编程类":\s*\[[^\]]*\]', src)
assert m2
lst2 = ['什么是类', '类是什么', '面向对象的类', '编程里的类', '编程类', 'class', '类和对象', '类与对象', '类是什么',
        '类对象区别', '类和对象区别', '类对象什么区别', '对象区别', '类和对象什么区别', '类与对象区别']
src = src[:m2.start()] + '"编程类": [%s]' % ", ".join('"%s"' % t for t in lst2) + src[m2.end():]

open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK")
