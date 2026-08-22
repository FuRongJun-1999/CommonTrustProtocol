# -*- coding: utf-8 -*-
"""给拖延启动簇加自然表达触发词"""
import re, ast, sys
sys.stdout.reconfigure(encoding="utf-8")
TRANSLATE_PY = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(TRANSLATE_PY, encoding="utf-8").read()
NEW = ["拖到最后一刻", "磨蹭", "卡在哪", "静不下来", "明天再做",
       "不动手", "从哪下手", "拆成小块", "逼自己开始", "进入状态",
       "大项目", "脑子空白"]
m = re.search(r'"拖延启动":\s*\[([^\]]*)\]', src)
existing = [t.strip().strip('"').strip("'") for t in m.group(1).split(",") if t.strip()]
merged = existing + [w for w in NEW if w not in existing]
block = '"拖延启动": [%s]' % ", ".join('"%s"' % w for w in merged)
src = src[:m.start()] + block + src[m.end():]
open(TRANSLATE_PY, "w", encoding="utf-8").write(src)
ast.parse(src)
print("patched 拖延启动 +%d 自然表达触发词" % len(NEW))
