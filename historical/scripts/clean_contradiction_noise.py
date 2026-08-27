# -*- coding: utf-8 -*-
"""清理矛盾类自进化 patch 的含「时」噪声触发词（保留干净条件词）"""
import re, sys
sys.stdout.reconfigure(encoding="utf-8")
TRANSLATE_PY = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(TRANSLATE_PY, encoding="utf-8").read()

def is_noise(t):
    t = t.strip('"').strip("'")
    if "时" in t:  # 模板「时」噪声
        return True
    if t.startswith("么") or t.startswith("候") or t.startswith("学不") and len(t) <= 4:
        return True
    if len(t) == 2 and t in ("习室", "学一", "玩一", "学不", "停不", "不住", "直玩", "要学", "用不", "还要", "带孩", "想学", "不想学"):
        return True
    return False

lines = src.split("\n")
removed = []
for i, line in enumerate(lines):
    m = re.match(r'^(\s*"[^"]+"):\s*\[(.*)\],?\s*$', line)
    if not m:
        continue
    key, body = m.group(1), m.group(2)
    items = [x.strip() for x in body.split(",") if x.strip()]
    clean_items = []
    for it in items:
        if is_noise(it):
            removed.append((key, it))
        else:
            clean_items.append(it)
    if len(clean_items) != len(items):
        lines[i] = f'{key}: [{", ".join(clean_items)}],'
src = "\n".join(lines)
open(TRANSLATE_PY, "w", encoding="utf-8").write(src)
print("removed:", len(removed))
for k, t in removed:
    print("  ", k, "->", t)
