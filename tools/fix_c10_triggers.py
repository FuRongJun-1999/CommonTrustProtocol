# -*- coding: utf-8 -*-
"""c10 触发词补盲：横着刷/通一次风"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

UPD = {
    "刷牙护牙": ['刷牙', '护牙', '蛀牙', '刷牙怎么', '巴氏刷牙', '牙刷多久换', '怎么刷牙', '为什么要刷牙', '防蛀',
               '横着刷', '横刷', '刷牙方法', '刷牙姿势', '牙刷'],
    "开窗通风": ['开窗通风', '通风', '开窗', '换气', '空气不流通', '为什么通风', '多久通风', '雾霾天开窗',
               '通一次风', '通风多久', '什么时候通风', '开窗多久', '每天通风'],
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
