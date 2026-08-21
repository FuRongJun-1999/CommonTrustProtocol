# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v29：社会变化激化新矛盾（遗产继承/恋爱控制/二胎压力/婚姻谎言/丧偶女性/月子中心/离婚冷静期/婚礼直播）

v1-v28 已覆盖 195 域 237 矛盾 1441 题。v29 聚焦婚姻家庭的生命周期激化新矛盾：
  1. 遗产继承：遗产分配 vs 继承
  2. 恋爱控制：恋爱控制 vs 自由
  3. 二胎压力：二胎 vs 精力
  4. 婚姻谎言：善意谎言 vs 坦诚
  5. 丧偶女性：丧偶 vs 再婚/独立
  6. 月子中心：月子中心 vs 值不值
  7. 离婚冷静期：冷静期 vs 自由
  8. 婚礼直播：婚礼直播 vs 隐私
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "fam-inheritance", "domain": "遗产继承", "need": "遗产不伤情",
     "conflict": "遗产分配 vs 继承",
     "linked": ["fam-property", "fam-division"],
     "thesis": ["遗产该怎么分？",
                "没遗嘱，遗产怎么继承？"],
     "antithesis": ["多尽孝就多分？",
                    "遗产分配是伤感情的事？"],
     "synthesis": ["遗产怎么安排不伤感情？",
                   "遗嘱该立吗？"]},
    {"id": "fam-datecontrol", "domain": "恋爱边界", "need": "恋爱不控制",
     "conflict": "恋爱控制 vs 自由",
     "linked": ["fam-maritalpua", "fam-dateexpense"],
     "thesis": ["恋爱中控制是爱吗？",
                "对方管太严，怎么办？"],
     "antithesis": ["管你是关心你？",
                    "恋爱中的自由重要吗？"],
     "synthesis": ["恋爱控制怎么识别？",
                   "恋爱中的边界怎么定？"]},
    {"id": "fam-secondchild", "domain": "二胎决策", "need": "二胎不焦虑",
     "conflict": "二胎 vs 精力",
     "linked": ["fam-birth", "fam-parenting"],
     "thesis": ["为什么生二胎犹豫？",
                "二胎是给老大做伴吗？"],
     "antithesis": ["一个孩子太孤单？",
                    "二胎养得起吗？"],
     "synthesis": ["二胎怎么决定？",
                   "二胎的精力怎么分配？"]},
    {"id": "fam-lies", "domain": "婚姻坦诚", "need": "坦诚不伤人",
     "conflict": "善意谎言 vs 坦诚",
     "linked": ["fam-phone", "fam-couple"],
     "thesis": ["婚姻中能说善意的谎言吗？",
                "隐瞒和欺骗有区别吗？"],
     "antithesis": ["诚实是婚姻的底线？",
                    "善意的谎言是保护？"],
     "synthesis": ["婚姻中怎么坦诚？",
                   "谎言和隐私怎么区分？"]},
    {"id": "gen-widow", "domain": "丧偶女性", "need": "丧偶后站起来",
     "conflict": "丧偶 vs 再婚/独立",
     "linked": ["fam-elderlove", "fam-singlemom"],
     "thesis": ["丧偶女性为什么难？",
                "丧偶后该再婚吗？"],
     "antithesis": ["丧偶是人生的坎？",
                    "再婚是对亡者的背叛吗？"],
     "synthesis": ["丧偶女性怎么走出来？",
                   "丧偶后的生活怎么安排？"]},
    {"id": "fam-yuegong", "domain": "月子中心", "need": "月子选得对",
     "conflict": "月子中心 vs 值不值",
     "linked": ["fam-yuesao", "fam-birth"],
     "thesis": ["月子中心值吗？",
                "月子中心是智商税吗？"],
     "antithesis": ["月子中心专业？",
                    "在家坐月子不好吗？"],
     "synthesis": ["月子中心怎么选？",
                   "坐月子怎么选择？"]},
    {"id": "gen-divorce2", "domain": "离婚制度", "need": "离婚不冲动",
     "conflict": "离婚冷静期 vs 自由",
     "linked": ["fam-sunkcost", "fam-division"],
     "thesis": ["离婚冷静期合理吗？",
                "冷静期是保护还是限制？"],
     "antithesis": ["想离婚还要等？",
                    "冷静期能挽救婚姻吗？"],
     "synthesis": ["离婚冷静期怎么看？",
                   "冲动离婚怎么避免？"]},
    {"id": "digit-wedding", "domain": "婚礼传播", "need": "婚礼有边界",
     "conflict": "婚礼直播 vs 隐私",
     "linked": ["digit-baby", "fam-wedding"],
     "thesis": ["为什么婚礼也直播？",
                "婚礼直播是记录还是作秀？"],
     "antithesis": ["直播婚礼，有错吗？",
                    "婚礼是两个人的事？"],
     "synthesis": ["婚礼直播怎么把握？",
                   "婚礼的隐私怎么保护？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v29.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v29", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v29: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
