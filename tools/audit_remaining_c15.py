# -*- coding: utf-8 -*-
"""常识域剩余薄簇全景审计（c14 后快照）：<80字 簇按域分类，输出升级建议"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.semantic_translate as st
import importlib
importlib.reload(st)

# 全部 <80 字簇（在 REVERSE_DAILY 中且属于 DOMAIN/SYNONYM 簇）
thin = []
for k, v in st.REVERSE_DAILY.items():
    if len(v) < 80 and (k in st.DOMAIN_SYNONYM_CLUSTERS or k in st.SYNONYM_CLUSTERS):
        route = st.DOMAIN_ROUTE.get(k, 'synonym')
        thin.append((k, len(v), route))
thin.sort(key=lambda x: x[1])

# 按域分组（用 DOMAIN_ROUTE 或关键词粗分）
def bucket(k):
    if k in ('行列式','极限运算法则','梯度下降法','傅里叶变换','蒙特卡洛方法','中心极限定理',
             '贝叶斯推断','概率图模型','高斯过程','奇异值分解','凸优化','拉普拉斯变换','格林公式',
             '方向导数与梯度','施密特正交化','共轭梯度法','相似对角化','核与像','随机微分方程',
             '微分几何与流形','最优传输','不动点定理','分支限界法','回溯算法','排队论','多元极值',
             '生成函数','复分析','数值线性代数','小波变换','短时傅里叶变换','张量分解','谱图论',
             '拓扑','群论','张量','维数','特征值'):
        return '数学'
    if k in ('香农熵','互信息','KL散度','信道容量','率失真理论','数据压缩熵界','Kolmogorov复杂度',
             '信息瓶颈','奈奎斯特采样定理'):
        return '信息论'
    if k in ('Transformer','注意机制','注意力机制','扩散模型','强化学习','元学习','正则化',
             '偏差方差权衡','PAC学习','VC维','神经网络','深度学习','大模型','梯度下降法','交叉验证与信息准则'):
        return '机器学习'
    if k in ('PID控制','卡尔曼滤波','自适应滤波','滤波器组','负反馈','二阶控制论','李雅普诺夫稳定性',
             '功率谱密度','相空间与吸引子','混沌与蝴蝶效应','混沌的边缘','分岔理论','Kuramoto模型',
             '自组织临界性','复杂适应系统','涌现','网络科学'):
        return '控制/复杂系统'
    if k in ('元认知','自我认知','工作记忆','认知负荷理论','默认模式网络','突触可塑性','神经振荡',
             '预测编码','自由能原理','前额叶执行功能','认知偏差','概念形成','注意力机制'):
        return '认知科学'
    if k in ('黑洞','放射性衰变','免疫系统','内稳态','能级','能带','细胞','原子','介质','弹性'):
        return '基础科学'
    if k in ('唐诗','宋词','绝句','科学方法论','辩证法','唯物史观','模因论','合作博弈','囚徒困境',
             '机制设计','效用理论','合作演化','复制子方程','适应度景观'):
        return '人文社科'
    if k in ('月亮发光','天空蓝色','船浮水上','声音不能传播'):
        return '自然常识'
    return '其他'

groups = {}
for k, n, r in thin:
    b = bucket(k)
    groups.setdefault(b, []).append((k, n))

print(f'剩余 <80字 簇: {len(thin)}')
for b in sorted(groups, key=lambda x: -len(groups[x])):
    items = groups[b]
    print(f'\n== {b} ({len(items)}):')
    for k, n in items:
        print(f'  {k}: {n}ch')

# 保存快照
import json
snap = {b: [{"key": k, "len": n} for k, n in items] for b, items in groups.items()}
with open(r'D:\Program Files\2_ai\CommonTrustProtocol\tools\remaining_thin_snapshot.json', 'w', encoding='utf-8') as f:
    json.dump({"count": len(thin), "groups": snap}, f, ensure_ascii=False, indent=1)
print('\n快照已存 tools/remaining_thin_snapshot.json')
