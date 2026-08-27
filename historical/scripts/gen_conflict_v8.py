# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v8：新矛盾域（性别/代际数字/教育就业/舆论/心理/城市治理）

v1-v7 已覆盖 31 域 72 矛盾 433 题。v8 新域：
  1. 性别议题：职场性别/家务分工/性别刻板
  2. 老年数字鸿沟：老人用手机难/数字服务排斥老人
  3. 教育就业错配：专业与市场/学历贬值
  4. 公共舆论：网络暴力/信息茧房/谣言
  5. 心理健康：抑郁/焦虑/内耗
  6. 城市治理：共享单车/噪音/宠物
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "gen-work", "domain": "性别议题", "need": "性别平等的职业发展",
     "conflict": "职场性别偏见（晋升/薪酬/产假歧视）vs 公平",
     "linked": ["work-pay", "fam-birth"],
     "thesis": ["为什么职场对女性有天花板？",
                "同工不同酬公平吗？"],
     "antithesis": ["女性要生孩子照顾家，企业顾虑有道理吗？",
                    "性别配额是不是另一种不平等？"],
     "synthesis": ["怎么打破职场性别天花板？",
                   "性别平等怎么做才真公平？"]},
    {"id": "gen-house", "domain": "性别议题", "need": "家务劳动被看见",
     "conflict": "隐形家务（育儿/家务/人情）vs 分工失衡",
     "linked": ["fam-couple", "work-pay"],
     "thesis": ["为什么家务总是女性在做？",
                "全职主妇的价值被低估了吗？"],
     "antithesis": ["男的赚钱养家，女的管好家，分工有错吗？",
                    "家务是小事，计较是不是矫情？"],
     "synthesis": ["怎么让家务分工更公平？",
                   "全职主妇/主夫的价值怎么衡量？"]},
    {"id": "age-digital", "domain": "老年数字", "need": "老人融入数字生活",
     "conflict": "数字化服务（挂号/支付/扫码）vs 老人不会用",
     "linked": ["digit-privacy", "fam-eldercare"],
     "thesis": ["为什么老人用手机这么难？",
                "不会扫码挂号，老人怎么办？"],
     "antithesis": ["老人多学学就会了，是不是懒得学？",
                    "数字时代淘汰跟不上的人，正常吗？"],
     "synthesis": ["怎么帮老人跨越数字鸿沟？",
                   "公共服务该不该保留人工窗口？"]},
    {"id": "edu-job", "domain": "教育就业", "need": "学有所用",
     "conflict": "专业与市场错配（学非所用）vs 就业压力",
     "linked": ["edu-score", "work-layoff"],
     "thesis": ["为什么学的东西工作用不上？",
                "大学专业和工作不对口正常吗？"],
     "antithesis": ["大学教的是思维不是技能，是不是也行？",
                    "学历贬值了，读书还有用吗？"],
     "synthesis": ["怎么选专业才不后悔？",
                   "学历和能力哪个更重要？"]},
    {"id": "pub-violence", "domain": "公共舆论", "need": "网络言论自由",
     "conflict": "网络匿名表达 vs 网络暴力/网暴",
     "linked": ["digit-privacy", "psy-appearance"],
     "thesis": ["为什么网上骂人不用负责？",
                "被网暴了怎么办？"],
     "antithesis": ["言论自由就该百无禁忌吗？",
                    "网暴受害者是不是也活该（做了错事）？"],
     "synthesis": ["怎么治理网络暴力？",
                   "被网暴的人怎么自救？"]},
    {"id": "psy-anxiety", "domain": "心理健康", "need": "情绪被接纳",
     "conflict": "抑郁焦虑的真实痛苦 vs 污名化/忽视",
     "linked": ["psy-lonely", "work-burnout"],
     "thesis": ["为什么现在抑郁焦虑的人这么多？",
                "心理问题是不是矫情？"],
     "antithesis": ["别人也难，怎么就你扛不住？",
                    "心理问题吃药有用吗？"],
     "synthesis": ["怎么判断自己需不需要心理帮助？",
                   "怎么和抑郁的人相处？"]},
    {"id": "city-share", "domain": "城市治理", "need": "共享便利",
     "conflict": "共享单车/电动车的便利 vs 乱停乱放/管理",
     "linked": ["gov-reg", "soc-urban"],
     "thesis": ["为什么共享单车到处都是乱的？",
                "共享经济是便利还是麻烦？"],
     "antithesis": ["方便的时候不说，乱一点就抱怨？",
                    "是不是该取消共享单车？"],
     "synthesis": ["共享单车怎么管才不乱？",
                   "共享经济和城市秩序怎么平衡？"]},
    {"id": "city-pet", "domain": "城市治理", "need": "养宠自由",
     "conflict": "养宠（陪伴/快乐）vs 扰民（吠叫/粪便/伤人）",
     "linked": ["social-boundary", "psy-lonely"],
     "thesis": ["为什么城市养宠矛盾这么多？",
                "遛狗不拴绳该不该罚？"],
     "antithesis": ["狗是人类朋友，拴着多残忍？",
                    "怕狗的人是不是太矫情？"],
     "synthesis": ["养宠和怕宠的人怎么共处？",
                   "城市养宠怎么规范？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v8.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v8", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v8: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
