# -*- coding: utf-8 -*-
"""c19 自然问法迁移测试集（15 簇）归档"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ITEMS = [
    {"q": "什么是信息差？", "theme": "信息差"},
    {"q": "怎么缩小信息差？", "theme": "信息差"},
    {"q": "什么是概念形成？", "theme": "概念形成"},
    {"q": "概念是怎么来的？", "theme": "概念形成"},
    {"q": "什么是混沌与蝴蝶效应？", "theme": "混沌与蝴蝶效应"},
    {"q": "蝴蝶效应是什么意思？", "theme": "混沌与蝴蝶效应"},
    {"q": "什么是混沌的边缘？", "theme": "混沌的边缘"},
    {"q": "大脑在混沌的边缘吗？", "theme": "混沌的边缘"},
    {"q": "什么是突触可塑性？", "theme": "突触可塑性"},
    {"q": "赫布定律是什么？", "theme": "突触可塑性"},
    {"q": "什么是辩证法？", "theme": "辩证法"},
    {"q": "辩证法的三大规律是什么？", "theme": "辩证法"},
    {"q": "什么是Kolmogorov复杂度？", "theme": "Kolmogorov复杂度"},
    {"q": "Kolmogorov复杂度和压缩什么关系？", "theme": "Kolmogorov复杂度"},
    {"q": "什么是小波变换？", "theme": "小波变换"},
    {"q": "小波变换和傅里叶有什么区别？", "theme": "小波变换"},
    {"q": "什么是自适应滤波？", "theme": "自适应滤波"},
    {"q": "降噪耳机怎么工作的？", "theme": "自适应滤波"},
    {"q": "什么是功率谱密度？", "theme": "功率谱密度"},
    {"q": "功率谱和频谱什么区别？", "theme": "功率谱密度"},
    {"q": "什么是高斯过程？", "theme": "高斯过程"},
    {"q": "高斯过程有什么用？", "theme": "高斯过程"},
    {"q": "什么是蒙特卡洛方法？", "theme": "蒙特卡洛方法"},
    {"q": "蒙特卡洛怎么算圆周率？", "theme": "蒙特卡洛方法"},
    {"q": "什么是排队论？", "theme": "排队论"},
    {"q": "银行几个窗口合适？", "theme": "排队论"},
    {"q": "什么是复分析？", "theme": "复分析"},
    {"q": "复数有什么用？", "theme": "复分析"},
    {"q": "什么是数值线性代数？", "theme": "数值线性代数"},
    {"q": "大矩阵怎么解方程组？", "theme": "数值线性代数"},
]
themes = ["信息差", "概念形成", "混沌与蝴蝶效应", "混沌的边缘", "突触可塑性", "辩证法",
          "Kolmogorov复杂度", "小波变换", "自适应滤波", "功率谱密度", "高斯过程",
          "蒙特卡洛方法", "排队论", "复分析", "数值线性代数"]
with open(r"D:\Program Files\2_ai\CommonTrustProtocol\testsets\migration\natural_variants_c19.json", "w", encoding="utf-8") as f:
    json.dump({"name": "natural_variants_c19", "themes": themes, "items": ITEMS}, f, ensure_ascii=False, indent=1)
print("c19 saved", len(ITEMS))
