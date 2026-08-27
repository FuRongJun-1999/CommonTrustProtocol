# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v10：新矛盾域（婚嫁/育儿/居住/医疗/教育分流/数字沉迷/乡村/旅游）

v1-v9 已覆盖 43 域 88 矛盾 529 题。v10 新域（生活实际矛盾细化）：
  1. 彩礼：婚嫁成本 vs 爱情/家庭负担
  2. 丧偶式育儿：育儿分工 vs 父亲缺席
  3. 房地产：房价/房贷 vs 居住需求
  4. 医疗保障：看病贵 vs 医保/生存
  5. 教育分流：中考分流/职高 vs 大学路
  6. 短视频沉迷：即时快乐 vs 时间/专注
  7. 农村空心化：进城发展 vs 乡村凋零
  8. 旅游乱象：景区商业化/宰客 vs 体验
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "fam-betrothal", "domain": "婚嫁家庭", "need": "婚姻的纯粹",
     "conflict": "彩礼习俗 vs 爱情/小家庭负担",
     "linked": ["fam-gener", "fam-couple"],
     "thesis": ["为什么彩礼越来越高？",
                "彩礼是卖女儿还是诚意？"],
     "antithesis": ["不给彩礼，女方家同意吗？",
                    "爱情为什么要用钱证明？"],
     "synthesis": ["彩礼多少才合理？",
                   "彩礼和嫁妆怎么平衡两家？"]},
    {"id": "fam-parenting", "domain": "婚嫁家庭", "need": "育儿公平",
     "conflict": "育儿分工 vs 父亲缺席",
     "linked": ["gen-house", "fam-couple"],
     "thesis": ["为什么育儿都是妈妈的事？",
                "爸爸去哪儿了？"],
     "antithesis": ["爸爸负责赚钱养家，还不够吗？",
                    "男人天生不会带孩子吗？"],
     "synthesis": ["育儿怎么分工才公平？",
                   "怎么让爸爸参与育儿？"]},
    {"id": "housing", "domain": "居住生活", "need": "安居",
     "conflict": "房价/房贷 vs 居住需求",
     "linked": ["fam-birth", "soc-urban"],
     "thesis": ["为什么房价这么高？",
                "年轻人买不起房怎么办？"],
     "antithesis": ["房价跌了，买房的人亏了怎么办？",
                    "不买房，租房过一辈子行吗？"],
     "synthesis": ["怎么住得起又住得好？",
                   "房子是必需品还是投资品？"]},
    {"id": "medical-cost", "domain": "医疗健康", "need": "看得起病",
     "conflict": "看病贵 vs 医保/生存",
     "linked": ["soc-doctor", "soc-aging"],
     "thesis": ["为什么看病这么贵？",
                "一场大病为什么能拖垮一个家？"],
     "antithesis": ["医生工资高一点有错吗？",
                    "看病贵是医院黑心还是本来就这么贵？"],
     "synthesis": ["怎么看得起病又不浪费医疗？",
                   "医保怎么才够用？"]},
    {"id": "edu-track", "domain": "教育制度", "need": "人人有出路",
     "conflict": "中考分流/职高 vs 大学路",
     "linked": ["edu-score", "edu-job"],
     "thesis": ["为什么中考就要分流？",
                "职高生为什么被看不起？"],
     "antithesis": ["都去上大学，谁做技术工人？",
                    "分流早一点，不合适的人早点学技术不好吗？"],
     "synthesis": ["普高和职高怎么选？",
                   "职业教育怎么才有出路？"]},
    {"id": "digit-scroll", "domain": "数字生活", "need": "时间主权",
     "conflict": "短视频即时快乐 vs 时间/专注",
     "linked": ["self-lazy", "youth-game"],
     "thesis": ["为什么刷短视频停不下来？",
                "短视频为什么比书好看？"],
     "antithesis": ["刷短视频放松一下有错吗？",
                    "不看短视频，就落伍了吗？"],
     "synthesis": ["怎么刷而不沉迷？",
                   "短视频怎么利用而不是被利用？"]},
    {"id": "rural-hollow", "domain": "城乡发展", "need": "乡村生机",
     "conflict": "进城发展 vs 乡村凋零",
     "linked": ["soc-urban", "fam-leftbehind"],
     "thesis": ["为什么农村年轻人越来越少？",
                "农村越来越空，谁种地？"],
     "antithesis": ["进城打工赚钱有错吗？",
                    "年轻人留在农村有前途吗？"],
     "synthesis": ["农村怎么留住人？",
                   "乡村振兴靠什么？"]},
    {"id": "tourism-trap", "domain": "文旅消费", "need": "玩得开心",
     "conflict": "景区商业化/宰客 vs 旅游体验",
     "linked": ["gov-reg", "soc-consumer"],
     "thesis": ["为什么景区总宰客？",
                "旅游为什么越来越贵？"],
     "antithesis": ["景区不赚钱，怎么维护？",
                    "商家定价高一点就是宰客吗？"],
     "synthesis": ["怎么玩得开心不被坑？",
                   "旅游体验和景区赚钱怎么平衡？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v10.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v10", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v10: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
