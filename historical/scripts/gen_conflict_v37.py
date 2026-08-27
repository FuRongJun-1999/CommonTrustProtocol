# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v37：学习动力 vs 娱乐诱惑（用户点名：为什么学习不如玩游戏有趣）

v1-v36 已覆盖 301 矛盾 1825 题。v37 聚焦学习动力与娱乐诱惑的激化矛盾：
  1. 学习游戏趣味：学习的苦（延迟满足）vs 游戏的爽（即时反馈）
  2. 学习枯燥：枯燥 vs 本质
  3. 游戏机制：设计套路 vs 自我沉迷
  4. 学习娱乐平衡：学 vs 玩
  5. 拖延启动：想学 vs 先玩
  6. 学习意义：用不上 vs 必备
  7. 知识乐趣：有趣 vs 枯燥
  8. 游戏责任：游戏害人 vs 自制力
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "edu-gamefun", "domain": "学习游戏趣味", "need": "学习的爽感",
     "conflict": "学习不如游戏 vs 有趣",
     "linked": ["youth-game", "edu-score"],
     "thesis": ["为什么学习不如游戏有趣？",
                "游戏为什么比学习好玩？"],
     "antithesis": ["学习没意思，游戏才有意思？",
                    "游戏好玩是天生的？"],
     "synthesis": ["学习和游戏怎么平衡？",
                   "怎么让学习像游戏一样好玩？"]},
    {"id": "edu-boring", "domain": "学习枯燥", "need": "枯燥可破",
     "conflict": "学习枯燥 vs 有趣",
     "linked": ["edu-homework", "edu-hobby"],
     "thesis": ["学习为什么枯燥？",
                "学习没意思怎么办？"],
     "antithesis": ["学习不该有趣？",
                    "枯燥是学习的本质？"],
     "synthesis": ["学习枯燥怎么破？",
                   "怎么把枯燥学出乐趣？"]},
    {"id": "digit-game", "domain": "游戏机制", "need": "识破套路",
     "conflict": "游戏设计 vs 沉迷",
     "linked": ["digit-drama", "digit-scroll"],
     "thesis": ["游戏为什么让人上瘾？",
                "游戏为什么好玩？"],
     "antithesis": ["游戏好玩是设计套路？",
                    "多巴胺让游戏上瘾？"],
     "synthesis": ["游戏机制怎么防沉迷？",
                   "怎么识别游戏套路？"]},
    {"id": "edu-playbalance", "domain": "学习娱乐平衡", "need": "学玩兼得",
     "conflict": "学习 vs 娱乐",
     "linked": ["edu-gamefun", "edu-sleep"],
     "thesis": ["学习烦了，玩会游戏行吗？",
                "先玩后学可以吗？"],
     "antithesis": ["玩完游戏就学不进去？",
                    "学习娱乐不能兼得？"],
     "synthesis": ["学习和娱乐怎么平衡？",
                   "怎么做到学得进玩得爽？"]},
    {"id": "edu-procrast", "domain": "拖延启动", "need": "先开始",
     "conflict": "想学 vs 先玩",
     "linked": ["self-procrast", "edu-gamefun"],
     "thesis": ["想学但总想先玩游戏怎么办？",
                "为什么一学习就犯困？"],
     "antithesis": ["学不进去是懒？",
                    "等有状态了再学？"],
     "synthesis": ["怎么开始学习的第一步？",
                   "拖延学习怎么治？"]},
    {"id": "edu-why", "domain": "学习意义", "need": "意义落地",
     "conflict": "学习无用 vs 必备",
     "linked": ["edu-score", "edu-job"],
     "thesis": ["学习有什么用？",
                "为什么要学习？"],
     "antithesis": ["学的东西用不上？",
                    "读书无用论对吗？"],
     "synthesis": ["学习的意义是什么？",
                   "学的东西怎么用上？"]},
    {"id": "edu-knowledgefun", "domain": "知识乐趣", "need": "知识有味",
     "conflict": "知识有趣 vs 枯燥",
     "linked": ["edu-boring", "soc-reading"],
     "thesis": ["知识有趣吗？",
                "怎么发现学习的乐趣？"],
     "antithesis": ["乐趣是玩出来的不是学出来的？",
                    "学习只能靠毅力？"],
     "synthesis": ["怎么让知识变得有趣？",
                   "好奇心和兴趣怎么培养？"]},
    {"id": "digit-gameblame", "domain": "游戏责任", "need": "不甩锅",
     "conflict": "游戏害人 vs 自制力",
     "linked": ["youth-game", "fam-phone"],
     "thesis": ["游戏害人还是帮人？",
                "沉迷游戏怪游戏吗？"],
     "antithesis": ["游戏是原罪？",
                    "孩子玩游戏全怪游戏？"],
     "synthesis": ["玩游戏怎么有度？",
                   "玩游戏和管住自己什么关系？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v37.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v37", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v37: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
