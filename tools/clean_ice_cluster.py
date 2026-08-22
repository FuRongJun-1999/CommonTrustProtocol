# -*- coding: utf-8 -*-
"""清理结冰簇：去掉自动提取产生的碎片（标点/口语噪声/邻现象词）
保留：人工基础触发词 + 有意义的 LLM 补盲词（水只冻住表层/冬天水管冻裂/冰块）
去掉：我家/一层/白霜（凝华）/标点碎片
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

CLEAN = [
    "结冰", "结冰了", "冻成冰", "水面结冰", "河面结冰", "湖面结冰", "为什么结冰",
    "结冰是", "上冻", "冻住了", "水结冰", "结冰温度", "冰是", "冰怎么",
    "冰能浮", "冰浮", "冰浮在水", "冰块", "冬天水管冻裂", "水只冻住表层",
]
new_block = '"结冰": [%s]' % ", ".join('"%s"' % t for t in CLEAN)

import re
m = re.search(r'"结冰":\s*\[[^\]]*\]', src)
assert m, "结冰 cluster not found"
src = src[:m.start()] + new_block + src[m.end():]
open(p, "w", encoding="utf-8").write(src)

import py_compile
py_compile.compile(p, doraise=True)
print("结冰簇已清理为 %d 个触发词" % len(CLEAN))
