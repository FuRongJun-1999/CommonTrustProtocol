# -*- coding: utf-8 -*-
"""结冰簇最终定稿：
- 人工基础词 + LLM 有效补盲（冰块/冬天水管冻裂/水只冻住表层/冰凌/冻实）
- 白霜归凝华（drift 正确路由），我家/一层/窗子等口语框架词全部丢弃
"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

ICE = [
    "结冰", "结冰了", "冻成冰", "水面结冰", "河面结冰", "湖面结冰", "为什么结冰",
    "结冰是", "上冻", "冻住了", "水结冰", "结冰温度", "冰是", "冰怎么",
    "冰能浮", "冰浮", "冰浮在水", "冰块", "冬天水管冻裂", "水只冻住表层",
    "冰凌", "冻实", "水管冻裂", "冰面",
]
new_block = '"结冰": [%s]' % ", ".join('"%s"' % t for t in ICE)
m = re.search(r'"结冰":\s*\[[^\]]*\]', src)
assert m
src = src[:m.start()] + new_block + src[m.end():]

# 凝华补 白霜（drift 正确路由）
HUA = ["窗户结霜", "结霜", "凝华", "白霜", "窗花"]
hb = '"凝华": [%s]' % ", ".join('"%s"' % t for t in HUA)
m2 = re.search(r'"凝华":\s*\[[^\]]*\]', src)
assert m2
src = src[:m2.start()] + hb + src[m2.end():]

open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("结冰(%d)/凝华(%d) 定稿" % (len(ICE), len(HUA)))
