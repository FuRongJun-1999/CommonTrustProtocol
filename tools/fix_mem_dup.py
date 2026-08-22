# -*- coding: utf-8 -*-
"""合并记忆簇重复 key：删旧场景版（line 1179），把场景词并入知识版（line 1143）"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
lines = src.splitlines()

# 提取 line 1179 完整行
scene_full = None
for i, line in enumerate(lines):
    if line.strip().startswith('"记忆": ["记得我"'):
        scene_full = line
        break
assert scene_full, "scene line not found"
print("scene line:", scene_full[:80])

# 提取场景词（去 "记忆": 前缀和末尾逗号）
inner = scene_full.strip()
inner = inner[len('"记忆": '):]
if inner.endswith(","):
    inner = inner[:-1]
scene_words = re.findall(r'"([^"]+)"', inner)
print("scene words:", scene_words)

# 找知识版 line 1143 完整行
know_full = None
know_idx = None
for i, line in enumerate(lines):
    if line.strip().startswith('"记忆": ["记忆"') or line.strip().startswith('"记忆": ["什么是记忆"'):
        know_full = line
        know_idx = i
        break
assert know_full, "knowledge line not found"
print("knowledge line:", know_full[:80])

# 知识版已有词 + 场景词 合并
know_inner = know_full.strip()
know_inner = know_inner[len('"记忆": '):]
if know_inner.endswith(","):
    know_inner = know_inner[:-1]
know_words = re.findall(r'"([^"]+)"', know_inner)
merged = list(dict.fromkeys(know_words + scene_words))
print("merged count:", len(merged))

# 重写知识版行
new_know = '    "记忆": [%s],' % ", ".join('"%s"' % t for t in merged)
# 删除场景版行（整行含换行）
scene_pos = src.find(scene_full)
scene_end = src.find("\n", scene_pos) + 1
src = src[:scene_pos] + src[scene_end:]
# 替换知识版
know_pos = src.find(know_full)
src = src[:know_pos] + new_know + src[know_pos + len(know_full):]

open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("记忆簇合并 OK:", len(merged), "词")
