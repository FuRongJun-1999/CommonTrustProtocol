# -*- coding: utf-8 -*-
"""round14 触发词补盲：
燃烧 +点不着/点不燃/和生锈、溶解 +放进水里/会不见/和融化/融化一样、
汽水气泡 +没气/放久了没气
"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

UPD = {
    "燃烧": ['着火了', '烧起来', '点燃', '燃烧', '着火点', '灭火', '为什么着火', '自燃',
            '火烧', '为什么烧起来', '怎么灭火', '燃点', '点不着', '点不燃', '和生锈'],
    "溶解": ['糖化了', '盐化了', '变咸', '咸了', '放盐', '糖放水里不见了', '溶解',
            '溶解了', '化在水里', '溶于', '溶解速度', '怎么溶解', '放进水里',
            '会不见', '和融化', '融化一样'],
    "汽水气泡": ['汽水气泡', '汽水为什么冒泡', '打开汽水', '冒泡', '气泡', '没气了',
                '打嗝', '喷出来', '摇晃汽水', '二氧化碳', '没气', '放久了没气'],
    "血液循环": ['心跳', '血管', '血液循环', '心跳加速', '心跳快', '为什么心跳',
                '血液', '心脏', '供血', '泵血'],
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
