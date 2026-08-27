# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v24：社会变化激化新矛盾（求职婚育歧视/男性情感表达/单身经济/女性生育焦虑/男性形象消费/单亲妈妈/女性夜间安全/婚恋性别比）

v1-v23 已覆盖 155 域 197 矛盾 1201 题。v24 聚焦性别与婚恋的社会激化新矛盾：
  1. 求职婚育歧视：面试问婚育计划 vs 就业公平
  2. 男性情感表达：男儿有泪不轻弹 vs 情绪健康
  3. 单身经济：一人食/小户型 vs 社会配套
  4. 女性生育焦虑：生育年龄焦虑 vs 选择
  5. 男性形象消费：男性护肤医美 vs 观念
  6. 单亲妈妈：单亲养育 vs 支持
  7. 女性夜间安全：夜归安全 vs 女性自由
  8. 婚恋性别比：男多女少 vs 婚恋压力
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "gen-hiring", "domain": "就业公平", "need": "求职不被问私事",
     "conflict": "面试问婚育 vs 就业公平",
     "linked": ["gen-work", "gen-stayhome"],
     "thesis": ["为什么面试总问婚育计划？",
                "女性求职被问生孩子，公平吗？"],
     "antithesis": ["企业怕成本，有错吗？",
                    "婚育是私事，凭啥问？"],
     "synthesis": ["求职婚育问题怎么答？",
                   "职场生育歧视怎么破？"]},
    {"id": "gen-maleemotion", "domain": "男性心理", "need": "情绪被允许",
     "conflict": "男儿有泪不轻弹 vs 情绪健康",
     "linked": ["gen-malepressure", "psy-anxiety"],
     "thesis": ["为什么男人不能哭？",
                "男儿有泪不轻弹，对吗？"],
     "antithesis": ["男人示弱，丢人吗？",
                    "情绪外露是软弱吗？"],
     "synthesis": ["男性情绪怎么表达？",
                   "男人的压力怎么释放？"]},
    {"id": "soc-singleeconomy", "domain": "单身社会", "need": "单身也体面",
     "conflict": "单身经济 vs 社会配套",
     "linked": ["psy-single", "fam-birth"],
     "thesis": ["为什么单身经济这么火？",
                "一人食是孤独还是自由？"],
     "antithesis": ["一个人生活，有错吗？",
                    "单身经济是逃避婚姻吗？"],
     "synthesis": ["单身生活怎么过好？",
                   "单身和社会怎么和解？"]},
    {"id": "gen-birthanxiety", "domain": "女性抉择", "need": "生育不焦虑",
     "conflict": "生育年龄焦虑 vs 选择",
     "linked": ["fam-birth", "gen-labels"],
     "thesis": ["为什么女性有生育年龄焦虑？",
                "30岁没生孩子，慌吗？"],
     "antithesis": ["年龄是生育的坎吗？",
                    "为了生育将就结婚，对吗？"],
     "synthesis": ["生育焦虑怎么面对？",
                   "生育和事业怎么权衡？"]},
    {"id": "gen-malegrooming", "domain": "男性消费", "need": "形象自由",
     "conflict": "男性护肤医美 vs 观念",
     "linked": ["gen-consume", "psy-appearance"],
     "thesis": ["为什么男性也开始护肤医美？",
                "男性爱美，娘吗？"],
     "antithesis": ["男性注重形象，有错吗？",
                    "男性消费崛起是好事吗？"],
     "synthesis": ["男性形象消费怎么看？",
                   "形象和实力怎么平衡？"]},
    {"id": "fam-singlemom", "domain": "单亲家庭", "need": "单亲不被看低",
     "conflict": "单亲养育 vs 支持",
     "linked": ["fam-remarry", "gen-stayhome"],
     "thesis": ["为什么单亲妈妈这么难？",
                "单亲妈妈养娃，能行吗？"],
     "antithesis": ["单亲是自己选的，怪谁？",
                    "单亲妈妈需要特殊照顾吗？"],
     "synthesis": ["单亲妈妈怎么撑起家？",
                   "社会怎么支持单亲家庭？"]},
    {"id": "public-night", "domain": "公共安全", "need": "夜晚也自由",
     "conflict": "女性夜间安全 vs 自由",
     "linked": ["traffic-ridehailing", "gen-war"],
     "thesis": ["为什么女性夜间出行不安全？",
                "晚上不敢出门，是女性问题吗？"],
     "antithesis": ["深夜出门，自己不小心？",
                    "女性夜间自由，是奢望吗？"],
     "synthesis": ["女性夜间安全怎么保障？",
                   "城市怎么让夜晚更安全？"]},
    {"id": "gen-genderratio", "domain": "人口结构", "need": "婚恋不恐慌",
     "conflict": "男多女少 vs 婚恋压力",
     "linked": ["gen-malepressure", "fam-betrothal"],
     "thesis": ["为什么男多女少？",
                "男女比例失衡，婚恋怎么办？"],
     "antithesis": ["男多女少是女性的红利？",
                    "光棍多是社会问题吗？"],
     "synthesis": ["性别比失衡怎么应对？",
                   "婚恋市场怎么理性？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v24.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v24", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v24: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
