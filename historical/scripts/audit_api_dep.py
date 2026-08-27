# -*- coding: utf-8 -*-
"""分析：灵枢 API 依赖点（启动链 + 对话链）——定位离线自维持的改造点"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
SITE = r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages'

# 1. chat_engine 的 LLM 调用点
src = open(SITE + r'\wisdom\chat_engine.py', encoding='utf-8').read()
print('=== chat_engine.py LLM/API 相关 ===')
for m in re.finditer(r'(api|deepseek|llm|openai|request|chat_completion|completion|LLM\()', src):
    ln = src[:m.start()].count('\n') + 1
    line = src.splitlines()[ln-1].strip()[:90]
    if 'def ' not in line:
        print(f'  line {ln}: {line}')
