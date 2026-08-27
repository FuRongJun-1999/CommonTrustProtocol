# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v20：新矛盾域（儿童性教育/宠物保险/大学生考证/医院陪护/儿童护牙/网购退货/老年人运动/辅导作业）

v1-v19 已覆盖 123 域 165 矛盾 1009 题。v20 新域（生活矛盾再细化）：
  1. 儿童性教育：性教育 vs 羞耻/保护
  2. 宠物保险：宠物保险 vs 值不值
  3. 大学生考证：考证 vs 含金量
  4. 医院陪护：住院陪护 vs 家庭负担
  5. 儿童护牙：蛀牙 vs 护牙习惯
  6. 网购退货：退货 vs 运费/浪费
  7. 老年人运动：运动 vs 受伤风险
  8. 辅导作业：辅导 vs 亲子关系
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "edu-sexed", "domain": "儿童教育", "need": "孩子的安全",
     "conflict": "性教育 vs 羞耻/教坏",
     "linked": ["edu-punish", "digit-scam"],
     "thesis": ["为什么孩子要接受性教育？",
                "性教育会不会教坏孩子？"],
     "antithesis": ["孩子还小，讲这个合适吗？",
                    "性教育是家长的事还是学校的事？"],
     "synthesis": ["儿童性教育怎么做？",
                   "怎么教孩子保护自己？"]},
    {"id": "pet-insurance", "domain": "养宠保障", "need": "宠物看病不慌",
     "conflict": "宠物保险 vs 值不值",
     "linked": ["pet-medical", "fin-childinsurance"],
     "thesis": ["宠物保险有必要买吗？",
                "宠物看病这么贵，保险能报吗？"],
     "antithesis": ["给宠物买保险，值得吗？",
                    "宠物保险是智商税吗？"],
     "synthesis": ["宠物保险怎么买？",
                   "宠物看病怎么省钱？"]},
    {"id": "edu-cert", "domain": "职业准备", "need": "证书有用",
     "conflict": "考证热 vs 含金量",
     "linked": ["edu-job", "study-kaoyan"],
     "thesis": ["为什么大学生都在考证？",
                "证书真的有用吗？"],
     "antithesis": ["多考一个证，多一条路？",
                    "考证是投资还是焦虑？"],
     "synthesis": ["证该怎么考？",
                   "证书和能力怎么选？"]},
    {"id": "med-accompany", "domain": "医疗照护", "need": "住院有人管",
     "conflict": "家属陪护 vs 家庭负担",
     "linked": ["medical-cost", "fam-eldercare"],
     "thesis": ["为什么住院要家属陪护？",
                "陪护是义务还是负担？"],
     "antithesis": ["医院不管陪护，合理吗？",
                    "请护工贵，家属陪省钱？"],
     "synthesis": ["住院陪护怎么安排？",
                   "医院陪护制度怎么改？"]},
    {"id": "health-teeth", "domain": "儿童健康", "need": "一口好牙",
     "conflict": "蛀牙 vs 护牙习惯",
     "linked": ["health-medicine", "health-weight"],
     "thesis": ["为什么孩子蛀牙这么多？",
                "刷牙为什么还蛀牙？"],
     "antithesis": ["乳牙会换，蛀了没事？",
                    "孩子不爱刷牙，怎么办？"],
     "synthesis": ["儿童护牙怎么做？",
                   "蛀牙怎么预防？"]},
    {"id": "soc-return", "domain": "线上消费", "need": "买得放心退得方便",
     "conflict": "退货 vs 运费/浪费",
     "linked": ["digit-live", "soc-secondhand"],
     "thesis": ["为什么网购退货这么多？",
                "退货是权利还是滥用？"],
     "antithesis": ["不合适就退，有错吗？",
                    "退货让商家亏钱，内疚吗？"],
     "synthesis": ["网购怎么减少退货？",
                   "退货怎么退不亏？"]},
    {"id": "health-exercise", "domain": "老年健康", "need": "动得安全",
     "conflict": "运动 vs 受伤风险",
     "linked": ["health-fall", "fam-solitude"],
     "thesis": ["老人该运动吗？",
                "老人运动会受伤吗？"],
     "antithesis": ["老人就该静养，动什么动？",
                    "广场舞/暴走，伤膝盖怎么办？"],
     "synthesis": ["老人怎么运动不受伤？",
                   "适合老人的运动有哪些？"]},
    {"id": "edu-homework", "domain": "家庭教育", "need": "辅导不崩溃",
     "conflict": "辅导作业 vs 亲子关系",
     "linked": ["edu-score", "fam-parenting"],
     "thesis": ["为什么辅导作业这么崩溃？",
                "辅导作业是父母的必修课吗？"],
     "antithesis": ["不辅导，孩子学不会？",
                    "辅导崩溃，是孩子笨吗？"],
     "synthesis": ["辅导作业怎么不崩溃？",
                   "作业辅导和独立怎么平衡？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v20.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v20", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v20: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
