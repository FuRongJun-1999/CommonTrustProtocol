# -*- coding: utf-8 -*-
"""删除 DOMAIN_SYNONYM_CLUSTERS 内重复的旧惯性簇（line 1150，3 词——覆盖了 line 135 的 17 词版）"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

old = '    "惯性": ["什么是惯性", "惯性是什么", "惯性定律"],\n'
count = src.count(old)
print("old 惯性 cluster occurrences:", count)
# 只删第二个（保留 line 135 的完整版）——find 第二个
idx = src.find(old)
idx2 = src.find(old, idx + 1)
if idx2 != -1:
    src = src[:idx2] + src[idx2 + len(old):]
    print("deleted duplicate 惯性 cluster")
else:
    print("no duplicate found (only one occurrence)")
open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("syntax OK")
