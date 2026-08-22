# -*- coding: utf-8 -*-
"""合并记忆簇重复 key：line 1143（知识版16词）+ line 1179（记忆询问场景版）
把场景词并入知识版，删除重复的旧 key（否则后覆盖前导致知识版失效）"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
lines = src.splitlines()

# 提取 line 1179 的场景词（记得我/想我吗...）
scene_line = None
for i, line in enumerate(lines):
    if line.strip().startswith('"记忆": ["记得我"'):
        scene_line = i
        break
print("scene line:", scene_line + 1 if scene_line is not None else None)
if scene_line is None:
    # 用行内容匹配
    for i, line in enumerate(lines):
        if '"记得我"' in line and '"记忆"' in line:
            scene_line = i
            break
print("scene line (2nd):", scene_line + 1 if scene_line is not None else None)

# 直接操作 src：找 line 1179 的完整行删除，并把场景词加到 line 1143
scene_str = None
for i, line in enumerate(lines):
    if '"记得我"' in line:
        scene_str = line.strip()
        break
print("scene_str:", scene_str[:60] if scene_str else None)
