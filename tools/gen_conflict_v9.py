# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v9：新矛盾域（消费金融/食品安全/交通出行/公共文化/体育竞技/资源环境）

v1-v8 已覆盖 37 域 80 矛盾 481 题。v9 新域：
  1. 消费金融：网贷/信用卡/消费贷
  2. 食品安全：添加剂/外卖安全/地沟油
  3. 交通出行：电动车/停车难/交通拥堵
  4. 公共文化：老字号/非遗/文化保护
  5. 体育竞技：运动员/饭圈化/兴奋剂
  6. 资源环境：水资源/塑料/垃圾
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "fin-loan", "domain": "消费金融", "need": "超前消费的便利",
     "conflict": "网贷/消费贷的便利 vs 高息/过度借贷",
     "linked": ["digit-live", "soc-consumer"],
     "thesis": ["为什么网贷这么容易借到？",
                "信用卡透支是不是坑？"],
     "antithesis": ["缺钱的时候不借怎么办？",
                    "借钱消费有错吗？"],
     "synthesis": ["怎么避免陷入网贷陷阱？",
                   "超前消费和理性消费怎么平衡？"]},
    {"id": "food-safe", "domain": "食品安全", "need": "吃得放心",
     "conflict": "食品工业的添加剂/预制菜 vs 健康担忧",
     "linked": ["health-takeout", "gov-reg"],
     "thesis": ["食品添加剂到底安不安全？",
                "预制菜是不是科技与狠活？"],
     "antithesis": ["没有添加剂，食品怎么保存？",
                    "谈添加剂色变是不是过度恐慌？"],
     "synthesis": ["怎么吃得放心又现实？",
                   "食品安全怎么保障？"]},
    {"id": "traffic-e", "domain": "交通出行", "need": "出行便利",
     "conflict": "电动车/电瓶车的便利 vs 安全/充电/管理",
     "linked": ["city-share", "gov-reg"],
     "thesis": ["为什么电动车起火事故这么多？",
                "电动车进楼充电该不该禁？"],
     "antithesis": ["没电动车怎么接送孩子上班？",
                    "管的太多是不是不让人活了？"],
     "synthesis": ["电动车怎么用才安全？",
                   "城市出行怎么更合理？"]},
    {"id": "traffic-jam", "domain": "交通出行", "need": "通勤效率",
     "conflict": "私家车便利 vs 拥堵/停车难",
     "linked": ["soc-urban", "gov-reg"],
     "thesis": ["为什么城市越来越堵？",
                "停车位为什么永远不够？"],
     "antithesis": ["不买车，公共交通够用吗？",
                    "限号限行是不是治标不治本？"],
     "synthesis": ["怎么缓解城市拥堵？",
                   "买车还是用公共交通？"]},
    {"id": "culture-heritage", "domain": "公共文化", "need": "传统文化传承",
     "conflict": "老字号/非遗的传承 vs 市场生存（年轻不吃）",
     "linked": ["relig-trad", "soc-consumer"],
     "thesis": ["为什么老字号越来越少？",
                "非遗手艺没人学怎么办？"],
     "antithesis": ["老东西过时了，淘汰不是自然吗？",
                    "非遗靠补贴养着有意义吗？"],
     "synthesis": ["老字号怎么焕发新生？",
                   "非遗传承和创新怎么结合？"]},
    {"id": "sport-fan", "domain": "体育竞技", "need": "运动员的纯粹竞技",
     "conflict": "竞技体育的饭圈化（追星式）vs 运动本身",
     "linked": ["youth-idol", "pub-violence"],
     "thesis": ["为什么体育圈也饭圈化了？",
                "运动员该不该接代言？"],
     "antithesis": ["运动员也是偶像，粉丝支持有错吗？",
                    "成绩不好被骂，是不是应该？"],
     "synthesis": ["怎么让体育回归竞技？",
                   "运动员怎么面对舆论？"]},
    {"id": "water-res", "domain": "资源环境", "need": "用水自由",
     "conflict": "水资源短缺 vs 浪费/污染",
     "linked": ["gov-carbon", "disaster-dev"],
     "thesis": ["为什么水资源越来越紧张？",
                "水费涨价合理吗？"],
     "antithesis": ["水到处都有，怎么会缺？",
                    "我多用点水有什么关系？"],
     "synthesis": ["怎么节约用水？",
                   "水资源怎么分配才公平？"]},
    {"id": "plastic-waste", "domain": "资源环境", "need": "一次性便利",
     "conflict": "塑料制品便利 vs 白色污染",
     "linked": ["gov-carbon", "health-takeout"],
     "thesis": ["为什么限塑令效果不好？",
                "外卖塑料垃圾怎么这么多？"],
     "antithesis": ["不用塑料，外卖怎么送？",
                    "塑料袋收费是不是变相赚钱？"],
     "synthesis": ["怎么减少塑料污染？",
                   "限塑和个人习惯怎么配合？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v9.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v9", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v9: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
