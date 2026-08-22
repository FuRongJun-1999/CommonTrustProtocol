# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

# 1) 结冰补 冻裂/水管冻裂（自然问法"水管冬天会冻裂"非连续子串）
m = re.search(r'"结冰":\s*\[[^\]]*\]', src)
assert m
ice = ['结冰', '结冰了', '冻成冰', '水面结冰', '河面结冰', '湖面结冰', '为什么结冰',
       '结冰是', '上冻', '冻住了', '水结冰', '结冰温度', '冰是', '冰怎么',
       '冰能浮', '冰浮', '冰浮在水', '冰块', '冬天水管冻裂', '水只冻住表层',
       '冰凌', '冻实', '水管冻裂', '冰面', '冻裂']
src = src[:m.start()] + '"结冰": [%s]' % ", ".join('"%s"' % t for t in ice) + src[m.end():]

# 2) 液化补 露水/露珠（草地露水=水汽遇冷凝结——液化/凝结）
m2 = re.search(r'"液化":\s*\[[^\]]*\]', src)
if m2:
    print("液化 cluster old:", m2.group(0)[:200])
    src = src[:m2.start()] + '"液化": ["液化", "水蒸气凝结", "凝结成水", "露水", "露珠", "哈气成水", "小水珠"]' + src[m2.end():]
else:
    print("液化 cluster not found — skip")

open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK")
