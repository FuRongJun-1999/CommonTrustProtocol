# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
m = re.search(r'"燃烧":\s*\[[^\]]*\]', src)
assert m
lst = ['着火了', '烧起来', '点燃', '燃烧', '着火点', '灭火', '为什么着火', '自燃',
       '火烧', '为什么烧起来', '怎么灭火', '燃点', '点不着', '点不燃', '和生锈',
       '用锅盖', '锅盖盖', '烧很久', '越烧越旺', '烧得更旺', '扑灭', '熄火',
       '蜡烛', '火苗', '烧完']
new = '"燃烧": [%s]' % ", ".join('"%s"' % t for t in lst)
src = src[:m.start()] + new + src[m.end():]
open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK 燃烧(%d)" % len(lst))
