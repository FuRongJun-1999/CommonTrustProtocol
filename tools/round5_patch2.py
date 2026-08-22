# -*- coding: utf-8 -*-
"""补学习游戏趣味 1 个自然表达触发词"""
import re, ast, sys
sys.stdout.reconfigure(encoding="utf-8")
TRANSLATE_PY = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(TRANSLATE_PY, encoding="utf-8").read()
m = re.search(r'"学习游戏趣味":\s*\[([^\]]*)\]', src)
existing = [t.strip().strip('"').strip("'") for t in m.group(1).split(",") if t.strip()]
merged = existing + ["马上就有奖励", "看不到效果"]
block = '"学习游戏趣味": [%s]' % ", ".join('"%s"' % w for w in merged)
src = src[:m.start()] + block + src[m.end():]
open(TRANSLATE_PY, "w", encoding="utf-8").write(src)
ast.parse(src)
print("patched 学习游戏趣味 +2")
