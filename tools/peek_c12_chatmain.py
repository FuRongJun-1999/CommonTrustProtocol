# -*- coding: utf-8 -*-
"""打印 chat() 主流程（def chat 到 _assemble 调用前）"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
src = open(r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\chat_engine.py', encoding='utf-8').read()
i = src.find('def chat(')
j = src.find('_assemble(message, hits, emotion)')
print(src[i:j+80])
