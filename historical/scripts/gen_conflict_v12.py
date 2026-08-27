# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v12：新矛盾域（应届生就业/电信诈骗/直播打赏/医美整容/月嫂月子/儿童近视/广场舞/光盘行动）

v1-v11 已覆盖 59 域 101 矛盾 625 题。v12 新域（生活矛盾再细化）：
  1. 应届生就业：毕业就失业 vs 第一份工作选择
  2. 电信诈骗：老人被骗 vs 反诈
  3. 直播打赏：打赏主播 vs 钱/理性
  4. 医美整容：变美需求 vs 手术风险
  5. 月嫂月子：花钱请月嫂 vs 值不值/家人带
  6. 儿童近视：电子产品 vs 视力保护
  7. 广场舞：老人健身 vs 噪音扰民
  8. 光盘行动：面子/点多了 vs 浪费
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "edu-graduate", "domain": "职业起步", "need": "第一份工作",
     "conflict": "毕业就失业 vs 岗位需求错配",
     "linked": ["edu-job", "study-kaoyan"],
     "thesis": ["为什么毕业就失业？",
                "第一份工作怎么选？"],
     "antithesis": ["先就业再择业，有错吗？",
                    "第一份工作必须对口吗？"],
     "synthesis": ["怎么找到第一份工作？",
                   "第一份工作看重什么？"]},
    {"id": "digit-scam", "domain": "数字安全", "need": "守住钱袋子",
     "conflict": "诈骗手段升级 vs 老人防范薄弱",
     "linked": ["age-digital", "digit-privacy"],
     "thesis": ["为什么老人容易被骗？",
                "电信诈骗怎么防？"],
     "antithesis": ["被骗是老人糊涂吗？",
                    "被骗的钱还能追回来吗？"],
     "synthesis": ["怎么让老人不被骗？",
                   "反诈怎么才有效？"]},
    {"id": "digit-tipping", "domain": "数字消费", "need": "打赏的理性",
     "conflict": "打赏主播 vs 钱/理性",
     "linked": ["digit-live", "youth-idol"],
     "thesis": ["为什么有人花那么多钱打赏？",
                "打赏的人傻吗？"],
     "antithesis": ["打赏是支持主播，有错吗？",
                    "花自己的钱打赏，别人管得着吗？"],
     "synthesis": ["怎么理性看待打赏？",
                   "未成年人打赏怎么管？"]},
    {"id": "med-cosmetic", "domain": "健康消费", "need": "变美的自由",
     "conflict": "变美需求 vs 手术风险",
     "linked": ["psy-appearance", "medical-cost"],
     "thesis": ["为什么越来越多人整容？",
                "整容有风险吗？"],
     "antithesis": ["变美有错吗？",
                    "整容是自信还是自卑？"],
     "synthesis": ["整容还是不整容怎么选？",
                   "医美怎么避坑？"]},
    {"id": "fam-yuesao", "domain": "家庭养育", "need": "月子有保障",
     "conflict": "请月嫂花钱 vs 家人带/值不值",
     "linked": ["fam-birth", "fam-parenting"],
     "thesis": ["为什么月嫂这么贵？",
                "请月嫂有必要吗？"],
     "antithesis": ["婆婆妈妈带娃不行吗？",
                    "月嫂的钱花得值吗？"],
     "synthesis": ["月嫂还是家人带，怎么选？",
                   "月子怎么坐才科学？"]},
    {"id": "health-myopia", "domain": "健康生活", "need": "孩子视力",
     "conflict": "电子产品/作业 vs 视力保护",
     "linked": ["digit-scroll", "edu-score"],
     "thesis": ["为什么孩子近视越来越多？",
                "近视是遗传还是玩手机？"],
     "antithesis": ["不玩手机，作业也伤眼啊？",
                    "近视了戴眼镜就行吗？"],
     "synthesis": ["怎么保护孩子的视力？",
                   "近视防控怎么做？"]},
    {"id": "city-square", "domain": "社区生活", "need": "锻炼有去处",
     "conflict": "老人健身需求 vs 周边安宁",
     "linked": ["public-civility", "fam-solitude"],
     "thesis": ["为什么广场舞总有矛盾？",
                "广场舞扰民该不该管？"],
     "antithesis": ["老人跳个舞怎么了？",
                    "不让跳广场舞，老人去哪锻炼？"],
     "synthesis": ["广场舞和安宁怎么平衡？",
                   "广场舞怎么跳不扰民？"]},
    {"id": "food-waste", "domain": "饮食文化", "need": "不浪费",
     "conflict": "面子/点多了 vs 粮食浪费",
     "linked": ["plastic-waste", "soc-consumer"],
     "thesis": ["为什么浪费食物这么普遍？",
                "光盘行动为什么难？"],
     "antithesis": ["点多了浪费，点少了不够吃？",
                    "打包丢人吗？"],
     "synthesis": ["怎么做到不浪费？",
                   "请客吃饭怎么不浪费？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v12.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v12", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v12: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
