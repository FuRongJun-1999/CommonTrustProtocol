# -*- coding: utf-8 -*-
"""批次9：master 最后 2 题 llm 兜底补直答（随机化算法/认知双过程）。"""
import sys

def patch(path):
    src = open(path, encoding="utf-8").read()
    # 簇：插在「科学方法论」簇后
    anchor_c = '''    "科学方法论": ["科学方法论", "什么是科学方法论", "可证伪", "证伪主义", "波普尔", "科学方法"],'''
    new_c = anchor_c + '''
    "随机化算法": ["随机化算法", "什么是随机化算法", "随机算法", "拉斯维加斯算法", "蒙特卡洛算法", "随机化"],
    "认知双过程": ["认知双过程", "双过程理论", "系统1", "系统2", "快思考", "慢思考", "直觉与推理"],'''
    assert anchor_c in src
    src = src.replace(anchor_c, new_c, 1)
    # 直答：插在「科学方法论」直答后
    anchor_d = '''    "科学方法论": "科学方法论：提出可证伪假设→可重复实验→数据验证——波普尔可证伪性（能被实验否定才是科学）；归纳（观测到规律）与演绎（规律推预测）结合",'''
    new_d = anchor_d + '''
    "随机化算法": "随机化算法：在算法中引入随机选择——拉斯维加斯算法（结果一定正确、时间随机，如随机化快排）、蒙特卡洛算法（结果可能错但概率小，如素数测试）；随机化简化分析并避免最坏情况",
    "认知双过程": "认知双过程理论（Kahneman）：系统1快思考——自动/直觉/低耗能（启发式，易偏差）；系统2慢思考——受控/分析/高耗能；日常大量判断靠系统1，复杂问题启动系统2",'''
    assert anchor_d in src
    src = src.replace(anchor_d, new_d, 1)
    open(path, "w", encoding="utf-8").write(src)
    print("patched")

patch(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py")
