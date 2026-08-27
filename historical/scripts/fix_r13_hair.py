# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
m = re.search(r'"遗传":\s*\[[^\]]*\]', src)
assert m
lst = ['像爸爸', '像妈妈', '长得像', '遗传', '长得不一样', '长得不像',
       '不像父母', '像父母', '传给孩子', '近视眼', '基因', '双胞胎',
       '天生还是后天', '遗传病', '隔代遗传', '有病的孩子', '生出',
       '偏偏是黄', '头发颜色']
new = '"遗传": [%s]' % ", ".join('"%s"' % t for t in lst)
src = src[:m.start()] + new + src[m.end():]
open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK 遗传(%d)" % len(lst))
