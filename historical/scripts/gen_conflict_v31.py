# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v31：社会变化激化新矛盾（异地婚姻/收养/夫妻分房/夫妻创业/婚前买房/婚姻情绪价值/母职绑架/家庭屏幕时间）

v1-v30 已覆盖 211 域 253 矛盾 1537 题。v31 聚焦婚姻家庭的新形态与数字时代激化矛盾：
  1. 异地婚姻：异地夫妻 vs 维系
  2. 收养：收养 vs 亲生
  3. 夫妻分房：分房睡 vs 感情
  4. 夫妻创业：夫妻创业 vs 关系
  5. 婚前买房：婚前买房 vs 婚后
  6. 婚姻情绪价值：情绪价值 vs 物质
  7. 母职绑架：为母则刚 vs 自我
  8. 家庭屏幕时间：刷手机 vs 陪伴
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "fam-longdistance", "domain": "异地婚姻", "need": "异地不散",
     "conflict": "异地婚姻 vs 维系",
     "linked": ["fam-couple", "digit-dating"],
     "thesis": ["异地婚姻能长久吗？",
                "夫妻异地，感情会淡吗？"],
     "antithesis": ["异地是为了生活？",
                    "异地是感情杀手？"],
     "synthesis": ["异地婚姻怎么维系？",
                   "异地夫妻怎么安排？"]},
    {"id": "fam-adoption", "domain": "收养", "need": "收养是家",
     "conflict": "收养 vs 亲生",
     "linked": ["fam-birth", "fam-remarry"],
     "thesis": ["收养孩子要注意什么？",
                "收养和亲生一样吗？"],
     "antithesis": ["收养是善举？",
                    "收养的孩子能当亲生的吗？"],
     "synthesis": ["收养怎么决定？",
                   "收养家庭怎么相处？"]},
    {"id": "fam-separatebeds", "domain": "夫妻睡眠", "need": "分房不伤情",
     "conflict": "夫妻分房 vs 感情",
     "linked": ["fam-intimacy", "fam-couple"],
     "thesis": ["夫妻分房睡正常吗？",
                "分房是感情淡了吗？"],
     "antithesis": ["分房是自由？",
                    "同床才叫夫妻？"],
     "synthesis": ["分房怎么不伤感情？",
                   "分房还是同房怎么选？"]},
    {"id": "fam-couplebusiness", "domain": "夫妻创业", "need": "创业不伤情",
     "conflict": "夫妻创业 vs 关系",
     "linked": ["gen-entrepreneur", "fam-couple"],
     "thesis": ["夫妻一起创业好吗？",
                "创业会伤感情吗？"],
     "antithesis": ["夫妻同心其利断金？",
                    "工作和生活分得开吗？"],
     "synthesis": ["夫妻创业怎么合作？",
                   "创业和婚姻怎么平衡？"]},
    {"id": "fam-premarriagehouse", "domain": "婚前房产", "need": "房产不纠纷",
     "conflict": "婚前买房 vs 婚后",
     "linked": ["fam-prenup", "fam-division"],
     "thesis": ["婚前买房算谁的？",
                "婚前买房婚后还贷怎么算？"],
     "antithesis": ["婚前财产是保障？",
                    "一起买房更公平？"],
     "synthesis": ["婚前买房怎么安排？",
                   "房产和婚姻怎么处理？"]},
    {"id": "fam-emotionalvalue", "domain": "婚姻情绪", "need": "情绪被接住",
     "conflict": "婚姻情绪价值 vs 物质",
     "linked": ["fam-couple", "fam-intimacy"],
     "thesis": ["婚姻中的情绪价值重要吗？",
                "提供不了情绪价值，怎么办？"],
     "antithesis": ["结婚是为了过日子的？",
                    "情绪价值是矫情吗？"],
     "synthesis": ["婚姻的情绪价值怎么给？",
                   "情绪和物质怎么平衡？"]},
    {"id": "gen-motherrole", "domain": "母职压力", "need": "妈妈不完美也没关系",
     "conflict": "为母则刚 vs 自我",
     "linked": ["gen-stayhome", "fam-parenting"],
     "thesis": ["为什么妈妈被要求完美？",
                "为母则刚是赞美还是绑架？"],
     "antithesis": ["当妈就该牺牲？",
                    "妈妈也要有自己？"],
     "synthesis": ["怎么摆脱母职绑架？",
                   "妈妈怎么做自己？"]},
    {"id": "digit-familytime", "domain": "家庭陪伴", "need": "陪伴在场",
     "conflict": "家庭屏幕时间 vs 陪伴",
     "linked": ["fam-groupchat", "digit-scroll"],
     "thesis": ["为什么家庭聚餐都在刷手机？",
                "手机偷走了家庭时光？"],
     "antithesis": ["吃饭玩手机怎么了？",
                    "各自看手机也是陪伴？"],
     "synthesis": ["家庭时间怎么放下手机？",
                   "屏幕和陪伴怎么平衡？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v31.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v31", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v31: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
