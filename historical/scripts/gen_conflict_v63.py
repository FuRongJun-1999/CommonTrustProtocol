# -*- coding: utf-8 -*-
"""冲突测试集 v63：物理常识 9 + 文学常识 3 簇迁移（c14）"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ITEMS = [
    # 频率
    {"q": "什么是频率？", "domain": "频率", "stage": "正题",
     "need": "每秒振动次数", "conflict": "频率 vs 振动快慢"},
    {"q": "频率和声音有什么关系？", "domain": "频率", "stage": "反题",
     "need": "频率定音调", "conflict": "频率 vs 振动快慢"},
    # 波
    {"q": "什么是波？", "domain": "波", "stage": "正题",
     "need": "振动传播能量", "conflict": "波 vs 能量传递"},
    {"q": "波需要介质吗？", "domain": "波", "stage": "反题",
     "need": "机械波要电磁波不要", "conflict": "波 vs 能量传递"},
    # 振动
    {"q": "什么是振动？", "domain": "振动", "stage": "正题",
     "need": "平衡位置往复", "conflict": "振动 vs 往复运动"},
    {"q": "振动和声音什么关系？", "domain": "振动", "stage": "反题",
     "need": "声音来自振动", "conflict": "振动 vs 往复运动"},
    # 声音不能传播
    {"q": "为什么声音不能在真空里传播？", "domain": "声音不能传播", "stage": "正题",
     "need": "机械波需介质", "conflict": "声音不能传播 vs 介质需求"},
    {"q": "为什么太空听不到声音？", "domain": "声音不能传播", "stage": "反题",
     "need": "真空无介质", "conflict": "声音不能传播 vs 介质需求"},
    # 弹性
    {"q": "什么是弹性？", "domain": "弹性", "stage": "正题",
     "need": "变形恢复原状", "conflict": "弹性 vs 形变恢复"},
    {"q": "弹性形变和塑性形变有什么区别？", "domain": "弹性", "stage": "反题",
     "need": "可恢复不可恢复", "conflict": "弹性 vs 形变恢复"},
    # 梁的弯曲
    {"q": "什么是梁的弯曲？", "domain": "梁的弯曲", "stage": "正题",
     "need": "受弯上压下拉", "conflict": "梁的弯曲 vs 弯矩与应力"},
    {"q": "为什么混凝土梁要配筋？", "domain": "梁的弯曲", "stage": "反题",
     "need": "底部受拉配筋", "conflict": "梁的弯曲 vs 弯矩与应力"},
    # 混凝土
    {"q": "什么是混凝土？", "domain": "混凝土", "stage": "正题",
     "need": "水泥砂石水硬化", "conflict": "混凝土 vs 人造石材"},
    {"q": "混凝土为什么需要养护？", "domain": "混凝土", "stage": "反题",
     "need": "水化需水保湿", "conflict": "混凝土 vs 人造石材"},
    # 能级
    {"q": "什么是能级？", "domain": "能级", "stage": "正题",
     "need": "量子化能量状态", "conflict": "能级 vs 量子化能量"},
    {"q": "电子为什么会跃迁？", "domain": "能级", "stage": "反题",
     "need": "吸能跳高放能跳低", "conflict": "能级 vs 量子化能量"},
    # 能带
    {"q": "什么是能带？", "domain": "能带", "stage": "正题",
     "need": "能级重叠成带", "conflict": "能带 vs 固体电子态"},
    {"q": "为什么导体能导电？", "domain": "能带", "stage": "反题",
     "need": "禁带为零", "conflict": "能带 vs 固体电子态"},
    # 唐诗
    {"q": "什么是唐诗？", "domain": "唐诗", "stage": "正题",
     "need": "唐代诗歌巅峰", "conflict": "唐诗 vs 诗歌巅峰"},
    {"q": "李白和杜甫有什么区别？", "domain": "唐诗", "stage": "反题",
     "need": "浪漫现实", "conflict": "唐诗 vs 诗歌巅峰"},
    # 宋词
    {"q": "什么是宋词？", "domain": "宋词", "stage": "正题",
     "need": "长短句配乐", "conflict": "宋词 vs 长短句"},
    {"q": "宋词和唐诗有什么区别？", "domain": "宋词", "stage": "反题",
     "need": "长短句vs齐整", "conflict": "宋词 vs 长短句"},
    # 绝句
    {"q": "什么是绝句？", "domain": "绝句", "stage": "正题",
     "need": "四句短诗", "conflict": "绝句 vs 四句短诗"},
    {"q": "绝句和律诗有什么区别？", "domain": "绝句", "stage": "反题",
     "need": "四句vs八句", "conflict": "绝句 vs 四句短诗"},
]
with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v63.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v63", "conflicts": 12, "items": ITEMS}, f, ensure_ascii=False, indent=1)
print("v63 testset:", len(ITEMS), "题")
