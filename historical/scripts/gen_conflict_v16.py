# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v16：新矛盾域（大学生兼职/中老年婚恋/宠物殡葬/图书阅读/快递驿站/老年代步车/儿童兴趣班/酒店卫生）

v1-v15 已覆盖 91 域 133 矛盾 817 题。v16 新域（生活矛盾再细化）：
  1. 大学生兼职：兼职赚钱 vs 学业
  2. 中老年婚恋：父母再婚 vs 子女态度/财产
  3. 宠物殡葬：宠物离世 vs 处理方式
  4. 图书阅读：读书 vs 手机
  5. 快递驿站：驿站取件 vs 送货上门
  6. 老年代步车：代步车 vs 安全/管理
  7. 儿童兴趣班：兴趣班 vs 孩子意愿
  8. 酒店卫生：酒店卫生 vs 成本
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "edu-parttime", "domain": "大学阶段", "need": "学业与自立",
     "conflict": "兼职赚钱 vs 学业时间",
     "linked": ["edu-job", "fin-loan"],
     "thesis": ["为什么大学生都在兼职？",
                "兼职会影响学习吗？"],
     "antithesis": ["自己赚钱有错吗？",
                    "大学不兼职，毕业没经验怎么办？"],
     "synthesis": ["兼职和学习怎么平衡？",
                   "大学生该找什么兼职？"]},
    {"id": "fam-elderlove", "domain": "家庭情感", "need": "老人的幸福",
     "conflict": "父母再婚 vs 子女态度/财产",
     "linked": ["fam-remarry", "fam-gener"],
     "thesis": ["为什么老人也想找老伴？",
                "父母再婚，子女为什么反对？"],
     "antithesis": ["老人有追求幸福的权利，有错吗？",
                    "老人再婚就是图财产吗？"],
     "synthesis": ["怎么看待父母再婚？",
                   "老人再婚怎么处理好财产？"]},
    {"id": "pet-funeral", "domain": "养宠生命", "need": "体面的告别",
     "conflict": "宠物离世 vs 处理方式",
     "linked": ["pet-medical", "fam-solitude"],
     "thesis": ["宠物离世怎么处理？",
                "宠物殡葬是智商税吗？"],
     "antithesis": ["宠物只是动物，随便处理不行吗？",
                    "给宠物办葬礼，矫情吗？"],
     "synthesis": ["宠物离世怎么告别？",
                   "怎么面对宠物的离开？"]},
    {"id": "soc-reading", "domain": "精神生活", "need": "阅读的习惯",
     "conflict": "读书 vs 手机碎片化",
     "linked": ["digit-scroll", "edu-score"],
     "thesis": ["为什么越来越多人不读书了？",
                "读书有什么用？"],
     "antithesis": ["手机也能学知识，有错吗？",
                    "读不读书是自己事，管得着吗？"],
     "synthesis": ["怎么重新开始读书？",
                   "读书和刷手机怎么平衡？"]},
    {"id": "logistics-station", "domain": "物流服务", "need": "取件方便",
     "conflict": "驿站取件 vs 送货上门",
     "linked": ["gov-platform", "soc-urban"],
     "thesis": ["为什么快递都不送上门了？",
                "驿站取件方便吗？"],
     "antithesis": ["驿站省了快递员时间，不好吗？",
                    "不送到家，凭什么？"],
     "synthesis": ["快递上门和驿站怎么平衡？",
                   "快递服务怎么选？"]},
    {"id": "traffic-eldercar", "domain": "老年出行", "need": "老人出行自由",
     "conflict": "老年代步车 vs 安全/管理",
     "linked": ["traffic-e", "age-digital"],
     "thesis": ["为什么老年代步车这么多？",
                "老年代步车安全吗？"],
     "antithesis": ["老人腿脚不便，开车有错吗？",
                    "管老年代步车，是欺负老人吗？"],
     "synthesis": ["老年代步车怎么管？",
                   "老人出行怎么解决？"]},
    {"id": "edu-hobby", "domain": "儿童教育", "need": "兴趣还是任务",
     "conflict": "兴趣班 vs 孩子意愿/玩",
     "linked": ["edu-chicken", "edu-allowance"],
     "thesis": ["为什么孩子都在上兴趣班？",
                "兴趣班是真兴趣吗？"],
     "antithesis": ["多学点才艺有错吗？",
                    "不报兴趣班，孩子就输了吗？"],
     "synthesis": ["兴趣班怎么选？",
                   "兴趣班和玩怎么平衡？"]},
    {"id": "tourism-hotel", "domain": "住宿消费", "need": "住得放心",
     "conflict": "酒店卫生 vs 成本",
     "linked": ["tourism-trap", "medical-cost"],
     "thesis": ["酒店卫生真的干净吗？",
                "酒店床单为什么总出事？"],
     "antithesis": ["酒店要赚钱，成本能省就省？",
                    "酒店卫生是酒店的事，消费者管不了？"],
     "synthesis": ["住酒店怎么保障卫生？",
                   "酒店卫生怎么管？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v16.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v16", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v16: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
