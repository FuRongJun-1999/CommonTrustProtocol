# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v26：社会变化激化新矛盾（婚姻冷暴力/未婚女性养老/儿童性别教育/婚姻经济控制/女性创业/离婚财产分割/婚后异性友谊/离婚孩子抚养）

v1-v25 已覆盖 171 域 213 矛盾 1297 题。v26 聚焦婚姻与性别议题的深层激化新矛盾：
  1. 婚姻冷暴力：冷暴力 vs 伤害
  2. 未婚女性养老：未婚 vs 养老规划
  3. 儿童性别教育：性别刻板印象 vs 多元教育
  4. 婚姻经济控制：经济控制 vs 家庭暴力
  5. 女性创业：女性创业 vs 偏见
  6. 离婚财产分割：离婚分割 vs 公平
  7. 婚后异性友谊：异性朋友 vs 边界
  8. 离婚孩子抚养：抚养权 vs 争夺
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "fam-coldviolence", "domain": "婚姻暴力", "need": "不被冷落",
     "conflict": "婚姻冷暴力 vs 伤害",
     "linked": ["fam-sunkcost", "fam-couple"],
     "thesis": ["什么是婚姻冷暴力？",
                "冷暴力算家暴吗？"],
     "antithesis": ["冷战是正常磨合？",
                    "不说话比吵架更伤人？"],
     "synthesis": ["冷暴力怎么破？",
                   "婚姻冷暴力怎么应对？"]},
    {"id": "gen-unmarriedpension", "domain": "未婚养老", "need": "单身有保障",
     "conflict": "未婚女性 vs 养老规划",
     "linked": ["gen-labels", "fam-eldercare"],
     "thesis": ["为什么未婚女性也要规划养老？",
                "不结婚，老了谁照顾？"],
     "antithesis": ["没孩子养老是问题吗？",
                    "未婚养老靠自己，行吗？"],
     "synthesis": ["未婚女性怎么规划养老？",
                   "单身养老怎么保障？"]},
    {"id": "edu-gender", "domain": "性别教育", "need": "孩子不被规训",
     "conflict": "性别刻板印象 vs 多元教育",
     "linked": ["gen-war", "edu-punish"],
     "thesis": ["孩子该接受性别平等教育吗？",
                "男孩女孩要区别养吗？"],
     "antithesis": ["性别教育是洗脑吗？",
                    "男孩就要像男孩，对吗？"],
     "synthesis": ["儿童性别教育怎么做？",
                   "怎么养出性别平等的孩子？"]},
    {"id": "fam-fincontrol", "domain": "婚姻经济", "need": "经济不控制",
     "conflict": "婚姻经济控制 vs 家庭暴力",
     "linked": ["fam-aa", "fam-sunkcost"],
     "thesis": ["什么是婚姻经济控制？",
                "管钱算控制吗？"],
     "antithesis": ["经济控制是家暴吗？",
                    "钱都交给我，不好吗？"],
     "synthesis": ["婚姻经济怎么平等？",
                   "经济控制怎么识别和应对？"]},
    {"id": "gen-entrepreneur", "domain": "女性创业", "need": "创业无性别",
     "conflict": "女性创业 vs 偏见",
     "linked": ["gen-work", "work-free"],
     "thesis": ["为什么女性创业更难？",
                "女性创业是异类吗？"],
     "antithesis": ["女性创业有优势吗？",
                    "创业不分性别，对吗？"],
     "synthesis": ["女性创业怎么起步？",
                   "创业性别偏见怎么破？"]},
    {"id": "fam-division", "domain": "婚姻财产", "need": "离婚分得公平",
     "conflict": "离婚财产分割 vs 公平",
     "linked": ["fam-prenup", "fam-sunkcost"],
     "thesis": ["离婚财产怎么分？",
                "全职妈妈离婚分不到财产吗？"],
     "antithesis": ["离婚分割公平吗？",
                    "财产分割是斤斤计较吗？"],
     "synthesis": ["离婚财产怎么分公平？",
                   "婚姻财产怎么保护？"]},
    {"id": "fam-friendboundary", "domain": "婚姻边界", "need": "友谊与边界",
     "conflict": "婚后异性友谊 vs 边界",
     "linked": ["fam-couple", "social-boundary"],
     "thesis": ["婚后可以有异性朋友吗？",
                "配偶和异性朋友走太近，怎么办？"],
     "antithesis": ["异性朋友是正常社交？",
                    "管异性朋友是控制吗？"],
     "synthesis": ["婚后异性友谊怎么处？",
                   "边界和信任怎么平衡？"]},
    {"id": "gen-divorce", "domain": "离婚抚养", "need": "孩子少受伤",
     "conflict": "离婚孩子抚养 vs 争夺",
     "linked": ["fam-sunkcost", "fam-remarry"],
     "thesis": ["离婚后孩子跟谁？",
                "争夺抚养权是爱还是伤害？"],
     "antithesis": ["孩子跟妈妈好还是爸爸好？",
                    "离婚就失去孩子，对吗？"],
     "synthesis": ["离婚抚养怎么对孩子好？",
                   "抚养权怎么定？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v26.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v26", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v26: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
