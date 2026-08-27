# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v22：社会变化激化的新矛盾（男女对立/丈夫夹心/女性消费与工作耐心/收入角色/婚后AA制/全职妈妈回归/大龄未婚标签/婆媳同住）

v1-v21 已覆盖 139 域 181 矛盾 1105 题。v22 聚焦用户点名的社会变化激化新矛盾：
  1. 男女对立：性别战争 vs 理性对话（网络放大）
  2. 丈夫夹心：婆媳矛盾中丈夫的角色（婆媳矛盾深化）
  3. 女性消费与工作耐心：消费欲望 vs 工作耐心（用户点名）
  4. 收入角色：男性养家 vs 女性独立（经济结构变化）
  5. 婚后AA制：独立 vs 生分（个体意识觉醒）
  6. 全职妈妈回归：全职带娃 vs 重返职场
  7. 大龄未婚标签：剩女剩男 vs 个人选择
  8. 婆媳同住：同住 vs 边界（婆媳矛盾深化）
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "gen-war", "domain": "性别议题", "need": "性别和解",
     "conflict": "男女对立 vs 理性对话",
     "linked": ["gen-work", "digit-bully"],
     "thesis": ["为什么现在男女对立这么严重？",
                "网上为什么天天吵性别？"],
     "antithesis": ["女性争取权利，有错吗？",
                    "男性被骂，冤吗？"],
     "synthesis": ["男女怎么放下对立？",
                   "性别话题怎么理性讨论？"]},
    {"id": "fam-mil2", "domain": "家庭关系", "need": "丈夫不夹心",
     "conflict": "婆媳矛盾中丈夫的角色",
     "linked": ["fam-motherinlaw", "fam-couple"],
     "thesis": ["为什么丈夫总在婆媳中间为难？",
                "婆媳吵架，丈夫该帮谁？"],
     "antithesis": ["丈夫向着妈，有错吗？",
                    "丈夫向着老婆，是不孝吗？"],
     "synthesis": ["丈夫怎么处理婆媳矛盾？",
                   "婆媳矛盾中丈夫该怎么做？"]},
    {"id": "gen-consume", "domain": "消费职场", "need": "消费与工作平衡",
     "conflict": "消费欲望高 vs 工作耐心低",
     "linked": ["soc-consumer", "work-loyalty"],
     "thesis": ["为什么女性消费欲望这么高？",
                "工作没耐心，是女性问题吗？"],
     "antithesis": ["赚钱不就是为了花？",
                    "消费和耐心有关系吗？"],
     "synthesis": ["消费和工作怎么平衡？",
                   "怎么看待消费高耐心低的现象？"]},
    {"id": "gen-income", "domain": "家庭经济", "need": "收入分工合理",
     "conflict": "男性养家 vs 女性独立",
     "linked": ["gen-house", "fam-couple"],
     "thesis": ["为什么现在女性也要养家？",
                "谁赚钱养家重要吗？"],
     "antithesis": ["男性养家，天经地义？",
                    "女性不赚钱，行吗？"],
     "synthesis": ["家庭收入怎么分工？",
                   "赚钱和顾家怎么平衡？"]},
    {"id": "fam-aa", "domain": "婚姻财务", "need": "钱不伤感情",
     "conflict": "婚后AA vs 生分",
     "linked": ["fam-couple", "fin-wealth"],
     "thesis": ["为什么越来越多人婚后AA？",
                "婚后AA是独立还是生分？"],
     "antithesis": ["AA伤感情吗？",
                    "钱分开，心也分开了？"],
     "synthesis": ["婚后钱怎么管？",
                   "AA和共同账户怎么选？"]},
    {"id": "gen-stayhome", "domain": "女性职场", "need": "回归有路",
     "conflict": "全职带娃 vs 重返职场",
     "linked": ["gen-house", "work-age35"],
     "thesis": ["为什么全职妈妈重返职场这么难？",
                "全职带娃几年，还能回去吗？"],
     "antithesis": ["全职妈妈是选择，有错吗？",
                    "不工作不独立，怪谁？"],
     "synthesis": ["全职妈妈怎么回归职场？",
                   "家庭和事业怎么平衡？"]},
    {"id": "gen-labels", "domain": "婚恋观念", "need": "不被定义",
     "conflict": "大龄未婚标签 vs 个人选择",
     "linked": ["fam-gener", "psy-lonely"],
     "thesis": ["为什么大龄未婚要被贴标签？",
                "剩女剩男是侮辱吗？"],
     "antithesis": ["晚婚是自己的选择，有错吗？",
                    "不结婚，老了怎么办？"],
     "synthesis": ["怎么面对大龄未婚标签？",
                   "婚姻和独立怎么平衡？"]},
    {"id": "fam-mil3", "domain": "家庭居住", "need": "同住有边界",
     "conflict": "婆媳同住 vs 边界",
     "linked": ["fam-motherinlaw", "fam-eldercare"],
     "thesis": ["为什么婆媳同住矛盾多？",
                "要不要和婆婆一起住？"],
     "antithesis": ["老人想和儿子住，有错吗？",
                    "分开住是不孝吗？"],
     "synthesis": ["婆媳同住怎么处？",
                   "同住和分开怎么选？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v22.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v22", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v22: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
