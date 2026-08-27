# -*- coding: utf-8 -*-
"""定位 c12 旧答案文本在源文件中的所有出现位置"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
src = open(r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py', encoding='utf-8').read()
lines = src.splitlines()

# 旧答案关键片段
frags = {
    '手机充电': '手机没电说明电池里的能量用完了',
    '饿了吃饭': '饿了是身体能量不足的信号',
    '洗手防病': '洗手能洗掉手上的细菌病毒',
    '喝水规律': '规律喝水保持身体水分平衡',
    '蔬果营养': '蔬菜水果富含维生素和膳食纤维',
    '节水节电': '节约用电随手关灯',
    '节约用水': '节约用水珍惜水资源',
    '垃圾入桶': '垃圾扔进垃圾桶',
    '下雨打伞': '下雨天打伞能挡住雨水',
    '晚上睡觉': '晚上睡觉是让身体休息',
    '烧水去氯': '水烧开后能去除部分氯气',
    '冬天穿衣': '冬天穿厚衣服能保暖',
    '吃早饭': '吃早饭给身体补充上午',
    '洗澡降温': '洗澡能清洁身体',
    '夏天出汗': '夏天出汗是身体散热降温',
    '开水晾凉': '热水晾一晾变凉再喝',
    '窗户起雾': '室内热空气遇到冷的玻璃窗',
}
for k, frag in frags.items():
    hits = [i+1 for i, ln in enumerate(lines) if frag in ln]
    print(f'{k}: {hits}')
