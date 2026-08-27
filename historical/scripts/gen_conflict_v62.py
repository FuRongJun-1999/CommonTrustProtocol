# -*- coding: utf-8 -*-
"""冲突测试集 v62：简单事实·自然·工程·基础科学 12 簇迁移（c13）"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ITEMS = [
    # 一年月数
    {"q": "一年有多少个月？", "domain": "一年月数", "stage": "正题",
     "need": "12个月历法约定", "conflict": "一年月数 vs 历法时间"},
    {"q": "2月为什么只有28天？", "domain": "一年月数", "stage": "反题",
     "need": "罗马历法沿革", "conflict": "一年月数 vs 历法时间"},
    # 一周天数
    {"q": "一周有几天？", "domain": "一周天数", "stage": "正题",
     "need": "7天人为约定", "conflict": "一周天数 vs 历法周期"},
    {"q": "星期是怎么来的？", "domain": "一周天数", "stage": "反题",
     "need": "7天体崇拜", "conflict": "一周天数 vs 历法周期"},
    # 一天小时
    {"q": "一天有多少个小时？", "domain": "一天小时", "stage": "正题",
     "need": "24小时自转", "conflict": "一天小时 vs 地球自转"},
    {"q": "一小时为什么是60分钟？", "domain": "一天小时", "stage": "反题",
     "need": "巴比伦六十进制", "conflict": "一天小时 vs 地球自转"},
    # 天空蓝色
    {"q": "为什么天空是蓝色的？", "domain": "天空蓝色", "stage": "正题",
     "need": "瑞利散射蓝光", "conflict": "天空蓝色 vs 瑞利散射"},
    {"q": "为什么傍晚天空变红？", "domain": "天空蓝色", "stage": "反题",
     "need": "光路径长蓝光散尽", "conflict": "天空蓝色 vs 瑞利散射"},
    # 月亮发光
    {"q": "月亮为什么会发光？", "domain": "月亮发光", "stage": "正题",
     "need": "反射太阳光", "conflict": "月亮发光 vs 反射阳光"},
    {"q": "为什么月亮形状会变？", "domain": "月亮发光", "stage": "反题",
     "need": "日地月位置月相", "conflict": "月亮发光 vs 反射阳光"},
    # 船浮水上
    {"q": "为什么船能浮在水上？", "domain": "船浮水上", "stage": "正题",
     "need": "浮力排开水", "conflict": "船浮水上 vs 浮力"},
    {"q": "铁做的船为什么不沉？", "domain": "船浮水上", "stage": "反题",
     "need": "空心平均密度小", "conflict": "船浮水上 vs 浮力"},
    # 应力
    {"q": "什么是应力？", "domain": "应力", "stage": "正题",
     "need": "单位面积内力", "conflict": "应力 vs 内力分布"},
    {"q": "应力大了会怎样？", "domain": "应力", "stage": "反题",
     "need": "超过强度破坏", "conflict": "应力 vs 内力分布"},
    # 短路
    {"q": "什么是短路？", "domain": "短路", "stage": "正题",
     "need": "无负载直接连通", "conflict": "短路 vs 电流通路"},
    {"q": "短路为什么会起火？", "domain": "短路", "stage": "反题",
     "need": "大电流发热", "conflict": "短路 vs 电流通路"},
    # 混凝土钢筋
    {"q": "为什么混凝土要加钢筋？", "domain": "混凝土钢筋", "stage": "正题",
     "need": "补抗拉短板", "conflict": "混凝土钢筋 vs 材料互补"},
    {"q": "钢筋在混凝土里干什么？", "domain": "混凝土钢筋", "stage": "反题",
     "need": "受压抗拉分工", "conflict": "混凝土钢筋 vs 材料互补"},
    # 细胞
    {"q": "什么是细胞？", "domain": "细胞", "stage": "正题",
     "need": "生命基本单位", "conflict": "细胞 vs 生命单位"},
    {"q": "细胞怎么变多？", "domain": "细胞", "stage": "反题",
     "need": "分裂生长修复", "conflict": "细胞 vs 生命单位"},
    # 原子
    {"q": "什么是原子？", "domain": "原子", "stage": "正题",
     "need": "化学变化最小粒子", "conflict": "原子 vs 物质组成"},
    {"q": "原子里面有什么？", "domain": "原子", "stage": "反题",
     "need": "原子核电子", "conflict": "原子 vs 物质组成"},
    # 介质
    {"q": "为什么声音需要介质？", "domain": "介质", "stage": "正题",
     "need": "机械波传播条件", "conflict": "介质 vs 传播条件"},
    {"q": "真空里能听到声音吗？", "domain": "介质", "stage": "反题",
     "need": "真空无声", "conflict": "介质 vs 传播条件"},
]
with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v62.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v62", "conflicts": 12, "items": ITEMS}, f, ensure_ascii=False, indent=1)
print("v62 testset:", len(ITEMS), "题")
