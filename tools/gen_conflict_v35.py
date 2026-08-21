# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v35：社会变化激化新矛盾（孩子独自在家/极端通勤/短剧沉迷/周末安排/空巢期夫妻/暑假安排/家人照护/失能老人照护）

v1-v34 已覆盖 243 域 285 矛盾 1729 题。v35 聚焦家庭场景与生活节奏的激化矛盾：
  1. 孩子独自在家：独立 vs 安全
  2. 极端通勤：通勤 vs 生活
  3. 短剧沉迷：娱乐 vs 沉迷
  4. 周末安排：休息 vs 家庭
  5. 空巢期夫妻：解放 vs 失落
  6. 暑假安排：放松 vs 超车
  7. 家人照护：责任 vs 负担
  8. 失能老人照护：家庭 vs 专业
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "fam-childhome", "domain": "孩子安全", "need": "独立又安全",
     "conflict": "孩子独自在家 vs 安全",
     "linked": ["fam-childprivacy", "public-night"],
     "thesis": ["孩子几岁能独自在家？",
                "孩子独自在家安全吗？"],
     "antithesis": ["孩子独立是锻炼？",
                    "独自在家是冒险？"],
     "synthesis": ["孩子独自在家怎么安排？",
                   "孩子独自在家的安全怎么保障？"]},
    {"id": "work-commute", "domain": "通勤生活", "need": "通勤不消耗",
     "conflict": "极端通勤 vs 生活",
     "linked": ["traffic-jam", "work-burnout"],
     "thesis": ["通勤两小时值得吗？",
                "极端通勤是无奈还是选择？"],
     "antithesis": ["近的工作不好找？",
                    "通勤是打工人常态？"],
     "synthesis": ["通勤怎么优化？",
                   "工作和居住怎么平衡？"]},
    {"id": "digit-drama", "domain": "短剧娱乐", "need": "短剧不沉迷",
     "conflict": "短剧 vs 沉迷",
     "linked": ["digit-scroll", "digit-tipping"],
     "thesis": ["为什么短剧这么上头？",
                "短剧是娱乐还是陷阱？"],
     "antithesis": ["短剧放松一下怎么了？",
                    "短剧比电视剧好看？"],
     "synthesis": ["短剧怎么不沉迷？",
                   "短剧和休息怎么平衡？"]},
    {"id": "fam-weekend", "domain": "周末生活", "need": "周末不累",
     "conflict": "周末休息 vs 家庭",
     "linked": ["fam-trip", "fam-schedule"],
     "thesis": ["周末该干嘛？",
                "周末是休息还是陪家人？"],
     "antithesis": ["周末补觉不行吗？",
                    "周末被安排，累不累？"],
     "synthesis": ["周末怎么安排？",
                   "休息和家庭怎么平衡？"]},
    {"id": "fam-empty", "domain": "空巢期", "need": "空巢不空虚",
     "conflict": "空巢期 vs 解放/失落",
     "linked": ["fam-solitude", "fam-postbirth"],
     "thesis": ["孩子离家后夫妻怎么办？",
                "空巢期是解放还是失落？"],
     "antithesis": ["空巢是自由？",
                    "空巢是空虚？"],
     "synthesis": ["空巢期夫妻怎么过？",
                   "空巢期怎么重新开始？"]},
    {"id": "fam-summer", "domain": "暑假安排", "need": "暑假两不误",
     "conflict": "暑假放松 vs 弯道超车",
     "linked": ["edu-hobby", "fam-weekend"],
     "thesis": ["暑假怎么安排孩子？",
                "暑假是放松还是弯道超车？"],
     "antithesis": ["暑假玩，开学落后？",
                    "暑假排满，孩子太累？"],
     "synthesis": ["暑假怎么安排合理？",
                   "学习和玩怎么平衡？"]},
    {"id": "fam-caregiving", "domain": "家人照护", "need": "照护不垮",
     "conflict": "家人照护 vs 责任/负担",
     "linked": ["med-accompany", "fam-couple"],
     "thesis": ["家人病了谁来照顾？",
                "照顾病人是责任还是负担？"],
     "antithesis": ["照顾是应该的？",
                    "照顾病人，谁来照顾照顾者？"],
     "synthesis": ["家人照护怎么安排？",
                   "照护者怎么照顾自己？"]},
    {"id": "fam-disabled", "domain": "失能照护", "need": "失能有出路",
     "conflict": "失能老人 vs 家庭/专业",
     "linked": ["med-eldercare", "fam-eldercare3"],
     "thesis": ["失能老人谁来照顾？",
                "失能照护是家庭能扛的吗？"],
     "antithesis": ["送机构是不孝？",
                    "失能照护是专业的事？"],
     "synthesis": ["失能照护怎么安排？",
                   "失能家庭怎么获得支持？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v35.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v35", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v35: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
