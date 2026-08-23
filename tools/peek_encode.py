# -*- coding: utf-8 -*-
"""查看 encode 函数实现（token 产出规则）"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
src = open(r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py', encoding='utf-8').read()
i = src.find('def encode')
print('位置:', i)
print(src[i:i+3000])
