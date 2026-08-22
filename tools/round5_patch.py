# -*- coding: utf-8 -*-
"""round5：自然表达触发词 patch（人工终裁）"""
import re, ast, sys
sys.stdout.reconfigure(encoding="utf-8")
TRANSLATE_PY = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(TRANSLATE_PY, encoding="utf-8").read()

ADD = {
    "学习游戏趣味": ["背单词软件", "学新东西", "三分钟热度", "打怪升级", "闯关一样", "一点就爽", "总想拖延", "爱上学习"],
    "学习意义": ["用不上", "图个啥", "白学", "记东西", "练本事", "手艺", "背公式", "越学越", "这把年纪"],
}
for theme, words in ADD.items():
    m = re.search(r'"%s":\s*\[([^\]]*)\]' % theme, src)
    existing = [t.strip().strip('"').strip("'") for t in m.group(1).split(",") if t.strip()]
    merged = existing + [w for w in words if w not in existing]
    block = '"%s": [%s]' % (theme, ", ".join('"%s"' % w for w in merged))
    src = src[:m.start()] + block + src[m.end():]
open(TRANSLATE_PY, "w", encoding="utf-8").write(src)
ast.parse(src)
print("patched:", {k: len(v) for k, v in ADD.items()})
