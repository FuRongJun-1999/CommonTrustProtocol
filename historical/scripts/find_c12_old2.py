# -*- coding: utf-8 -*-
"""全局搜索旧答案片段（wisdom 目录 + 相关路径）"""
import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')
root = r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom'
frags = ['手机没电说明电池里的能量用完了', '饿了是身体能量不足的信号', '洗手能洗掉手上的细菌病毒',
         '规律喝水保持身体水分平衡', '蔬菜水果富含维生素和膳食纤维', '节约用电随手关灯',
         '下雨天打伞能挡住雨水', '晚上睡觉是让身体休息', '水烧开后能去除部分氯气',
         '冬天穿厚衣服能保暖', '吃早饭给身体补充上午', '洗澡能清洁身体',
         '夏天出汗是身体散热降温', '热水晾一晾变凉再喝', '室内热空气遇到冷的玻璃窗',
         '节约用水珍惜水资源', '垃圾扔进垃圾桶']
for fn in os.listdir(root):
    if not fn.endswith('.py'): continue
    p = os.path.join(root, fn)
    src = open(p, encoding='utf-8').read()
    for frag in frags:
        if frag in src:
            i = src.find(frag)
            lineno = src[:i].count('\n') + 1
            print(f'{fn}:{lineno} :: {frag}')
