# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v19：新矛盾域（儿童电话手表/高血压用药/大学生宿舍/老人防跌倒/儿童保险/博物馆预约/宠物绝育/公交让座）

v1-v18 已覆盖 115 域 157 矛盾 961 题。v19 新域（生活矛盾再细化）：
  1. 儿童电话手表：手表社交 vs 学校管理
  2. 高血压用药：降压药天天吃 vs 停药风险
  3. 大学生宿舍：宿舍矛盾 vs 相处
  4. 老人防跌倒：跌倒 vs 预防
  5. 儿童保险：儿童保险 vs 智商税
  6. 博物馆预约：免费预约 vs 黄牛/难约
  7. 宠物绝育：绝育 vs 残忍
  8. 公交让座：让座 vs 道德绑架
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "digit-watch", "domain": "儿童数字", "need": "安全与专注",
     "conflict": "电话手表社交 vs 学校管理",
     "linked": ["digit-scroll", "edu-punish"],
     "thesis": ["为什么孩子都想要电话手表？",
                "电话手表是必需品还是攀比？"],
     "antithesis": ["手表能联系孩子，有错吗？",
                    "学校不让戴手表，对吗？"],
     "synthesis": ["电话手表怎么用不沉迷？",
                   "儿童手表怎么选？"]},
    {"id": "health-hypertension", "domain": "慢病管理", "need": "血压平稳",
     "conflict": "降压药天天吃 vs 停药风险",
     "linked": ["medical-cost", "health-medicine"],
     "thesis": ["为什么高血压要天天吃药？",
                "降压药有副作用吗？"],
     "antithesis": ["血压正常了，停药行吗？",
                    "是药三分毒，能不吃就不吃？"],
     "synthesis": ["高血压怎么科学用药？",
                   "降压药怎么吃才安全？"]},
    {"id": "edu-dorm", "domain": "校园生活", "need": "宿舍和谐",
     "conflict": "宿舍矛盾 vs 相处",
     "linked": ["psy-lonely", "social-boundary"],
     "thesis": ["为什么宿舍矛盾这么多？",
                "室友打呼噜怎么办？"],
     "antithesis": ["宿舍是公共的，忍忍不行吗？",
                    "矛盾是小事，至于吗？"],
     "synthesis": ["宿舍矛盾怎么解决？",
                   "和室友怎么相处？"]},
    {"id": "health-fall", "domain": "老年健康", "need": "老人不摔跤",
     "conflict": "跌倒风险 vs 预防投入",
     "linked": ["med-eldercare", "fam-solitude"],
     "thesis": ["为什么老人容易摔倒？",
                "老人摔倒有多危险？"],
     "antithesis": ["老人自己能走，扶什么扶？",
                    "摔倒就摔倒，注意点不就行了？"],
     "synthesis": ["老人怎么防跌倒？",
                   "老人摔倒怎么处理？"]},
    {"id": "fin-childinsurance", "domain": "家庭保障", "need": "孩子有保障",
     "conflict": "儿童保险 vs 智商税",
     "linked": ["medical-cost", "fin-wealth"],
     "thesis": ["为什么儿童保险这么火？",
                "儿童保险有必要买吗？"],
     "antithesis": ["给孩子买保险，有错吗？",
                    "保险是骗人的吗？"],
     "synthesis": ["儿童保险怎么买不踩坑？",
                   "孩子的保障怎么配？"]},
    {"id": "culture-museum", "domain": "公共文化", "need": "免费资源人人可享",
     "conflict": "免费预约 vs 黄牛/难约",
     "linked": ["culture-ticket", "gov-reg"],
     "thesis": ["为什么博物馆也要预约？",
                "博物馆免费预约怎么还这么难？"],
     "antithesis": ["免费预约，公平吗？",
                    "黄牛倒票，怎么治？"],
     "synthesis": ["博物馆怎么约到票？",
                   "免费资源怎么公平分配？"]},
    {"id": "pet-spay", "domain": "宠物健康", "need": "宠物与城市和谐",
     "conflict": "绝育 vs 残忍/必要",
     "linked": ["pet-medical", "city-pet"],
     "thesis": ["为什么宠物要绝育？",
                "绝育对宠物残忍吗？"],
     "antithesis": ["绝育是爱还是伤害？",
                    "不绝育，宠物怎么办？"],
     "synthesis": ["宠物绝育怎么决定？",
                   "流浪猫狗怎么治理？"]},
    {"id": "public-seat", "domain": "公共礼仪", "need": "座位与善意",
     "conflict": "让座 vs 道德绑架",
     "linked": ["public-civility", "age-digital"],
     "thesis": ["为什么让座总有争议？",
                "该不该给老人让座？"],
     "antithesis": ["让座是情分不是本分？",
                    "老人不感谢，还让吗？"],
     "synthesis": ["让座怎么不尴尬？",
                   "公交座位怎么分配？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v19.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v19", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v19: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
