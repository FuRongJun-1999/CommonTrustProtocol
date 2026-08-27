# -*- coding: utf-8 -*-
"""补剩余未收敛变体的触发词（人工终裁：物理基底确认）"""
import re, sys
sys.stdout.reconfigure(encoding="utf-8")
TRANSLATE_PY = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(TRANSLATE_PY, encoding="utf-8").read()

def add_triggers(theme, new_words):
    m = re.search(r'"%s":\s*\[([^\]]*)\]' % theme, src)
    existing = [t.strip().strip('"').strip("'") for t in m.group(1).split(",") if t.strip()]
    merged = existing + [w for w in new_words if w not in existing]
    block = '"%s": [%s]' % (theme, ", ".join('"%s"' % w for w in merged))
    return src[:m.start()] + block + src[m.end():]

src = add_triggers("瓶外水珠", ["杯壁"])
src = add_triggers("泡泡彩色", ["阳光彩色"])
open(TRANSLATE_PY, "w", encoding="utf-8").write(src)
import ast
ast.parse(src)
print("patched: 瓶外水珠+杯壁, 泡泡彩色+阳光彩色; AST OK")
