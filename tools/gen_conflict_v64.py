# -*- coding: utf-8 -*-
"""冲突测试集 v64：学科常识 12 簇迁移（c15）"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ITEMS = [
    # 负反馈
    {"q": "什么是负反馈？", "domain": "负反馈", "stage": "正题",
     "need": "输出抑制输入", "conflict": "负反馈 vs 系统调节"},
    {"q": "生活里有哪些负反馈？", "domain": "负反馈", "stage": "反题",
     "need": "空调体温调节", "conflict": "负反馈 vs 系统调节"},
    # 香农熵
    {"q": "什么是香农熵？", "domain": "香农熵", "stage": "正题",
     "need": "信息量度量", "conflict": "香农熵 vs 信息量"},
    {"q": "熵和压缩什么关系？", "domain": "香农熵", "stage": "反题",
     "need": "压缩极限", "conflict": "香农熵 vs 信息量"},
    # 傅里叶变换
    {"q": "什么是傅里叶变换？", "domain": "傅里叶变换", "stage": "正题",
     "need": "正弦波分解", "conflict": "傅里叶变换 vs 信号分解"},
    {"q": "傅里叶变换有什么用？", "domain": "傅里叶变换", "stage": "反题",
     "need": "声音图像处理", "conflict": "傅里叶变换 vs 信号分解"},
    # 中心极限定理
    {"q": "什么是中心极限定理？", "domain": "中心极限定理", "stage": "正题",
     "need": "和近似正态", "conflict": "中心极限定理 vs 分布收敛"},
    {"q": "为什么中心极限定理重要？", "domain": "中心极限定理", "stage": "反题",
     "need": "统计推断基础", "conflict": "中心极限定理 vs 分布收敛"},
    # 贝叶斯推断
    {"q": "什么是贝叶斯推断？", "domain": "贝叶斯推断", "stage": "正题",
     "need": "证据更新信念", "conflict": "贝叶斯推断 vs 先验更新"},
    {"q": "检测阳性就一定有病吗？", "domain": "贝叶斯推断", "stage": "反题",
     "need": "假阳患病率", "conflict": "贝叶斯推断 vs 先验更新"},
    # 梯度下降法
    {"q": "什么是梯度下降？", "domain": "梯度下降法", "stage": "正题",
     "need": "负梯度迭代", "conflict": "梯度下降法 vs 最优化"},
    {"q": "什么是学习率？", "domain": "梯度下降法", "stage": "反题",
     "need": "步长控制", "conflict": "梯度下降法 vs 最优化"},
    # 正则化
    {"q": "什么是正则化？", "domain": "正则化", "stage": "正题",
     "need": "复杂度惩罚", "conflict": "正则化 vs 过拟合"},
    {"q": "L1和L2正则有什么区别？", "domain": "正则化", "stage": "反题",
     "need": "稀疏vs平滑", "conflict": "正则化 vs 过拟合"},
    # 强化学习
    {"q": "什么是强化学习？", "domain": "强化学习", "stage": "正题",
     "need": "试错奖励", "conflict": "强化学习 vs 试错奖励"},
    {"q": "强化学习和监督学习有什么区别？", "domain": "强化学习", "stage": "反题",
     "need": "奖励非标签", "conflict": "强化学习 vs 试错奖励"},
    # 黑洞
    {"q": "什么是黑洞？", "domain": "黑洞", "stage": "正题",
     "need": "光逃不出", "conflict": "黑洞 vs 引力塌缩"},
    {"q": "黑洞是怎么形成的？", "domain": "黑洞", "stage": "反题",
     "need": "大恒星塌缩", "conflict": "黑洞 vs 引力塌缩"},
    # 免疫系统
    {"q": "什么是免疫系统？", "domain": "免疫系统", "stage": "正题",
     "need": "防御病菌", "conflict": "免疫系统 vs 防御机制"},
    {"q": "免疫力越强越好吗？", "domain": "免疫系统", "stage": "反题",
     "need": "过强过敏", "conflict": "免疫系统 vs 防御机制"},
    # 内稳态
    {"q": "什么是内稳态？", "domain": "内稳态", "stage": "正题",
     "need": "内部稳定动态平衡", "conflict": "内稳态 vs 动态平衡"},
    {"q": "体温怎么维持稳定？", "domain": "内稳态", "stage": "反题",
     "need": "出汗发抖调节", "conflict": "内稳态 vs 动态平衡"},
    # 行列式
    {"q": "什么是行列式？", "domain": "行列式", "stage": "正题",
     "need": "方阵数值特征", "conflict": "行列式 vs 线性变换"},
    {"q": "行列式为0意味着什么？", "domain": "行列式", "stage": "反题",
     "need": "矩阵不可逆", "conflict": "行列式 vs 线性变换"},
]
with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v64.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v64", "conflicts": 12, "items": ITEMS}, f, ensure_ascii=False, indent=1)
print("v64 testset:", len(ITEMS), "题")
