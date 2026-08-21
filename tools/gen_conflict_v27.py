# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v27：社会变化激化新矛盾（彩礼返还/婚姻精神操控/试管婴儿压力/相亲骗局/未婚先孕/家暴求助/单亲爸爸/老年离婚）

v1-v26 已覆盖 179 域 221 矛盾 1345 题。v27 聚焦婚姻与生育议题的深层激化新矛盾：
  1. 彩礼返还：分手/离婚礼金怎么退
  2. 婚姻精神操控：亲密关系PUA vs 伤害
  3. 试管婴儿压力：辅助生殖 vs 身心代价
  4. 相亲骗局：婚托/相亲机构 vs 防骗
  5. 未婚先孕：意外怀孕 vs 选择
  6. 家暴求助：家暴 vs 识别求助
  7. 单亲爸爸：单亲爸爸 vs 养育
  8. 老年离婚：老年离婚 vs 观念
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "fam-betrothalreturn", "domain": "彩礼纠纷", "need": "礼金不纠纷",
     "conflict": "分手/离婚礼金 vs 返还",
     "linked": ["fam-betrothal", "fam-division"],
     "thesis": ["分手了订婚礼金要退吗？",
                "离婚时收的礼金该还吗？"],
     "antithesis": ["礼金是诚意，退什么退？",
                    "礼金是买卖吗？"],
     "synthesis": ["礼金纠纷怎么处理？",
                   "礼金怎么给不伤感情不惹纠纷？"]},
    {"id": "fam-maritalpua", "domain": "婚姻心理", "need": "不被操控",
     "conflict": "婚姻精神操控 vs 伤害",
     "linked": ["fam-coldviolence", "emp-pua"],
     "thesis": ["什么是婚姻中的精神操控？",
                "亲密关系也会PUA吗？"],
     "antithesis": ["操控是爱得太深？",
                    "被操控是自己想太多？"],
     "synthesis": ["精神操控怎么识别？",
                   "婚姻PUA怎么摆脱？"]},
    {"id": "gen-ivf", "domain": "辅助生殖", "need": "生育压力被理解",
     "conflict": "试管婴儿 vs 身心代价",
     "linked": ["gen-birthanxiety", "medical-cost"],
     "thesis": ["为什么选择试管婴儿？",
                "试管婴儿对身体伤害大吗？"],
     "antithesis": ["生不了就试管，值得吗？",
                    "试管是希望还是执念？"],
     "synthesis": ["试管婴儿怎么决定？",
                   "生育压力怎么面对？"]},
    {"id": "fam-datingscam", "domain": "相亲安全", "need": "相亲不被骗",
     "conflict": "相亲骗局 vs 防骗",
     "linked": ["digit-dating", "fam-date"],
     "thesis": ["为什么相亲总遇骗局？",
                "婚托怎么识别？"],
     "antithesis": ["相亲机构是正规服务？",
                    "被骗是自己不小心？"],
     "synthesis": ["相亲怎么防骗？",
                   "相亲机构怎么选？"]},
    {"id": "fam-unplanned", "domain": "意外怀孕", "need": "选择被尊重",
     "conflict": "未婚先孕 vs 选择",
     "linked": ["gen-birthanxiety", "fam-cohabit"],
     "thesis": ["未婚先孕怎么办？",
                "意外怀孕是危机还是选择？"],
     "antithesis": ["未婚先孕丢人吗？",
                    "奉子成婚，能幸福吗？"],
     "synthesis": ["未婚先孕怎么决定？",
                   "意外怀孕怎么面对？"]},
    {"id": "fam-violence", "domain": "家庭暴力", "need": "家暴不被忍",
     "conflict": "家暴 vs 识别求助",
     "linked": ["fam-coldviolence", "fam-fincontrol"],
     "thesis": ["家暴为什么难以摆脱？",
                "被打为什么不报警？"],
     "antithesis": ["家暴是家务事？",
                    "被打忍忍就过去了吗？"],
     "synthesis": ["家暴怎么识别和求助？",
                   "被家暴怎么保护自己？"]},
    {"id": "gen-singleparent", "domain": "单亲爸爸", "need": "爸爸也能带娃",
     "conflict": "单亲爸爸 vs 养育",
     "linked": ["fam-singlemom", "gen-staydad"],
     "thesis": ["单亲爸爸带孩子行吗？",
                "单亲爸爸和单亲妈妈一样难吗？"],
     "antithesis": ["爸爸带娃，能行吗？",
                    "单亲爸爸需要帮助吗？"],
     "synthesis": ["单亲爸爸怎么带好娃？",
                   "单亲爸爸怎么获得支持？"]},
    {"id": "fam-elderdivorce", "domain": "老年婚姻", "need": "晚年不将就",
     "conflict": "老年离婚 vs 观念",
     "linked": ["fam-sunkcost", "fam-elderlove"],
     "thesis": ["为什么老年人也离婚？",
                "老了还离婚，值得吗？"],
     "antithesis": ["忍了一辈子，为什么不忍了？",
                    "老年离婚是自由还是冲动？"],
     "synthesis": ["老年离婚怎么面对？",
                   "老年婚姻怎么经营？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v27.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v27", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v27: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
