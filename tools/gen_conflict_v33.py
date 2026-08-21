# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v33：社会变化激化新矛盾（夫妻健康观念/家庭养宠之争/家庭买车/成年兄弟姐妹/夫妻共同目标/远程办公家庭/父母健康管理/孩子隐私）

v1-v32 已覆盖 227 域 269 矛盾 1633 题。v33 聚焦家庭生活决策与代际互动的激化矛盾：
  1. 夫妻健康观念：体检/养生/就医分歧
  2. 家庭养宠之争：养宠 vs 不养
  3. 家庭买车：买车 vs 不买
  4. 成年兄弟姐妹：手足关系 vs 利益
  5. 夫妻共同目标：共同 vs 各自
  6. 远程办公家庭：远程工作 vs 家庭
  7. 父母健康管理：劝父母体检 vs 尊重
  8. 孩子隐私：日记/房间 vs 关心
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "fam-health", "domain": "夫妻健康", "need": "健康观念合拍",
     "conflict": "夫妻健康观念 vs 统一",
     "linked": ["fam-couple", "medical-cost"],
     "thesis": ["夫妻健康观念不同怎么办？",
                "他不体检，我劝不动？"],
     "antithesis": ["养生是矫情？",
                    "健康是自己的事？"],
     "synthesis": ["夫妻健康怎么互相督促？",
                   "健康观念怎么统一？"]},
    {"id": "fam-pet", "domain": "家庭养宠", "need": "养宠不吵架",
     "conflict": "家庭养宠 vs 责任",
     "linked": ["city-pet", "fam-couple"],
     "thesis": ["家里要不要养宠物？",
                "他想养，我不想养？"],
     "antithesis": ["养宠是爱心？",
                    "养宠是负担？"],
     "synthesis": ["养宠怎么决定？",
                   "养宠的责任怎么分配？"]},
    {"id": "fam-car", "domain": "家庭买车", "need": "买车不后悔",
     "conflict": "家庭买车 vs 刚需/面子",
     "linked": ["traffic-jam", "fam-decision"],
     "thesis": ["家里要不要买车？",
                "买车是刚需还是面子？"],
     "antithesis": ["有车方便？",
                    "养车是负担？"],
     "synthesis": ["买车怎么决定？",
                   "用车怎么安排？"]},
    {"id": "fam-sibling", "domain": "手足关系", "need": "手足不伤情",
     "conflict": "成年兄弟姐妹 vs 利益",
     "linked": ["fam-inheritance", "fam-eldercare"],
     "thesis": ["成年兄弟姐妹怎么相处？",
                "手足之间要谈钱吗？"],
     "antithesis": ["血浓于水？",
                    "亲兄弟明算账？"],
     "synthesis": ["兄弟姐妹怎么处？",
                   "手足和利益怎么平衡？"]},
    {"id": "fam-couplegoals", "domain": "夫妻目标", "need": "目标同向",
     "conflict": "夫妻共同目标 vs 各自追求",
     "linked": ["fam-growth", "fam-couple"],
     "thesis": ["夫妻要有共同目标吗？",
                "各自追求，行吗？"],
     "antithesis": ["目标是绑在一起？",
                    "没有目标也能过？"],
     "synthesis": ["夫妻怎么定共同目标？",
                   "共同和各自怎么平衡？"]},
    {"id": "fam-remotework", "domain": "远程家庭", "need": "工作家庭分界",
     "conflict": "远程工作 vs 家庭",
     "linked": ["work-remote", "digit-familytime"],
     "thesis": ["远程工作会影响家庭吗？",
                "在家上班是自由还是混乱？"],
     "antithesis": ["在家上班，家庭工作分不开？",
                    "远程工作是好是坏？"],
     "synthesis": ["远程办公家庭怎么安排？",
                   "工作和家庭怎么分界？"]},
    {"id": "fam-elderlyhealth", "domain": "父母健康", "need": "关心不越界",
     "conflict": "劝父母体检 vs 尊重",
     "linked": ["fam-eldercare3", "medical-cost"],
     "thesis": ["怎么劝父母体检？",
                "父母讳疾忌医怎么办？"],
     "antithesis": ["父母身体自己做主？",
                    "不管父母，是失职吗？"],
     "synthesis": ["父母健康怎么管？",
                   "关心和尊重怎么平衡？"]},
    {"id": "fam-childprivacy", "domain": "孩子隐私", "need": "尊重孩子",
     "conflict": "孩子隐私 vs 关心",
     "linked": ["edu-punish", "fam-phone"],
     "thesis": ["父母该看孩子日记吗？",
                "孩子的隐私重要吗？"],
     "antithesis": ["孩子有什么隐私？",
                    "看日记是关心？"],
     "synthesis": ["孩子隐私怎么尊重？",
                   "关心和边界怎么平衡？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v33.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v33", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v33: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
