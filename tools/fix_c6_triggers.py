# -*- coding: utf-8 -*-
"""c6 触发词补盲：价格怎么定/越来越不值钱/递归和循环"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

UPD = {
    "供需求": ['供求', '供需', '供大于求', '供需求', '供求关系', '供需关系', '供不应求', '价格由', '供需平衡', '为什么涨价', '为什么降价', '物以稀为贵',
             '价格怎么定', '价格是', '价格谁定', '怎么定价'],
    "通货膨胀": ['通货膨胀', '通胀', '物价上涨', '钱不值钱', '通胀是', '购买力下降', '钱变多', '通胀率', '货币贬值', '为什么钱不值钱',
               '越来越不值钱', '钱越来越', '不值钱了'],
    "递归": ['什么是递归', '递归是什么', '递归算法', '递归', '递归是', '阶乘', '斐波那契', '调用自己', '递归函数', '终止条件', '汉诺塔',
            '递归和循环', '递归与循环', '递归循环'],
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
