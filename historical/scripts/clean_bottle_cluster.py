# -*- coding: utf-8 -*-
"""清理瓶外水珠簇：移除裸泛条件词（冬天/夏天/空调房/冰箱/瓶壁碎片）
——这些是早期 auto_blindspot（v40 前）加入的，违反「裸泛词」纪律，造成跨主题误路由
（"为什么冬天河面会结冰" 命中 瓶外水珠 的 "冬天" 触发词，len(t) 决胜选了它）。
保留现象词（冰可乐/瓶外/冒水珠/冒汗/杯壁等）。
"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

CLEAN = [
    "冰可乐", "瓶外", "冒水珠", "水珠是", "瓶子里的水", "冒汗", "瓶子外",
    "杯子冒水珠", "杯壁", "冰箱拿出", "冷凝水",
]
new_block = '"瓶外水珠": [%s]' % ", ".join('"%s"' % t for t in CLEAN)
m = re.search(r'"瓶外水珠":\s*\[([^\]]*)\]', src)
assert m, "瓶外水珠 cluster not found"
print("old:", m.group(1)[:300])
src = src[:m.start()] + new_block + src[m.end():]
open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("瓶外水珠簇已清理为 %d 个触发词" % len(CLEAN))
