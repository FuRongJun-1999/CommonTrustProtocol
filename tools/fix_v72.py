# -*- coding: utf-8 -*-
"""v72 修复：①恢复 DOMAIN_ROUTE 16 行（被答案覆盖）②在 REVERSE_DAILY 添加 16 簇答案
根因：pipeline apply_patches 的 '"key": "' 锚点误中 DOMAIN_ROUTE（新建簇 REVERSE_DAILY 无此 key）"""
import sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

SRC = r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py'
src = open(SRC, encoding='utf-8').read()
lines = src.splitlines(keepends=True)

KEYS = ['碳中和','碳达峰','温室效应','全球变暖','碳排放','温室气体','气候变化','新能源',
        '可再生能源','光伏','风力发电','电动汽车','锂电池','储能','绿色能源','双碳']

# 1. 恢复 DOMAIN_ROUTE：找以答案开头的污染行（含「是『」特征），替换为 "环境科学"
fixed = 0
for i, ln in enumerate(lines):
    for k in KEYS:
        if re.match(r'^\s*"' + k + r'": "什么是', ln):
            indent = ln[:len(ln) - len(ln.lstrip())]
            lines[i] = indent + '"' + k + '": "环境科学",\n'
            fixed += 1
            break
print(f'恢复 DOMAIN_ROUTE: {fixed} 行')

# 2. REVERSE_DAILY 添加 16 簇答案
patches = json.load(open(r'D:\Program Files\2_ai\CommonTrustProtocol\tools\patches_env.json', encoding='utf-8'))
i_rd = src.find('REVERSE_DAILY = {')
# 找 REVERSE_DAILY 字典闭合（括号深度）
depth = 0
end = -1
j = src.find('{', i_rd)
for k in range(j, len(src)):
    if src[k] == '{':
        depth += 1
    elif src[k] == '}':
        depth -= 1
        if depth == 0:
            end = k
            break
assert end > 0, 'REVERSE_DAILY 闭合未找到'

# 先检查这些 key 是否已在 REVERSE_DAILY（防重复）
import re as _re
existing = []
for p in patches:
    if _re.search('"' + p['key'] + r'"\s*:\s*"', src[i_rd:end]):
        existing.append(p['key'])
print('已在 REVERSE_DAILY 的 key（跳过）:', existing)

block = ''
added = 0
for p in patches:
    if p['key'] in existing:
        continue
    block += f'    "{p["key"]}": "{p["answer"]}",\n'
    added += 1
if block:
    src = src[:end] + '\n' + block + src[end:]
print(f'REVERSE_DAILY 新增: {added} 簇')

open(SRC, 'w', encoding='utf-8').write(src)

import py_compile
py_compile.compile(SRC, doraise=True)
print('语法 OK')

# 五副本同步
import shutil, hashlib
COPIES = [r'D:\Program Files\2_ai\knowledge-base\semantic_translate.py',
          r'D:\Program Files\2_ai\CommonTrustProtocol\aeis\wisdom\semantic_translate.py',
          r'D:\Program Files\1_ai\lingshu-wisdom\wisdom\semantic_translate.py',
          r'D:\Program Files\3_ai\lingshu-wisdom\wisdom\semantic_translate.py']
h0 = hashlib.sha256(open(SRC, 'rb').read()).hexdigest()[:12]
for c in COPIES:
    shutil.copy2(SRC, c)
print(f'五副本同步 [{h0}]')
