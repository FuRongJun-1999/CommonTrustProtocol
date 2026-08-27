# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v17：新矛盾域（网约车安全/健身房跑路/充电桩安装/图书馆占座/儿童身高焦虑/宠物寄养/随份子/演唱会抢票）

v1-v16 已覆盖 99 域 141 矛盾 865 题。v17 新域（生活矛盾再细化）：
  1. 网约车安全：网约车便利 vs 安全/司机权益
  2. 健身房跑路：办卡优惠 vs 跑路风险
  3. 充电桩安装：装桩需求 vs 物业/安全阻力
  4. 图书馆占座：占座 vs 座位资源
  5. 儿童身高焦虑：比身高 vs 科学
  6. 宠物寄养：寄养 vs 宠物应激/费用
  7. 随份子：人情往来 vs 经济负担
  8. 演唱会抢票：抢票难 vs 黄牛
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "traffic-ridehailing", "domain": "出行服务", "need": "打车的安全",
     "conflict": "网约车便利 vs 安全/司机权益",
     "linked": ["gov-platform", "traffic-e"],
     "thesis": ["为什么网约车这么方便？",
                "网约车安全吗？"],
     "antithesis": ["网约车便宜，司机赚得少有错吗？",
                    "深夜打车，是不是自己不小心？"],
     "synthesis": ["怎么安全地打网约车？",
                   "网约车平台该管什么？"]},
    {"id": "fitness-card", "domain": "健身消费", "need": "健身的保障",
     "conflict": "办卡优惠 vs 跑路风险",
     "linked": ["fin-loan", "gov-reg"],
     "thesis": ["为什么健身房总跑路？",
                "办卡为什么这么便宜？"],
     "antithesis": ["健身房也是生意，先收钱有错吗？",
                    "办卡前自己不看，怪谁？"],
     "synthesis": ["怎么健身不被坑？",
                   "预付卡怎么防跑路？"]},
    {"id": "traffic-charge", "domain": "新能源出行", "need": "充电便利",
     "conflict": "装桩需求 vs 物业/安全阻力",
     "linked": ["traffic-e", "city-property"],
     "thesis": ["为什么装充电桩这么难？",
                "物业为什么不让装充电桩？"],
     "antithesis": ["物业也是为安全，有错吗？",
                    "没充电桩，电车怎么买？"],
     "synthesis": ["充电桩怎么装得成？",
                   "小区充电怎么解决？"]},
    {"id": "city-library", "domain": "公共空间", "need": "座位公平",
     "conflict": "占座 vs 座位资源",
     "linked": ["edu-score", "public-civility"],
     "thesis": ["为什么图书馆总有人占座？",
                "占座的人为什么理直气壮？"],
     "antithesis": ["占座是为学习，有错吗？",
                    "占座是常态，忍忍不行吗？"],
     "synthesis": ["图书馆座位怎么管？",
                   "备考人怎么抢到座位？"]},
    {"id": "health-height", "domain": "儿童健康", "need": "身高不焦虑",
     "conflict": "比身高 vs 科学/个体差异",
     "linked": ["psy-appearance", "health-weight"],
     "thesis": ["为什么家长都焦虑孩子身高？",
                "孩子长得慢就是不正常吗？"],
     "antithesis": ["担心孩子矮，有错吗？",
                    "打生长激素，是科学还是焦虑？"],
     "synthesis": ["怎么科学看待孩子身高？",
                   "孩子长不高怎么办？"]},
    {"id": "pet-boarding", "domain": "养宠服务", "need": "出门宠物有托付",
     "conflict": "寄养费用 vs 宠物应激/靠谱",
     "linked": ["city-pet", "pet-medical"],
     "thesis": ["为什么宠物寄养这么贵？",
                "宠物寄养靠谱吗？"],
     "antithesis": ["寄养是生意，赚钱有错吗？",
                    "宠物能自理，放家里不行吗？"],
     "synthesis": ["宠物寄养怎么选？",
                   "出门宠物怎么办？"]},
    {"id": "fam-giftmoney", "domain": "人情往来", "need": "人情不累",
     "conflict": "随份子 vs 经济负担",
     "linked": ["fam-wedding", "soc-consumer"],
     "thesis": ["为什么份子钱越随越多？",
                "随份子是人情还是负担？"],
     "antithesis": ["人情往来，有错吗？",
                    "不随份子，关系就淡了？"],
     "synthesis": ["份子钱怎么随不心疼？",
                   "人情往来怎么不累？"]},
    {"id": "culture-ticket", "domain": "演出消费", "need": "看到喜欢的演出",
     "conflict": "抢票难 vs 黄牛溢价",
     "linked": ["digit-live", "youth-idol"],
     "thesis": ["为什么演唱会票这么难抢？",
                "黄牛票为什么这么贵？"],
     "antithesis": ["演唱会溢价，是市场规律？",
                    "抢不到就不看，不行吗？"],
     "synthesis": ["怎么抢到原价票？",
                   "演出市场怎么治黄牛？"]},
]

items = []
for c in CONFLICTS:
    for q in c["thesis"]:
        items.append({"q": q, "conflict_id": c["id"], "domain": c["domain"],
                      "stage": "正题", "need": c["need"], "conflict": c["conflict"],
                      "linked": c.get("linked", [])})
    for q in c["antithesis"]:
        items.append({"q": q, "conflict_id": c["id"], "domain": c["domain"],
                      "stage": "反题", "need": c["need"], "conflict": c["conflict"],
                      "linked": c.get("linked", [])})
    for q in c["synthesis"]:
        items.append({"q": q, "conflict_id": c["id"], "domain": c["domain"],
                      "stage": "合题", "need": c["need"], "conflict": c["conflict"],
                      "linked": c.get("linked", [])})

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v17.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v17", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v17: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
