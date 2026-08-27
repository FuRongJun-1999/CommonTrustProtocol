# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
m = re.search(r'"鸟的飞行":\s*\[[^\]]*\]', src)
assert m
lst = ["鸟能飞", "为什么鸟", "鸟为什么", "鸟飞行", "鸟会飞", "鸟类飞行",
       "鸟怎么飞", "翅膀", "羽毛", "扑翅膀", "扇翅膀", "展翅", "振翅",
       "滑翔", "翱翔", "盘旋", "飞不起来", "不会飞", "人能飞吗",
       "人为什么不会飞", "鸟为什么会飞", "鸟是怎么飞的", "为什么鸟能飞",
       "像鸟一样飞", "鸟一样飞", "怎么让鸟飞", "让鸟飞起来", "鸟飞起来",
       "鸵鸟", "起飞", "展翅高飞", "鸟在天上飞"]
new = '"鸟的飞行": [%s]' % ", ".join('"%s"' % t for t in lst)
src = src[:m.start()] + new + src[m.end():]
open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK 鸟的飞行(%d)" % len(lst))
