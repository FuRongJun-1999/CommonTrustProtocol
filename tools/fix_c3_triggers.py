# -*- coding: utf-8 -*-
"""c3 收尾触发词：零自然数+正整数/正整数吗、偶数+0是偶数/0是偶"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

UPD = {
    "零自然数": ['0是自然数', '零是自然数', '0是自然数吗', '0是自然', '自然数', '0是什么数', '0是偶数', '0的特性',
               '正整数', '正整数吗', '正整数是', '自然数包括'],
    "偶数": ['什么是偶数', '偶数是什么', '偶数', '什么叫偶数', '双数', '偶数奇数', '偶数是', '奇偶',
            '0是偶数吗', '0是偶', '零是偶数'],
}
for theme, lst in UPD.items():
    m = re.search(r'"%s":\s*\[[^\]]*\]' % theme, src)
    assert m, theme
    new = '"%s": [%s]' % (theme, ", ".join('"%s"' % t for t in lst))
    src = src[:m.start()] + new + src[m.end():]

open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK:", {k: len(v) for k, v in UPD.items()})
