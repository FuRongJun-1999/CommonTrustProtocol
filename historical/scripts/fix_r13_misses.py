# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

PHOTO = ['叶子变绿', '植物晒太阳', '光合作用', '叶子为什么绿', '叶子是绿的',
         '植物为什么', '植物要晒太阳', '叶子为什么是绿', '为什么叶子绿',
         '植物', '叶子', '植物不吃东西', '植物吸收二氧化碳', '草长得快', '花放两天',
         '花草不长', '不长', '枯了', '蔫了']
GENETIC = ['像爸爸', '像妈妈', '长得像', '遗传', '长得不一样', '长得不像',
           '不像父母', '像父母', '传给孩子', '近视眼', '基因', '双胞胎',
           '天生还是后天', '遗传病', '隔代遗传', '有病的孩子', '生出']

for theme, lst in (("光合作用", PHOTO), ("遗传", GENETIC)):
    m = re.search(r'"%s":\s*\[[^\]]*\]' % theme, src)
    assert m, theme
    new = '"%s": [%s]' % (theme, ", ".join('"%s"' % t for t in lst))
    src = src[:m.start()] + new + src[m.end():]

open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK 光合作用(%d)/遗传(%d)" % (len(PHOTO), len(GENETIC)))
