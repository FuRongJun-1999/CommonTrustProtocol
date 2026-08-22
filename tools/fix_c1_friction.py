# -*- coding: utf-8 -*-
"""摩擦 补「搓手会发热」变体（问句是"搓手会发热"非连续子串）"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
m = re.search(r'"摩擦":\s*\[[^\]]*\]', src)
assert m
lst = ['搓手发热', '鞋底防滑', '摩擦', '摩擦力', '防滑', '打滑', '摩擦生热', '为什么摩擦', '增大摩擦', '减小摩擦',
       '搓手', '鞋底花纹', '鞋底', '摩擦发热', '发热是摩擦', '搓手会发热', '手会发热']
new = '"摩擦": [%s]' % ", ".join('"%s"' % t for t in lst)
src = src[:m.start()] + new + src[m.end():]
open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK 摩擦(%d)" % len(lst))
