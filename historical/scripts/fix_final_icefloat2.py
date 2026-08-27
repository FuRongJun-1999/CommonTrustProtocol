# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
m = re.search(r'"结冰":\s*\[[^\]]*\]', src)
assert m
lst = ['结冰', '结冰了', '冻成冰', '水面结冰', '河面结冰', '湖面结冰', '为什么结冰',
       '结冰是', '上冻', '冻住了', '水结冰', '结冰温度', '冰是', '冰怎么',
       '冰能浮', '冰浮', '冰浮在水', '冰浮在水上', '冰能浮在水上', '冬天水管冻裂',
       '水只冻住表层', '冰凌', '冻实', '水管冻裂', '冰面', '冻裂']
new = '"结冰": [%s]' % ", ".join('"%s"' % t for t in lst)
src = src[:m.start()] + new + src[m.end():]
open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK 结冰(%d)" % len(lst))
