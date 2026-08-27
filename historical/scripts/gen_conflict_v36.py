# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v36：社会变化激化新矛盾（工作日家庭时间/孩子奖励教育/搬家决策/适老化改造/夫妻价值观冲突/青春期沟通/老人衰老/孩子独立放手）

v1-v35 已覆盖 251 域 293 矛盾 1777 题。v36 聚焦家庭生命周期与代际互动的激化矛盾：
  1. 工作日家庭时间：上班忙 vs 陪家人
  2. 孩子奖励教育：奖励 vs 内在动力
  3. 搬家决策：折腾 vs 新开始
  4. 适老化改造：改造 vs 成本
  5. 夫妻价值观冲突：差异 vs 磨合
  6. 青春期沟通：叛逆 vs 理解
  7. 老人衰老：衰老 vs 接受
  8. 孩子独立放手：独立 vs 守护
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "fam-workday", "domain": "家庭时间", "need": "忙也陪伴",
     "conflict": "工作日家庭时间 vs 工作",
     "linked": ["work-burnout", "fam-weekend"],
     "thesis": ["工作日怎么陪家人？",
                "上班忙，家庭时间少怎么办？"],
     "antithesis": ["赚钱养家就是负责？",
                    "下班就该陪家人？"],
     "synthesis": ["工作日家庭时间怎么安排？",
                   "工作家庭怎么兼顾？"]},
    {"id": "fam-childreward", "domain": "奖励教育", "need": "奖励不绑架",
     "conflict": "孩子奖励 vs 内在动力",
     "linked": ["edu-allowance", "edu-punish"],
     "thesis": ["孩子做得好该奖励吗？",
                "物质奖励有用吗？"],
     "antithesis": ["奖励是贿赂？",
                    "奖励会让孩子为了奖励做事？"],
     "synthesis": ["孩子奖励怎么给？",
                   "奖励和内在动力怎么平衡？"]},
    {"id": "fam-move", "domain": "搬家决策", "need": "搬家不折腾",
     "conflict": "搬家 vs 折腾/新开始",
     "linked": ["housing", "fam-decision"],
     "thesis": ["要不要搬家？",
                "搬家是为了什么？"],
     "antithesis": ["搬家太折腾？",
                    "搬家是新的开始？"],
     "synthesis": ["搬家怎么决定？",
                   "搬家怎么减少折腾？"]},
    {"id": "fam-elderlyhome", "domain": "适老改造", "need": "老人住得安全",
     "conflict": "适老化改造 vs 成本",
     "linked": ["health-fall", "housing-renovation"],
     "thesis": ["家里要适老化改造吗？",
                "适老改造有必要吗？"],
     "antithesis": ["改造花钱值得吗？",
                    "老人说不用改？"],
     "synthesis": ["适老化改造怎么做？",
                   "老人居住安全怎么保障？"]},
    {"id": "fam-values", "domain": "夫妻价值观", "need": "差异能磨合",
     "conflict": "夫妻价值观冲突 vs 磨合",
     "linked": ["fam-couple", "fam-diet"],
     "thesis": ["夫妻价值观不同怎么办？",
                "钱/教育/消费观不合？"],
     "antithesis": ["价值观不合是离婚原因？",
                    "磨合能改价值观吗？"],
     "synthesis": ["夫妻价值观怎么磨合？",
                   "差异和尊重怎么平衡？"]},
    {"id": "fam-teenager", "domain": "青春期", "need": "叛逆被理解",
     "conflict": "青春期沟通 vs 叛逆",
     "linked": ["edu-punish", "fam-childprivacy"],
     "thesis": ["青春期孩子为什么难沟通？",
                "孩子叛逆怎么办？"],
     "antithesis": ["叛逆是正常？",
                    "叛逆是问题？"],
     "synthesis": ["青春期怎么沟通？",
                   "叛逆期怎么陪伴？"]},
    {"id": "fam-aging", "domain": "面对衰老", "need": "衰老不悲哀",
     "conflict": "老人衰老 vs 接受",
     "linked": ["fam-elderlyhealth", "fam-eldercare3"],
     "thesis": ["怎么面对父母变老？",
                "老人衰老是自然还是悲哀？"],
     "antithesis": ["衰老是自然规律？",
                    "变老就失去价值吗？"],
     "synthesis": ["怎么陪父母面对衰老？",
                   "老人怎么接受变老？"]},
    {"id": "fam-childindependence", "domain": "孩子独立", "need": "独立不失控",
     "conflict": "孩子独立 vs 放手",
     "linked": ["fam-teenager", "fam-empty"],
     "thesis": ["孩子多大该独立？",
                "父母什么时候该放手？"],
     "antithesis": ["放手是放任？",
                    "管着是爱？"],
     "synthesis": ["孩子独立怎么培养？",
                   "放手和守护怎么平衡？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v36.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v36", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v36: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
