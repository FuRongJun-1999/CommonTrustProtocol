# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v15：新矛盾域（独居青年/培训贷/高考复读/隔代育儿/旧手机回收/社区团购/高铁餐饮/儿童零花钱）

v1-v14 已覆盖 83 域 125 矛盾 769 题。v15 新域（生活矛盾再细化）：
  1. 独居青年：独居 vs 孤独/生活管理
  2. 培训贷：培训先贷款 vs 就业承诺
  3. 高考复读：复读 vs 一年青春
  4. 隔代育儿：老人带娃 vs 教育理念
  5. 旧手机回收：旧手机处理 vs 数据隐私
  6. 社区团购：团购便宜 vs 菜市场/品质
  7. 高铁餐饮：高铁盒饭贵 vs 自带
  8. 儿童零花钱：零花钱 vs 理财教育
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "psy-single", "domain": "青年生活", "need": "独居的质量",
     "conflict": "独居自由 vs 孤独/生活管理",
     "linked": ["psy-lonely", "fam-birth"],
     "thesis": ["为什么越来越多人独居？",
                "独居是自由还是孤独？"],
     "antithesis": ["独居自由，有错吗？",
                    "独居久了会不会废掉？"],
     "synthesis": ["独居怎么不孤独？",
                   "独居生活怎么过得好？"]},
    {"id": "edu-trainingloan", "domain": "技能投资", "need": "学有所值",
     "conflict": "培训先贷款 vs 就业承诺",
     "linked": ["fin-loan", "edu-job"],
     "thesis": ["为什么培训总是先贷款？",
                "培训贷是馅饼还是陷阱？"],
     "antithesis": ["想学技能没钱，贷款有错吗？",
                    "培训机构也是生意，赚钱有错吗？"],
     "synthesis": ["怎么判断培训值不值？",
                   "想学技能怎么不踩坑？"]},
    {"id": "edu-gaokao", "domain": "升学选择", "need": "不留遗憾",
     "conflict": "复读一年 vs 青春/风险",
     "linked": ["edu-score", "study-kaoyan"],
     "thesis": ["为什么越来越多人复读？",
                "复读一年值吗？"],
     "antithesis": ["不甘心，再拼一年有错吗？",
                    "复读是机会还是逃避？"],
     "synthesis": ["复读还是走，怎么选？",
                   "复读怎么不后悔？"]},
    {"id": "fam-grandparenting", "domain": "家庭育儿", "need": "两代不冲突",
     "conflict": "老人带娃 vs 父母教育理念",
     "linked": ["fam-gener", "fam-parenting"],
     "thesis": ["为什么老人总要插手带娃？",
                "老人带娃有什么问题？"],
     "antithesis": ["老人帮忙带，还挑三拣四？",
                    "老人带娃省钱又省心，不好吗？"],
     "synthesis": ["隔代育儿怎么不吵架？",
                   "老人和父母怎么分工？"]},
    {"id": "digit-phone", "domain": "数字消费", "need": "旧物有归处",
     "conflict": "旧手机处理 vs 数据隐私/浪费",
     "linked": ["digit-privacy", "env-sort"],
     "thesis": ["旧手机怎么处理？",
                "旧手机回收安全吗？"],
     "antithesis": ["手机还能用，换什么换？",
                    "旧手机卖钱，有错吗？"],
     "synthesis": ["旧手机怎么处理最划算？",
                   "换手机怎么不浪费？"]},
    {"id": "soc-tuango", "domain": "社区消费", "need": "买菜又便宜又好",
     "conflict": "团购便宜 vs 菜市场/品质",
     "linked": ["digit-live", "food-safe"],
     "thesis": ["为什么社区团购这么便宜？",
                "社区团购靠谱吗？"],
     "antithesis": ["便宜不好吗？",
                    "团购抢了菜市场的生意？"],
     "synthesis": ["社区团购怎么选？",
                   "买菜去哪儿买？"]},
    {"id": "traffic-trainfood", "domain": "出行消费", "need": "路上吃得好",
     "conflict": "高铁盒饭贵 vs 自带/垄断",
     "linked": ["tourism-trap", "gov-reg"],
     "thesis": ["为什么高铁盒饭这么贵？",
                "高铁上为什么不能自带食物？"],
     "antithesis": ["高铁盒饭贵，有成本啊？",
                    "高铁餐饮是垄断吗？"],
     "synthesis": ["高铁吃饭怎么办？",
                   "高铁餐饮怎么改善？"]},
    {"id": "edu-allowance", "domain": "财商教育", "need": "孩子会管钱",
     "conflict": "零花钱 vs 惯坏/理财教育",
     "linked": ["edu-punish", "soc-consumer"],
     "thesis": ["该不该给孩子零花钱？",
                "孩子乱花钱怎么办？"],
     "antithesis": ["零花钱是惯孩子吗？",
                    "不给孩子钱，孩子偷拿怎么办？"],
     "synthesis": ["零花钱怎么给才合理？",
                   "怎么教孩子管钱？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v15.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v15", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v15: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
