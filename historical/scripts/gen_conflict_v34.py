# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v34：社会变化激化新矛盾（家庭饮食之争/家庭作息之争/家庭旅行安排/家庭聚会/孩子交友/孩子家务/家务标准/宠物与孩子）

v1-v33 已覆盖 235 域 277 矛盾 1681 题。v34 聚焦家庭日常运转的激化矛盾：
  1. 家庭饮食之争：健康 vs 口味
  2. 家庭作息之争：早睡 vs 晚睡
  3. 家庭旅行安排：带娃旅行
  4. 家庭聚会：温馨 vs 负担
  5. 孩子交友：交友自由 vs 把关
  6. 孩子家务：家务 vs 学习
  7. 家务标准：洁癖 vs 随意
  8. 宠物与孩子：养宠与育儿
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "fam-diet", "domain": "家庭饮食", "need": "吃得健康也开心",
     "conflict": "健康饮食 vs 口味",
     "linked": ["fam-health", "food-safe"],
     "thesis": ["家庭饮食听谁的？",
                "健康饮食和口味怎么平衡？"],
     "antithesis": ["爱吃啥吃啥？",
                    "健康饮食是矫情？"],
     "synthesis": ["家庭饮食怎么安排？",
                   "健康和孩子口味怎么兼顾？"]},
    {"id": "fam-schedule", "domain": "家庭作息", "need": "作息不冲突",
     "conflict": "早睡 vs 晚睡",
     "linked": ["fam-separatebeds", "edu-sleep"],
     "thesis": ["家庭作息不统一怎么办？",
                "早睡的和晚睡的怎么处？"],
     "antithesis": ["作息是个人自由？",
                    "家庭作息要统一吗？"],
     "synthesis": ["家庭作息怎么协调？",
                   "作息差异怎么磨合？"]},
    {"id": "fam-trip", "domain": "家庭旅行", "need": "旅行不折腾",
     "conflict": "带娃旅行 vs 享受/折腾",
     "linked": ["edu-trip", "fam-couple"],
     "thesis": ["家庭旅行听谁的？",
                "带娃旅行是享受还是受罪？"],
     "antithesis": ["旅行是为了孩子？",
                    "旅行是放松还是折腾？"],
     "synthesis": ["家庭旅行怎么规划？",
                   "旅行的需求怎么平衡？"]},
    {"id": "fam-gathering", "domain": "家庭聚会", "need": "聚会不负担",
     "conflict": "家庭聚会 vs 温馨/负担",
     "linked": ["fam-groupchat", "fam-inlaws"],
     "thesis": ["家庭聚会是温馨还是负担？",
                "不想参加家庭聚会，行吗？"],
     "antithesis": ["聚会是亲情？",
                    "聚会是应酬？"],
     "synthesis": ["家庭聚会怎么相处？",
                   "聚会和自由怎么平衡？"]},
    {"id": "fam-childfriends", "domain": "孩子交友", "need": "交友有边界",
     "conflict": "孩子交友 vs 把关",
     "linked": ["edu-punish", "fam-childprivacy"],
     "thesis": ["孩子交朋友要管吗？",
                "孩子的朋友不好，怎么办？"],
     "antithesis": ["孩子交友是自由？",
                    "不管孩子交朋友，行吗？"],
     "synthesis": ["孩子交友怎么引导？",
                   "把关和放手怎么平衡？"]},
    {"id": "fam-chorechild", "domain": "孩子家务", "need": "家务是成长",
     "conflict": "孩子家务 vs 学习",
     "linked": ["edu-allowance", "gen-house"],
     "thesis": ["孩子该做家务吗？",
                "家务和学习怎么排？"],
     "antithesis": ["孩子小，做什么家务？",
                    "做家务是锻炼还是剥削？"],
     "synthesis": ["孩子家务怎么安排？",
                   "家务和零花钱怎么挂钩？"]},
    {"id": "fam-cleanliness", "domain": "家务标准", "need": "干净不吵架",
     "conflict": "洁癖 vs 随意",
     "linked": ["gen-house", "fam-fight"],
     "thesis": ["家务标准不同怎么办？",
                "洁癖和随意怎么处？"],
     "antithesis": ["干净是基本要求？",
                    "差不多就行了？"],
     "synthesis": ["家务标准怎么统一？",
                   "干净和轻松怎么平衡？"]},
    {"id": "fam-petchild", "domain": "宠物孩子", "need": "宠物孩子两全",
     "conflict": "宠物与孩子 vs 共存",
     "linked": ["fam-pet", "fam-childfriends"],
     "thesis": ["有孩子能养宠物吗？",
                "宠物和孩子能共存吗？"],
     "antithesis": ["宠物对孩子有好处？",
                    "宠物对孩子有风险？"],
     "synthesis": ["宠物和孩子怎么相处？",
                   "养宠和育儿怎么兼顾？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v34.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v34", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v34: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
