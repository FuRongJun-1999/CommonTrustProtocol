# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
m = re.search(r'"结冰":\s*\[[^\]]*\]', src)
assert m
ice = ['结冰', '结冰了', '冻成冰', '水面结冰', '河面结冰', '湖面结冰', '为什么结冰',
       '结冰是', '上冻', '冻住了', '水结冰', '结冰温度', '冰是', '冰怎么',
       '冰能浮', '冰浮', '冰浮在水', '冰块', '冬天水管冻裂', '水只冻住表层',
       '冰凌', '冻实', '水管冻裂', '冰面', '冻裂', '融化', '快点融化', '冰融化']
src = src[:m.start()] + '"结冰": [%s]' % ", ".join('"%s"' % t for t in ice) + src[m.end():]
open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("结冰 +融化/快点融化/冰融化 ->", len(ice))
