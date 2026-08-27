# -*- coding: utf-8 -*-
"""删除 DOMAIN_SYNONYM_CLUSTERS 中重复的短版惯性（line 1150），保留 line 135 的长版"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
# 短版惯性行：只含 3 个触发词
short = '    "惯性": ["什么是惯性", "惯性是什么", "惯性定律"],'
count = src.count(short)
print("short 惯性 occurrences:", count)
if count == 1:
    src = src.replace(short, "")
    print("deleted short 惯性 (line 1150)")
elif count > 1:
    # 删最后一个（保留最前面的长版）
    idx = src.rfind(short)
    src = src[:idx] + src[idx + len(short):]
    print(f"deleted one of {count} short 惯性")
open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("syntax OK")
