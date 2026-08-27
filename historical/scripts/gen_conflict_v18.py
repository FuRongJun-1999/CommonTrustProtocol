# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v18：新矛盾域（儿童用药/医养结合/付费自习室/教师收礼/银行网点消失/大学生生活费/宠物训练/学生睡眠）

v1-v17 已覆盖 107 域 149 矛盾 913 题。v18 新域（生活矛盾再细化）：
  1. 儿童用药：喂药难/抗生素滥用 vs 科学用药
  2. 医养结合：养老院医疗 vs 养老
  3. 付费自习室：付费自习 vs 免费图书馆
  4. 教师收礼：教师收礼 vs 教育公平
  5. 银行网点消失：网点减少 vs 老人办事
  6. 大学生生活费：生活费 vs 家庭负担/攀比
  7. 宠物训练：宠物行为 vs 训练管教
  8. 学生睡眠：作业多 vs 睡眠
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "health-medicine", "domain": "儿童医疗", "need": "孩子健康",
     "conflict": "喂药难/抗生素滥用 vs 科学用药",
     "linked": ["medical-cost", "fam-parenting"],
     "thesis": ["为什么孩子老生病？",
                "抗生素为什么不能乱吃？"],
     "antithesis": ["孩子病了不吃药，扛着行吗？",
                    "喂药难，灌下去不行吗？"],
     "synthesis": ["孩子生病怎么科学用药？",
                   "喂药难怎么破？"]},
    {"id": "med-eldercare", "domain": "养老医疗", "need": "养老有医靠",
     "conflict": "养老院医疗 vs 养老",
     "linked": ["fam-eldercare", "medical-cost"],
     "thesis": ["为什么养老院一床难求？",
                "养老院能看病吗？"],
     "antithesis": ["养老院管养老就行，看病去医院？",
                    "医养结合，钱谁出？"],
     "synthesis": ["老人养老医疗怎么保障？",
                   "医养结合怎么做？"]},
    {"id": "edu-studyroom", "domain": "学习空间", "need": "学得进去",
     "conflict": "付费自习室 vs 免费图书馆/在家",
     "linked": ["city-library", "study-kaoyan"],
     "thesis": ["为什么付费自习室这么火？",
                "在家学不进去，去自习室有用吗？"],
     "antithesis": ["自习还要花钱，值吗？",
                    "免费图书馆不够用吗？"],
     "synthesis": ["自习室和图书馆怎么选？",
                   "怎么高效自习？"]},
    {"id": "teach-gift", "domain": "师生伦理", "need": "教育公平",
     "conflict": "教师收礼 vs 教育公平",
     "linked": ["teach-fair", "gov-reg"],
     "thesis": ["为什么家长要给老师送礼？",
                "老师收礼是常态吗？"],
     "antithesis": ["送礼是感谢老师，有错吗？",
                    "老师辛苦，收点礼怎么了？"],
     "synthesis": ["怎么感谢老师不送礼？",
                   "教师收礼怎么管？"]},
    {"id": "fin-branch", "domain": "金融服务", "need": "老人也能办业务",
     "conflict": "网点减少 vs 老人办事",
     "linked": ["age-digital", "digit-scam"],
     "thesis": ["为什么银行网点越来越少？",
                "银行都在手机上，网点有必要吗？"],
     "antithesis": ["网点少，老人怎么办？",
                    "银行也要赚钱，网点关了就关了？"],
     "synthesis": ["老人办事怎么办？",
                   "银行服务怎么兼顾？"]},
    {"id": "edu-allowance2", "domain": "大学生活", "need": "生活费合理",
     "conflict": "生活费多少 vs 家庭负担/攀比",
     "linked": ["edu-parttime", "soc-consumer"],
     "thesis": ["大学生一个月生活费多少合适？",
                "生活费不够怎么办？"],
     "antithesis": ["多给生活费，是惯孩子吗？",
                    "孩子要多少给多少，行吗？"],
     "synthesis": ["生活费怎么给才合理？",
                   "大学生怎么管自己的生活费？"]},
    {"id": "pet-training", "domain": "养宠教育", "need": "宠物守规矩",
     "conflict": "宠物行为 vs 训练管教",
     "linked": ["city-pet", "edu-punish"],
     "thesis": ["为什么宠物不听话？",
                "宠物训练是打骂吗？"],
     "antithesis": ["宠物就该自由，训练残忍吗？",
                    "不训练，宠物伤人谁负责？"],
     "synthesis": ["宠物怎么训练不伤害？",
                   "宠物行为问题怎么解决？"]},
    {"id": "edu-sleep", "domain": "学生健康", "need": "睡够",
     "conflict": "作业多 vs 睡眠",
     "linked": ["edu-score", "digit-scroll"],
     "thesis": ["为什么学生都缺觉？",
                "作业多到做不完，怎么办？"],
     "antithesis": ["睡得少学得多，有错吗？",
                    "熬夜是努力，不是问题？"],
     "synthesis": ["作业和睡眠怎么平衡？",
                   "怎么让孩子睡够？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v18.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v18", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v18: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
