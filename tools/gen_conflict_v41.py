# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v41：生活常识补盲批次（自主）

8 主题：煮鸡蛋变硬(蛋白质变性)/气球上天(密度)/空调滴水(冷凝)/牛奶冷藏(抑菌)/
饭后犯困(消化供血)/蚊子叮(吸引机制)/电梯失重(超重失重)/晒被子(紫外线除螨)
触发词规避：犯困→困簇、电梯→老旧小区簇、晒太阳→光合作用簇（长短语决胜）。
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "chem-egg", "domain": "煮鸡蛋", "need": "蛋白质变性",
     "conflict": "变性凝固 vs 熟了",
     "thesis": ["为什么煮鸡蛋会变硬？",
                "为什么鸡蛋变硬了？"],
     "antithesis": ["鸡蛋变硬是煮熟了？",
                    "鸡蛋煮多久会变硬？"],
     "synthesis": ["鸡蛋煮太久会怎样？",
                   "怎么判断鸡蛋煮熟了？"]},
    {"id": "phy-balloon", "domain": "气球上天", "need": "密度小于空气",
     "conflict": "浮力 vs 重量",
     "thesis": ["为什么气球会飞上天？",
                "气球为什么会飘起来？"],
     "antithesis": ["气球飞上天是气球变轻了？",
                    "所有气球都会飞？"],
     "synthesis": ["怎么让气球飞起来？",
                   "为什么氢气气球能飞？"]},
    {"id": "phy-ac", "domain": "空调滴水", "need": "冷凝水",
     "conflict": "冷凝 vs 故障",
     "thesis": ["为什么空调外机会滴水？",
                "空调为什么会滴水？"],
     "antithesis": ["空调滴水是坏了？",
                    "空调漏的是氟利昂？"],
     "synthesis": ["空调外机滴水怎么处理？",
                   "空调排水管堵了怎么办？"]},
    {"id": "bio-milk", "domain": "牛奶冷藏", "need": "低温抑菌",
     "conflict": "冷藏 vs 变质",
     "thesis": ["为什么牛奶要放冰箱？",
                "牛奶为什么容易坏？"],
     "antithesis": ["牛奶放冰箱就不会坏？",
                    "牛奶坏了还能喝？"],
     "synthesis": ["怎么判断牛奶变质了？",
                   "牛奶怎么保存不容易坏？"]},
    {"id": "bio-sleepy", "domain": "饭后犯困", "need": "消化供血",
     "conflict": "消化需要 vs 大脑供血",
     "thesis": ["为什么吃完饭会犯困？",
                "饭后为什么想睡觉？"],
     "antithesis": ["犯困是因为吃得太多？",
                    "吃饱了就该睡？"],
     "synthesis": ["饭后犯困怎么办？",
                   "怎么避免吃完饭犯困？"]},
    {"id": "bio-mosquito", "domain": "蚊子叮", "need": "二氧化碳体温汗味",
     "conflict": "吸引因素 vs 血型",
     "thesis": ["为什么蚊子爱叮我？",
                "蚊子为什么叮人？"],
     "antithesis": ["蚊子叮人是吸血？",
                    "血型招蚊子？"],
     "synthesis": ["怎么防蚊子叮？",
                   "被蚊子咬了怎么止痒？"]},
    {"id": "phy-elevator", "domain": "电梯失重", "need": "加速度感觉",
     "conflict": "失重超重 vs 掉下去",
     "thesis": ["为什么坐电梯会有失重感？",
                "电梯下行时为什么心慌？"],
     "antithesis": ["失重是电梯掉下去了？",
                    "电梯加速上行也难受？"],
     "synthesis": ["电梯失重感怎么缓解？",
                   "为什么电梯上升有超重感？"]},
    {"id": "life-quilt", "domain": "晒被子", "need": "紫外线除螨",
     "conflict": "杀菌除螨 vs 晒热",
     "thesis": ["被子晒了有什么用？",
                "晒被子有什么好处？"],
     "antithesis": ["晒被子是把被子晒热？",
                    "阴天晒被子没用？"],
     "synthesis": ["怎么晒被子最好？",
                   "晒被子要不要拍打？"]},
]

items = []
for c in CONFLICTS:
    for q in c["thesis"]:
        items.append({"q": q, "conflict_id": c["id"], "domain": c["domain"],
                      "stage": "正题", "need": c["need"], "conflict": c["conflict"]})
    for q in c["antithesis"]:
        items.append({"q": q, "conflict_id": c["id"], "domain": c["domain"],
                      "stage": "反题", "need": c["need"], "conflict": c["conflict"]})
    for q in c["synthesis"]:
        items.append({"q": q, "conflict_id": c["id"], "domain": c["domain"],
                      "stage": "合题", "need": c["need"], "conflict": c["conflict"]})

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v41.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v41", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v41: {len(CONFLICTS)} 主题，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}")
