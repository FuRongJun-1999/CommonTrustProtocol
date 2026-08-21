# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v28：社会变化激化新矛盾（恋爱消费/夫妻查手机/生育后夫妻/家务补偿/孕期职场/婚姻激情消退/岳母女婿/家族群）

v1-v27 已覆盖 187 域 229 矛盾 1393 题。v28 聚焦婚姻家庭关系细节的社会激化新矛盾：
  1. 恋爱消费：恋爱谁花钱 vs AA
  2. 夫妻查手机：查手机 vs 隐私
  3. 生育后夫妻：生娃后关系变淡
  4. 家务补偿：离婚家务补偿 vs 权益
  5. 孕期职场：怀孕被辞退 vs 权益
  6. 婚姻激情消退：激情褪去 vs 经营
  7. 岳母女婿：岳母女婿矛盾 vs 婆媳对照
  8. 家族群：家族群 vs 压力
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "fam-dateexpense", "domain": "恋爱消费", "need": "花钱不伤情",
     "conflict": "恋爱谁花钱 vs AA",
     "linked": ["fam-aa", "fam-date"],
     "thesis": ["恋爱中谁该花钱？",
                "恋爱AA，伤感情吗？"],
     "antithesis": ["男生买单是应该的？",
                    "恋爱花钱是投资吗？"],
     "synthesis": ["恋爱消费怎么分担？",
                   "恋爱和钱怎么处理？"]},
    {"id": "fam-phone", "domain": "夫妻隐私", "need": "信任与隐私",
     "conflict": "查手机 vs 隐私",
     "linked": ["fam-friendboundary", "digit-privacy"],
     "thesis": ["夫妻该互相查手机吗？",
                "查手机是爱还是控制？"],
     "antithesis": ["不查手机，怎么知道忠诚？",
                    "隐私在婚姻里重要吗？"],
     "synthesis": ["夫妻手机边界怎么定？",
                   "信任和隐私怎么平衡？"]},
    {"id": "fam-postbirth", "domain": "产后婚姻", "need": "有娃不忘爱人",
     "conflict": "生娃后夫妻关系变淡",
     "linked": ["fam-parenting", "fam-couple"],
     "thesis": ["为什么生娃后夫妻关系变淡？",
                "有了孩子忘了爱人？"],
     "antithesis": ["孩子是家庭的中心，不对吗？",
                    "夫妻感情可以等孩子大点再说？"],
     "synthesis": ["生娃后夫妻感情怎么保鲜？",
                   "育儿和婚姻怎么兼顾？"]},
    {"id": "fam-houseworkcomp", "domain": "家务价值", "need": "家务被承认",
     "conflict": "家务补偿 vs 权益",
     "linked": ["fam-division", "gen-house"],
     "thesis": ["全职主妇离婚有家务补偿吗？",
                "家务劳动值多少钱？"],
     "antithesis": ["家务是爱的付出，要算钱吗？",
                    "补偿是让婚姻变买卖吗？"],
     "synthesis": ["家务补偿怎么算？",
                   "家务价值怎么被承认？"]},
    {"id": "fam-pregnancywork", "domain": "孕期职场", "need": "孕期不被歧视",
     "conflict": "孕期职场权益 vs 企业负担",
     "linked": ["gen-hiring", "gen-stayhome"],
     "thesis": ["怀孕会被辞退吗？",
                "孕期被调岗降薪，合法吗？"],
     "antithesis": ["企业怕负担，有错吗？",
                    "孕期上班，是正常职场吗？"],
     "synthesis": ["孕期职场权益怎么保护？",
                   "孕期上班怎么应对？"]},
    {"id": "fam-intimacy", "domain": "婚姻经营", "need": "激情不褪",
     "conflict": "婚后激情消退 vs 经营",
     "linked": ["fam-couple", "fam-sunkcost"],
     "thesis": ["为什么婚后激情会消退？",
                "老夫老妻就该平淡吗？"],
     "antithesis": ["激情消退是自然规律？",
                    "平淡就是不爱了吗？"],
     "synthesis": ["婚姻激情怎么保鲜？",
                   "平淡和激情怎么平衡？"]},
    {"id": "fam-mil4", "domain": "姻亲关系", "need": "两家都处好",
     "conflict": "岳母女婿矛盾 vs 婆媳对照",
     "linked": ["fam-mil3", "fam-couple"],
     "thesis": ["为什么岳母女婿也有矛盾？",
                "女婿和岳母怎么处？"],
     "antithesis": ["岳母疼女儿，有错吗？",
                    "女婿是半个儿，对吗？"],
     "synthesis": ["岳母女婿怎么相处？",
                   "两家的关系怎么平衡？"]},
    {"id": "fam-groupchat", "domain": "家庭联络", "need": "亲情不绑架",
     "conflict": "家族群 vs 压力",
     "linked": ["fam-gener", "digit-scroll"],
     "thesis": ["为什么家族群让人压力大？",
                "家族群的养生文章怎么办？"],
     "antithesis": ["家族群是亲情纽带？",
                    "家族群是情感绑架吗？"],
     "synthesis": ["家族群怎么相处？",
                   "家族群的边界怎么定？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v28.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v28", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v28: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
