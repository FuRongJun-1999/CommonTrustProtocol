# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v13：新矛盾域（断舍离/宠物医疗/相亲条件/酒桌文化/学车驾考/无障碍出行/退休再就业/垃圾分类）

v1-v12 已覆盖 67 域 109 矛盾 673 题。v13 新域（生活矛盾再细化）：
  1. 断舍离：囤积 vs 极简/解脱
  2. 宠物医疗：宠物看病贵 vs 弃养/值不值
  3. 相亲条件：相亲看条件 vs 感情
  4. 酒桌文化：劝酒 vs 健康/自愿
  5. 学车驾考：驾校乱象 vs 拿证刚需
  6. 无障碍出行：残障出行 vs 设施不足
  7. 退休再就业：退休后再就业 vs 年龄/体面
  8. 垃圾分类：分类麻烦 vs 环境
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "soc-declutter", "domain": "生活方式", "need": "空间清爽",
     "conflict": "囤积/留着 vs 断舍离/极简",
     "linked": ["soc-consumer", "digit-live"],
     "thesis": ["为什么东西越攒越多？",
                "断舍离是浪费还是解脱？"],
     "antithesis": ["留着说不定有用，扔了才浪费？",
                    "断舍离是极简主义矫情吗？"],
     "synthesis": ["怎么断舍离不后悔？",
                   "家里的东西怎么整理？"]},
    {"id": "pet-medical", "domain": "养宠生活", "need": "宠物健康",
     "conflict": "宠物看病贵 vs 弃养/值不值",
     "linked": ["city-pet", "medical-cost"],
     "thesis": ["为什么宠物看病这么贵？",
                "宠物生病花几万值吗？"],
     "antithesis": ["宠物也是家人，花钱有错吗？",
                    "看不起病就弃养，人渣吗？"],
     "synthesis": ["宠物医疗怎么省钱又负责？",
                   "养宠物要花多少钱想清楚了吗？"]},
    {"id": "fam-date", "domain": "婚恋关系", "need": "婚姻的匹配",
     "conflict": "相亲看条件 vs 感情",
     "linked": ["fam-betrothal", "relation-attach"],
     "thesis": ["为什么相亲都看条件？",
                "相亲看条件是不是太现实？"],
     "antithesis": ["不看条件，爱情能当饭吃吗？",
                    "条件好就一定合适吗？"],
     "synthesis": ["相亲怎么平衡条件和感情？",
                   "相亲该看重什么？"]},
    {"id": "social-toast", "domain": "社交习俗", "need": "拒绝的自由",
     "conflict": "劝酒 vs 健康/自愿",
     "linked": ["work-age35", "social-boundary"],
     "thesis": ["为什么酒桌总要劝酒？",
                "不喝酒是不是不给面子？"],
     "antithesis": ["喝点酒增进感情，有错吗？",
                    "劝酒是热情不是恶意吧？"],
     "synthesis": ["怎么礼貌地拒酒？",
                   "酒桌文化怎么变？"]},
    {"id": "edu-driving", "domain": "技能学习", "need": "拿证顺利",
     "conflict": "驾校乱象 vs 拿证刚需",
     "linked": ["edu-job", "gov-reg"],
     "thesis": ["为什么驾校教练这么凶？",
                "学车为什么要送礼？"],
     "antithesis": ["教练严一点，上路才安全？",
                    "驾考难一点不好吗？"],
     "synthesis": ["怎么选驾校不被坑？",
                   "学车怎么少受气？"]},
    {"id": "city-accessibility", "domain": "城市文明", "need": "人人能出行",
     "conflict": "残障出行 vs 设施不足/占用",
     "linked": ["age-digital", "city-elevator"],
     "thesis": ["为什么盲道总被占用？",
                "轮椅出行为什么这么难？"],
     "antithesis": ["无障碍设施少，谁的责任？",
                    "健全人占无障碍设施，至于吗？"],
     "synthesis": ["怎么让城市对残障友好？",
                   "无障碍设施怎么管？"]},
    {"id": "work-rehire", "domain": "老年就业", "need": "老有所为",
     "conflict": "退休后再就业 vs 年龄/体面",
     "linked": ["work-age35", "soc-aging"],
     "thesis": ["为什么退休了还想找工作？",
                "老年人再就业为什么难？"],
     "antithesis": ["退休了享清福不好吗？",
                    "老人返聘，年轻人就业更紧张？"],
     "synthesis": ["退休后再就业怎么安排？",
                   "老年劳动力怎么用？"]},
    {"id": "env-sort", "domain": "环境保护", "need": "环境好",
     "conflict": "分类麻烦 vs 环境收益",
     "linked": ["plastic-waste", "gov-reg"],
     "thesis": ["为什么垃圾分类这么麻烦？",
                "分好的垃圾最后还是一起烧吗？"],
     "antithesis": ["不分类，垃圾去哪？",
                    "分类麻烦点，环境好点不好吗？"],
     "synthesis": ["怎么分类不麻烦？",
                   "垃圾分类怎么坚持？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v13.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v13", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v13: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
