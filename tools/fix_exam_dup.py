# -*- coding: utf-8 -*-
"""删除 DOMAIN_SYNONYM_CLUSTERS 中重复的旧版考试簇（line 1146），保留 line 90 的新版"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
short = '    "考试": ["明天要考试", "要考试", "考试怎么办", "考试了", "考试"],'
count = src.count(short)
print("old 考试 occurrences:", count)
if count == 1:
    src = src.replace(short, "")
    print("deleted old 考试 cluster")
open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("syntax OK")
