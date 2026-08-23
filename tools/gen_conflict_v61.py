# -*- coding: utf-8 -*-
"""冲突测试集 v61：生活常识 17 簇迁移（c12）"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ITEMS = [
    # 手机充电
    {"q": "手机没电了为什么要充电？", "domain": "手机充电", "stage": "正题",
     "need": "电池能量耗尽", "conflict": "手机充电 vs 电池能量"},
    {"q": "手机电池怎么充电才不伤电池？", "domain": "手机充电", "stage": "合题",
     "need": "随用随充避免过充", "conflict": "手机充电 vs 电池能量"},
    # 下雨打伞
    {"q": "下雨天为什么要打伞？", "domain": "下雨打伞", "stage": "正题",
     "need": "防淋湿防着凉", "conflict": "下雨打伞 vs 防水"},
    {"q": "伞为什么能挡住雨？", "domain": "下雨打伞", "stage": "反题",
     "need": "防水伞面弧形导水", "conflict": "下雨打伞 vs 防水"},
    # 晚上睡觉
    {"q": "为什么要晚上睡觉？", "domain": "晚上睡觉", "stage": "正题",
     "need": "生物钟身体修复", "conflict": "晚上睡觉 vs 睡眠恢复"},
    {"q": "睡多久合适？", "domain": "晚上睡觉", "stage": "合题",
     "need": "成年人7-8小时", "conflict": "晚上睡觉 vs 睡眠恢复"},
    # 开水晾凉
    {"q": "开水为什么要晾凉再喝？", "domain": "开水晾凉", "stage": "正题",
     "need": "防烫伤食道", "conflict": "开水晾凉 vs 温度安全"},
    {"q": "喝太烫的水有什么危害？", "domain": "开水晾凉", "stage": "反题",
     "need": "65度以上伤黏膜", "conflict": "开水晾凉 vs 温度安全"},
    # 饿了吃饭
    {"q": "饿了为什么要吃饭？", "domain": "饿了吃饭", "stage": "正题",
     "need": "血糖低信号补能量", "conflict": "饿了吃饭 vs 能量补充"},
    {"q": "饿过头会怎样？", "domain": "饿了吃饭", "stage": "反题",
     "need": "低血糖头晕", "conflict": "饿了吃饭 vs 能量补充"},
    # 烧水去氯
    {"q": "水为什么要烧开了喝？", "domain": "烧水去氯", "stage": "正题",
     "need": "杀菌去余氯", "conflict": "烧水去氯 vs 饮用水安全"},
    {"q": "烧水能去掉什么？", "domain": "烧水去氯", "stage": "反题",
     "need": "余氯挥发", "conflict": "烧水去氯 vs 饮用水安全"},
    # 窗户起雾
    {"q": "冬天窗户为什么会起雾？", "domain": "窗户起雾", "stage": "正题",
     "need": "水蒸气遇冷液化", "conflict": "窗户起雾 vs 液化"},
    {"q": "怎么防止窗户起雾？", "domain": "窗户起雾", "stage": "合题",
     "need": "通风除湿防雾剂", "conflict": "窗户起雾 vs 液化"},
    # 夏天出汗
    {"q": "夏天为什么容易出汗？", "domain": "夏天出汗", "stage": "正题",
     "need": "体温调节散热", "conflict": "夏天出汗 vs 散热降温"},
    {"q": "出汗后怎么补水？", "domain": "夏天出汗", "stage": "合题",
     "need": "补水补盐少量多次", "conflict": "夏天出汗 vs 散热降温"},
    # 冬天穿衣
    {"q": "冬天为什么要穿厚衣服？", "domain": "冬天穿衣", "stage": "正题",
     "need": "空气层保温", "conflict": "冬天穿衣 vs 保温"},
    {"q": "穿什么最保暖？", "domain": "冬天穿衣", "stage": "合题",
     "need": "羽绒羊毛锁空气", "conflict": "冬天穿衣 vs 保温"},
    # 洗手防病
    {"q": "为什么要洗手？", "domain": "洗手防病", "stage": "正题",
     "need": "洗掉细菌病毒", "conflict": "洗手防病 vs 细菌病毒"},
    {"q": "怎么洗才干净？", "domain": "洗手防病", "stage": "合题",
     "need": "肥皂流水20秒", "conflict": "洗手防病 vs 细菌病毒"},
    # 洗澡降温
    {"q": "夏天冲凉能降温吗？", "domain": "洗澡降温", "stage": "正题",
     "need": "水带走皮肤热量", "conflict": "洗澡降温 vs 散热"},
    {"q": "洗冷水澡还是温水澡好？", "domain": "洗澡降温", "stage": "反题",
     "need": "温水扩张血管散热", "conflict": "洗澡降温 vs 散热"},
    # 吃早饭
    {"q": "为什么吃早饭很重要？", "domain": "吃早饭", "stage": "正题",
     "need": "补充血糖启动代谢", "conflict": "吃早饭 vs 空腹危害"},
    {"q": "不吃早饭会怎样？", "domain": "吃早饭", "stage": "反题",
     "need": "伤胃胆结石风险", "conflict": "吃早饭 vs 空腹危害"},
    # 喝水规律
    {"q": "为什么要按时喝水？", "domain": "喝水规律", "stage": "正题",
     "need": "口渴已缺水", "conflict": "喝水规律 vs 水分平衡"},
    {"q": "一天喝多少水合适？", "domain": "喝水规律", "stage": "合题",
     "need": "8杯1500-1700ml", "conflict": "喝水规律 vs 水分平衡"},
    # 蔬果营养
    {"q": "为什么要多吃蔬菜水果？", "domain": "蔬果营养", "stage": "正题",
     "need": "维生素膳食纤维", "conflict": "蔬果营养 vs 维生素膳食纤维"},
    {"q": "果汁能代替水果吗？", "domain": "蔬果营养", "stage": "反题",
     "need": "丢纤维糖浓缩", "conflict": "蔬果营养 vs 维生素膳食纤维"},
    # 垃圾入桶
    {"q": "为什么要垃圾分类入桶？", "domain": "垃圾入桶", "stage": "正题",
     "need": "统一清运防污染", "conflict": "垃圾入桶 vs 环境整洁"},
    {"q": "乱扔垃圾有什么危害？", "domain": "垃圾入桶", "stage": "反题",
     "need": "污染滋生蚊蝇", "conflict": "垃圾入桶 vs 环境整洁"},
    # 节约用水
    {"q": "为什么要节约用水？", "domain": "节约用水", "stage": "正题",
     "need": "淡水仅占2.5%", "conflict": "节约用水 vs 水资源"},
    {"q": "怎么节约用水？", "domain": "节约用水", "stage": "合题",
     "need": "关紧水龙头一水多用", "conflict": "节约用水 vs 水资源"},
    # 节水节电
    {"q": "为什么要节约用电？", "domain": "节水节电", "stage": "正题",
     "need": "火电排碳减排", "conflict": "节水节电 vs 能源消耗"},
    {"q": "待机也耗电吗？", "domain": "节水节电", "stage": "反题",
     "need": "待机耗电5-10%", "conflict": "节水节电 vs 能源消耗"},
]
with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v61.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v61", "conflicts": 17, "items": ITEMS}, f, ensure_ascii=False, indent=1)
print("v61 testset:", len(ITEMS), "题")
