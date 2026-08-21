# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v30：社会变化激化新矛盾（婚内出轨/老年同居/同居分手财产/产后身材/闪婚/目睹家暴的孩子/婚前体检/男性生育年龄）

v1-v29 已覆盖 203 域 245 矛盾 1489 题。v30 聚焦婚姻家庭的非常态与新形态激化矛盾：
  1. 婚内出轨：出轨 vs 原谅
  2. 老年同居：老年同居 vs 领证
  3. 同居分手财产：同居分手 vs 财产
  4. 产后身材：产后身材 vs 恢复
  5. 闪婚：闪婚 vs 了解
  6. 目睹家暴的孩子：孩子目睹 vs 影响
  7. 婚前体检：婚前检查 vs 信任
  8. 男性生育年龄：男性生育 vs 年龄
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "fam-affair", "domain": "婚姻背叛", "need": "背叛后的决定",
     "conflict": "婚内出轨 vs 原谅",
     "linked": ["fam-lies", "fam-sunkcost"],
     "thesis": ["婚内出轨能原谅吗？",
                "出轨该离婚还是原谅？"],
     "antithesis": ["为了孩子不离婚？",
                    "原谅一次，会有第二次？"],
     "synthesis": ["出轨后怎么决定？",
                   "婚姻的信任怎么重建？"]},
    {"id": "fam-eldercohabit", "domain": "老年同居", "need": "同居有保障",
     "conflict": "老年同居 vs 领证",
     "linked": ["fam-elderlove", "fam-cohabit"],
     "thesis": ["为什么老年人选择同居不领证？",
                "老年同居是趋势吗？"],
     "antithesis": ["同居不领证，是不负责？",
                    "领证有保障，为什么不领？"],
     "synthesis": ["老年同居怎么决定？",
                   "老年同居的保障怎么安排？"]},
    {"id": "fam-cohabitreturn", "domain": "同居财产", "need": "同居权益",
     "conflict": "同居分手 vs 财产",
     "linked": ["fam-betrothalreturn", "fam-cohabit"],
     "thesis": ["同居分手财产怎么分？",
                "同居期间的买房怎么算？"],
     "antithesis": ["同居财产是共同财产？",
                    "没结婚，凭什么分？"],
     "synthesis": ["同居财产怎么约定？",
                   "同居期间的权益怎么保护？"]},
    {"id": "gen-postbody", "domain": "产后身体", "need": "产后不焦虑",
     "conflict": "产后身材 vs 恢复",
     "linked": ["gen-postpartum", "health-weight"],
     "thesis": ["为什么产后身材难恢复？",
                "产后身材回不去，正常吗？"],
     "antithesis": ["产后恢复是必须的？",
                    "身材焦虑是矫情吗？"],
     "synthesis": ["产后身材怎么恢复？",
                   "产后身体怎么爱护？"]},
    {"id": "fam-flashmarriage", "domain": "闪婚", "need": "闪婚不后悔",
     "conflict": "闪婚 vs 了解",
     "linked": ["fam-cohabit", "fam-date"],
     "thesis": ["闪婚靠谱吗？",
                "认识三个月结婚，太快了？"],
     "antithesis": ["闪婚是冲动还是缘分？",
                    "恋爱久结婚就稳？"],
     "synthesis": ["闪婚怎么决定？",
                   "闪婚的风险怎么降低？"]},
    {"id": "fam-violencechild", "domain": "家暴孩子", "need": "孩子少受伤",
     "conflict": "孩子目睹家暴 vs 影响",
     "linked": ["fam-violence", "fam-postbirth"],
     "thesis": ["孩子目睹家暴有什么影响？",
                "当着孩子面吵架，没事吗？"],
     "antithesis": ["孩子小，不懂事？",
                    "家暴是夫妻的事，与孩子无关？"],
     "synthesis": ["怎么减少对孩子的伤害？",
                   "目睹家暴的孩子怎么帮助？"]},
    {"id": "fam-premarriagecheck", "domain": "婚前检查", "need": "婚前心里有底",
     "conflict": "婚前体检 vs 信任",
     "linked": ["fam-cohabit", "medical-cost"],
     "thesis": ["婚前体检有必要吗？",
                "婚前检查是信任问题吗？"],
     "antithesis": ["查出来有病，还结婚吗？",
                    "不查，是信任还是侥幸？"],
     "synthesis": ["婚前体检怎么做？",
                   "体检结果怎么面对？"]},
    {"id": "gen-malefertility", "domain": "男性生育", "need": "生育不焦虑",
     "conflict": "男性生育 vs 年龄",
     "linked": ["gen-birthanxiety", "gen-malepressure"],
     "thesis": ["男性生育有年龄限制吗？",
                "男性高龄生育有风险吗？"],
     "antithesis": ["男的50岁还能生？",
                    "男性生育压力大吗？"],
     "synthesis": ["男性生育年龄怎么看？",
                   "生育计划怎么规划？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v30.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v30", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v30: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
