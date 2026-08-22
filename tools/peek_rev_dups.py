# -*- coding: utf-8 -*-
"""检查 REVERSE_DAILY 重复 key 的实际内容（后覆盖前是否合理）"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
lines = src.splitlines()
for key in ("惯性", "科学方法论", "概念形成", "职场边界"):
    print(f"=== {key} ===")
    for i, line in enumerate(lines):
        if line.strip().startswith('"%s": "' % key):
            # 截取答案开头
            m = re.match(r'\s*"%s": "([^"]{0,60})' % key, line)
            print(f"  L{i+1}: {m.group(1)[:60] if m else line[:60]}")
