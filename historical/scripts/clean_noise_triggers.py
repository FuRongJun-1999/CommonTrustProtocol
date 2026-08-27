# -*- coding: utf-8 -*-
"""清理自进化 patch 的噪声触发词：含「的时候」/「候X」碎片从所有簇移除
保留干净条件词（空调房/高海拔/刀沾水/通风处等）。"""
import re, sys
sys.stdout.reconfigure(encoding="utf-8")
TRANSLATE_PY = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(TRANSLATE_PY, encoding="utf-8").read()

def is_noise(t):
    t = t.strip('"').strip("'")
    if "的时候" in t:
        return True
    if t.startswith("候") or t.endswith("候"):
        return True
    if re.fullmatch(r"[^\"']{1,3}候[^\"']{0,2}", t) and "候" in t:
        return True
    return False

# 逐簇处理：删除噪声触发词
lines = src.split("\n")
removed = []
for i, line in enumerate(lines):
    if "]: [" in line or '"' not in line:
        continue
    # 找到 "key": [ 列表行（可能跨行——本场景 patch 都是单行列表）
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
print("removed noise triggers:", len(removed))
for k, t in removed:
    print("  ", k, "->", t)
