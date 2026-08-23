# -*- coding: utf-8 -*-
"""c22 自然问法迁移测试集（收尾 16 簇）归档"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ITEMS = [
    {"q": "什么是对抗鲁棒性？", "theme": "对抗鲁棒性"},
    {"q": "对抗样本是什么？", "theme": "对抗鲁棒性"},
    {"q": "什么是PAC学习？", "theme": "PAC学习"},
    {"q": "什么是概率近似正确？", "theme": "PAC学习"},
    {"q": "什么是概率图模型？", "theme": "概率图模型"},
    {"q": "贝叶斯网络是什么？", "theme": "概率图模型"},
    {"q": "什么是扩散模型？", "theme": "扩散模型"},
    {"q": "Stable Diffusion怎么工作的？", "theme": "扩散模型"},
    {"q": "什么是凸优化？", "theme": "凸优化"},
    {"q": "凸优化为什么有全局最优？", "theme": "凸优化"},
    {"q": "什么是注意机制？", "theme": "注意机制"},
    {"q": "自注意力是什么？", "theme": "注意机制"},
    {"q": "什么是希尔伯特空间？", "theme": "希尔伯特空间"},
    {"q": "函数怎么看成向量？", "theme": "希尔伯特空间"},
    {"q": "什么是标度律？", "theme": "标度律"},
    {"q": "代谢率为什么是体重的3/4次方？", "theme": "标度律"},
    {"q": "什么是自由能原理？", "theme": "自由能原理"},
    {"q": "大脑怎么最小化自由能？", "theme": "自由能原理"},
    {"q": "什么是滤波器组？", "theme": "滤波器组"},
    {"q": "子带编码是什么？", "theme": "滤波器组"},
    {"q": "什么是极限运算法则？", "theme": "极限运算法则"},
    {"q": "0/0型的极限怎么求？", "theme": "极限运算法则"},
    {"q": "什么是色谱法？", "theme": "色谱法"},
    {"q": "HPLC是什么？", "theme": "色谱法"},
    {"q": "什么是元学习？", "theme": "元学习"},
    {"q": "few-shot学习是什么？", "theme": "元学习"},
    {"q": "什么是Transformer？", "theme": "Transformer"},
    {"q": "为什么Transformer能并行？", "theme": "Transformer"},
    {"q": "什么是注意力机制？", "theme": "注意力机制"},
    {"q": "注意力机制和Transformer什么关系？", "theme": "注意力机制"},
    {"q": "什么是Kuramoto模型？", "theme": "Kuramoto模型"},
    {"q": "萤火虫为什么会同步闪光？", "theme": "Kuramoto模型"},
]
themes = ["对抗鲁棒性", "PAC学习", "概率图模型", "扩散模型", "凸优化", "注意机制",
          "希尔伯特空间", "标度律", "自由能原理", "滤波器组", "极限运算法则", "色谱法",
          "元学习", "Transformer", "注意力机制", "Kuramoto模型"]
with open(r"D:\Program Files\2_ai\CommonTrustProtocol\testsets\migration\natural_variants_c22.json", "w", encoding="utf-8") as f:
    json.dump({"name": "natural_variants_c22", "themes": themes, "items": ITEMS}, f, ensure_ascii=False, indent=1)
print("c22 saved", len(ITEMS))
