# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v32：社会变化激化新矛盾（家庭决策权/夫妻吵架/成长不同步/婚礼筹备/亲家关系/异地养老/过年回谁家/夫妻说话方式）

v1-v31 已覆盖 219 域 261 矛盾 1585 题。v32 聚焦婚姻家庭的互动细节激化矛盾：
  1. 家庭决策权：谁说了算
  2. 夫妻吵架：吵架 vs 不吵架
  3. 成长不同步：夫妻成长差异
  4. 婚礼筹备：筹备 vs 吵架
  5. 亲家关系：两家父母相处
  6. 异地养老：孝心与距离
  7. 过年回谁家：婆家 vs 娘家
  8. 夫妻说话方式：好好说话
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "fam-decision", "domain": "家庭决策", "need": "决策共担",
     "conflict": "家庭决策权 vs 尊重",
     "linked": ["fam-couple", "gen-income"],
     "thesis": ["家里大事谁说了算？",
                "家庭决策要商量吗？"],
     "antithesis": ["谁赚得多谁做主？",
                    "决策权是地位的象征吗？"],
     "synthesis": ["家庭决策怎么定？",
                   "决策权和尊重怎么平衡？"]},
    {"id": "fam-fight", "domain": "夫妻吵架", "need": "吵架不伤情",
     "conflict": "夫妻吵架 vs 沟通",
     "linked": ["fam-couple", "fam-intimacy"],
     "thesis": ["夫妻吵架正常吗？",
                "吵架会伤感情吗？"],
     "antithesis": ["不吵架是感情好？",
                    "吵架是沟通还是伤害？"],
     "synthesis": ["夫妻怎么吵不伤感情？",
                   "吵架后怎么和好？"]},
    {"id": "fam-growth", "domain": "夫妻成长", "need": "一起成长",
     "conflict": "成长不同步 vs 婚姻",
     "linked": ["fam-couple", "fam-emotionalvalue"],
     "thesis": ["夫妻成长不同步怎么办？",
                "他进步了，我落后了？"],
     "antithesis": ["成长是各走各的？",
                    "不同步是离婚的原因？"],
     "synthesis": ["夫妻怎么一起成长？",
                   "成长差异怎么面对？"]},
    {"id": "fam-weddingprep", "domain": "婚礼筹备", "need": "筹备不吵架",
     "conflict": "婚礼筹备 vs 吵架",
     "linked": ["fam-wedding", "fam-couple"],
     "thesis": ["为什么婚礼筹备总吵架？",
                "办婚礼是幸福的开始还是吵架的开始？"],
     "antithesis": ["婚礼要听父母的？",
                    "婚礼是两个人的还是两家的？"],
     "synthesis": ["婚礼筹备怎么不吵架？",
                   "婚礼的矛盾怎么化解？"]},
    {"id": "fam-inlaws", "domain": "亲家关系", "need": "两家和睦",
     "conflict": "亲家关系 vs 相处",
     "linked": ["fam-mil3", "fam-mil4"],
     "thesis": ["亲家之间怎么相处？",
                "亲家关系影响小两口吗？"],
     "antithesis": ["亲家是亲戚？",
                    "亲家之间要客气吗？"],
     "synthesis": ["亲家关系怎么处好？",
                   "两家父母怎么互动？"]},
    {"id": "fam-eldercare3", "domain": "异地养老", "need": "孝心不缺席",
     "conflict": "异地养老 vs 尽孝",
     "linked": ["fam-onlychild", "fam-longdistance"],
     "thesis": ["父母在老家，怎么尽孝？",
                "异地养老是遗憾吗？"],
     "antithesis": ["接父母过来住？",
                    "常回家看看够吗？"],
     "synthesis": ["异地养老怎么安排？",
                   "孝心和距离怎么平衡？"]},
    {"id": "fam-newyear", "domain": "过年回家", "need": "两家都过",
     "conflict": "过年回谁家 vs 两难",
     "linked": ["fam-couple", "fam-mil4"],
     "thesis": ["过年回谁家总吵架？",
                "回婆家还是回娘家？"],
     "antithesis": ["传统是回婆家？",
                    "轮流回，公平吗？"],
     "synthesis": ["过年回谁家怎么定？",
                   "两家的年怎么安排？"]},
    {"id": "fam-talk", "domain": "夫妻沟通", "need": "好好说话",
     "conflict": "夫妻说话方式 vs 伤害",
     "linked": ["fam-fight", "fam-couple"],
     "thesis": ["为什么夫妻说话容易伤人？",
                "好好说话难吗？"],
     "antithesis": ["一家人说话随便点？",
                    "语言暴力是暴力吗？"],
     "synthesis": ["夫妻怎么好好说话？",
                   "伤人的话怎么不说？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v32.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v32", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v32: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
