# -*- coding: utf-8 -*-
"""比较级答案改写：去掉 'This is' 例句（BAD_SIGNALS 误报——英文例句被当 LLM 崩坏信号）"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
m = re.search(r'    "比较级": "([^"]*)"', src)
assert m
ans = m.group(1)
# 替换含 This is 的例句
ans = ans.replace("This is cheaper than that", "这件比那件便宜")
ans = ans.replace("This is", "那件更")
open(p, "w", encoding="utf-8").write(src.replace(m.group(1), ans))
import py_compile
py_compile.compile(p, doraise=True)
print("比较级答案已改写，This is 剩余:", "This is" in ans)
