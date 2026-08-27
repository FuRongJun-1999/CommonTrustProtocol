# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v11：新矛盾域（职场PUA/减肥焦虑/公共文明/教育惩戒/考研考公/独居老人/农药残留/老旧小区）

v1-v10 已覆盖 51 域 93 矛盾 577 题。v11 新域（生活矛盾再细化）：
  1. 职场PUA：老板画饼/贬低 vs 自我价值
  2. 减肥焦虑：身材标准 vs 健康/自我接纳
  3. 公共文明：公共场所熊孩子/噪音 vs 个人自由
  4. 教育惩戒：打骂/惩罚 vs 讲道理/边界
  5. 考研考公热：稳定追求 vs 竞争/内卷
  6. 独居老人：老人独居 vs 子女陪伴/照护
  7. 农药残留：吃得安全 vs 有机太贵
  8. 老旧小区：加装电梯/改造 vs 费用/利益分歧
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "emp-pua", "domain": "职场成长", "need": "工作价值感",
     "conflict": "老板画饼/贬低 vs 自我价值",
     "linked": ["work-burnout", "social-boundary"],
     "thesis": ["为什么老板总爱画饼？",
                "被领导当众批评，是我太玻璃心吗？"],
     "antithesis": ["领导严格要求有错吗？",
                    "骂你是为你好，这话对吗？"],
     "synthesis": ["怎么应对职场PUA？",
                   "怎么分辨真心栽培和PUA？"]},
    {"id": "health-weight", "domain": "健康生活", "need": "健康身材",
     "conflict": "身材标准 vs 健康/自我接纳",
     "linked": ["psy-appearance", "health-takeout"],
     "thesis": ["为什么越来越多人身材焦虑？",
                "胖一点就是不自律吗？"],
     "antithesis": ["减肥是为了健康，有错吗？",
                    "别人都说我胖，我该减肥吗？"],
     "synthesis": ["怎么健康地管理身材？",
                   "体重和健康怎么平衡？"]},
    {"id": "public-civility", "domain": "公共生活", "need": "公共安宁",
     "conflict": "公共场所熊孩子/噪音 vs 个人自由",
     "linked": ["city-pet", "social-boundary"],
     "thesis": ["为什么高铁上总有熊孩子？",
                "公共场合孩子哭闹，该不该管？"],
     "antithesis": ["孩子还小，忍忍不行吗？",
                    "公共场合太安静，是不是太压抑了？"],
     "synthesis": ["怎么和熊孩子家长沟通？",
                   "公共场所的边界怎么定？"]},
    {"id": "edu-punish", "domain": "教育方法", "need": "孩子守规矩",
     "conflict": "打骂/惩罚 vs 讲道理/边界",
     "linked": ["teach-authority", "youth-game"],
     "thesis": ["孩子不打不成器吗？",
                "为什么讲道理没用？"],
     "antithesis": ["打孩子是家暴还是管教？",
                    "完全不管，孩子不就无法无天了？"],
     "synthesis": ["怎么立规矩不打骂？",
                   "惩罚和伤害的边界在哪？"]},
    {"id": "study-kaoyan", "domain": "教育选择", "need": "出路稳定",
     "conflict": "考研考公热 vs 竞争/内卷",
     "linked": ["edu-job", "soc-lieflat"],
     "thesis": ["为什么越来越多人考研考公？",
                "考不上研就是失败吗？"],
     "antithesis": ["都去考公，谁搞科研做实业？",
                    "稳定有什么不好？"],
     "synthesis": ["考研考公还是就业，怎么选？",
                   "考了几年没上岸，还要继续吗？"]},
    {"id": "fam-solitude", "domain": "家庭养老", "need": "老人有伴",
     "conflict": "老人独居 vs 子女陪伴/照护",
     "linked": ["fam-eldercare", "soc-aging"],
     "thesis": ["为什么老人越来越孤独？",
                "独居老人最怕什么？"],
     "antithesis": ["子女在外打拼，有错吗？",
                    "把老人送养老院，是不孝吗？"],
     "synthesis": ["怎么让独居老人不孤单？",
                   "陪伴和打拼怎么平衡？"]},
    {"id": "food-residue", "domain": "食品安全", "need": "吃得安全",
     "conflict": "农药残留 vs 有机太贵",
     "linked": ["food-safe", "medical-cost"],
     "thesis": ["蔬菜水果都有农药残留吗？",
                "不买有机食品，就不安全吗？"],
     "antithesis": ["种地不打药，产量够吗？",
                    "有机食品贵得有道理吗？"],
     "synthesis": ["怎么吃得安全又实惠？",
                   "普通食品和有机食品怎么选？"]},
    {"id": "city-elevator", "domain": "城市社区", "need": "居住改善",
     "conflict": "老旧小区改造 vs 费用/利益分歧",
     "linked": ["housing", "gov-subsidy"],
     "thesis": ["为什么老小区加装电梯这么难？",
                "一楼住户凭什么反对装电梯？"],
     "antithesis": ["装电梯的钱该谁出？",
                    "老小区拆了重建不更好吗？"],
     "synthesis": ["加装电梯怎么让大家都满意？",
                   "老旧小区怎么改造才公平？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v11.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v11", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v11: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
