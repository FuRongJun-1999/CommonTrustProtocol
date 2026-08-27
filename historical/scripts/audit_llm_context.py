# -*- coding: utf-8 -*-
"""审计：灵枢 → DeepSeek 调用的上下文组装（信噪比分析）
收集 respond() 注入 system/user 的全部内容源 + 长度估算"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
SRC = r'D:\Program Files\2_ai\CommonTrustProtocol\aeis\aeis\roleplay_chat.py'
src = open(SRC, encoding='utf-8').read()

print('=== respond() 上下文注入源（sys_parts 组装） ===')
# 找 sys_parts.append 和 _user_msg 构造
for m in re.finditer(r'sys_parts\.append\([^\n]{0,120}|_user_msg\s*=|_mem_text\s*=|mem_notes\s*\+=', src):
    ln = src[:m.start()].count('\n') + 1
    print(f'  line {ln}: {m.group(0)[:110]}')

print()
print('=== 长度控制点 ===')
for pat in [r'_recall_mem\([^\n]*', r'\[:100\]', r'\[:60\]', r'\[:80\]', r'limit[=:][^\n]*', r'\[-3:\]', r'\[:4\]', r'\[:2\]']:
    hits = [(src[:m.start()].count('\n')+1, m.group(0)) for m in re.finditer(pat, src)]
    if hits:
        print(f'  {pat}: {hits[:6]}')
