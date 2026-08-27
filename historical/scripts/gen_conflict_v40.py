# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v40：生活场景尝试问题（自主补盲批次）

用户授权自主补盲生活场景问题。v40 选 8 个最常见未覆盖主题（物理/化学/生活常识）：
  1. 雷声闪电：光速 vs 声速
  2. 瓶外水珠：冷凝现象
  3. 饺子浮起：密度变化
  4. 切洋葱：催泪物质
  5. 吸管吸饮料：大气压
  6. 泡泡彩色：薄膜干涉
  7. 磁铁吸铁：磁场/铁磁性
  8. 热水瓶保温：真空隔热
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "phy-thunder", "domain": "雷声闪电", "need": "光速大于声速",
     "conflict": "光速 vs 声速",
     "thesis": ["为什么先看到闪电后听到雷声？",
                "打雷时为什么闪电在前？"],
     "antithesis": ["闪电和雷声同时发生？",
                    "近距离打雷也先看到闪电吗？"],
     "synthesis": ["怎么算雷声离我们多远？",
                   "为什么雷声轰隆隆的？"]},
    {"id": "phy-condense", "domain": "瓶外水珠", "need": "水汽遇冷凝结",
     "conflict": "冷凝 vs 渗漏",
     "thesis": ["为什么冰可乐瓶外有水珠？",
                "可乐瓶为什么冒汗？"],
     "antithesis": ["水珠是瓶子漏出来的？",
                    "瓶子里的水跑出来了？"],
     "synthesis": ["怎么让杯子不冒水珠？",
                   "冬天眼镜起雾是为什么？"]},
    {"id": "phy-dumpling", "domain": "饺子浮起", "need": "熟了变轻浮起",
     "conflict": "密度变化 vs 熟了",
     "thesis": ["为什么饺子熟了会浮起来？",
                "饺子煮的时候为什么会浮上来？"],
     "antithesis": ["饺子浮起来是熟了吗？",
                    "生饺子也会浮起来？"],
     "synthesis": ["为什么饺子先沉底后浮起？",
                   "怎么判断饺子熟了？"]},
    {"id": "chem-onion", "domain": "切洋葱", "need": "催泪气体",
     "conflict": "催泪物质 vs 有毒",
     "thesis": ["为什么切洋葱会流泪？",
                "洋葱为什么会辣眼睛？"],
     "antithesis": ["切洋葱流泪是洋葱有毒？",
                    "只有切洋葱才流泪？"],
     "synthesis": ["怎么切洋葱不流泪？",
                   "洋葱辣眼睛怎么缓解？"]},
    {"id": "phy-straw", "domain": "吸管吸饮料", "need": "大气压",
     "conflict": "大气压 vs 嘴巴吸力",
     "thesis": ["为什么吸管能吸上饮料？",
                "用吸管喝水是什么原理？"],
     "antithesis": ["是嘴巴把水吸上来的？",
                    "吸管越长越费力？"],
     "synthesis": ["吸管吸不上来怎么办？",
                   "为什么吸管放水里能看到水上升？"]},
    {"id": "phy-bubble", "domain": "泡泡彩色", "need": "薄膜干涉",
     "conflict": "薄膜干涉 vs 颜料",
     "thesis": ["为什么肥皂泡是彩色的？",
                "为什么泡泡上有彩虹色？"],
     "antithesis": ["泡泡彩色是颜料染的？",
                    "只有肥皂泡才彩色？"],
     "synthesis": ["泡泡为什么会破？",
                   "怎么让泡泡不容易破？"]},
    {"id": "phy-magnet", "domain": "磁铁吸铁", "need": "铁磁性",
     "conflict": "磁场 vs 黏性",
     "thesis": ["为什么磁铁能吸铁？",
                "磁铁为什么能吸住铁？"],
     "antithesis": ["磁铁能吸所有金属？",
                    "磁铁吸铁是磁铁有黏性？"],
     "synthesis": ["磁铁为什么能吸别的东西？",
                   "怎么让磁铁失去磁性？"]},
    {"id": "phy-thermos", "domain": "热水瓶保温", "need": "隔热不加热",
     "conflict": "隔热 vs 加热",
     "thesis": ["为什么热水瓶能保温？",
                "热水瓶为什么能保热？"],
     "antithesis": ["热水瓶是加热的？",
                    "保温杯能一直热？"],
     "synthesis": ["热水瓶怎么选保温好？",
                   "为什么保温杯装冰水也保冷？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v40.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v40", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v40: {len(CONFLICTS)} 主题，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}")
