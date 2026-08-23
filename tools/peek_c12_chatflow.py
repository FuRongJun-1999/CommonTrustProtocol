# -*- coding: utf-8 -*-
"""定位 chat() 主流程：fp 直答为何没生效 + 搜索收敛路径"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
src = open(r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\chat_engine.py', encoding='utf-8').read()

# 1. 搜索收敛文本位置
i = src.find('搜索收敛')
print('=== 搜索收敛 上下文 ===')
print(src[max(0,i-800):i+200])

# 2. _assemble 调用点
print('=== _assemble( 调用点 ===')
for m in re.finditer(r'_assemble\(', src):
    ln = src[:m.start()].count('\n') + 1
    print(f'  line {ln}: {src[m.start()-100:m.start()+150]!r}')
