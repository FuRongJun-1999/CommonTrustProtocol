# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 · 矛盾清单 v2（荣方法论 · 7 大关系域扩展）

从 8 域扩展到 7 大关系域，每域多个具体矛盾。每个矛盾 = 人的需要 ×
现实约束的张力，按正反合展开（矛盾论：正题→反题→合题）。

域结构：
  family-self  家庭个体内部（欲望vs自律/理想vs现实/躺平vs奋斗）
  family       家庭成员间（夫妻/代际/经济）
  edu-sys      教育制度（应试vs素质/减负vs竞争/资源不均）
  teacher      师生关系（权威vs质疑/公平vs偏爱/惩戒vs体罚）
  work-emp     企业与员工（贡献vs报酬/忠诚vs跳槽/加班vs生活）
  gov-corps    政府与企业（监管vs创新/扶持vs垄断/环保vs发展）
  intl         国家之间（竞争vs合作/封锁vs自主/贸易战）
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    # ============ 家庭个体内部 ============
    {"id": "self-lazy", "domain": "家庭个体", "need": "想休息与娱乐（即时满足）",
     "conflict": "需要自律完成目标（延迟满足）——本我vs超我",
     "thesis": ["为什么我总是一边想努力一边控制不住玩手机？",
                "为什么道理都懂就是做不到？"],
     "antithesis": ["是不是我就是没有毅力的人？",
                    "别人都能自律，为什么我不行？"],
     "synthesis": ["怎么让自己真的行动起来而不是继续内耗？",
                   "怎么和『想躺平』的自己和解？"]},
    {"id": "self-ideal", "domain": "家庭个体", "need": "实现理想/成为想成为的人",
     "conflict": "现实条件（能力/金钱/年龄）限制理想",
     "thesis": ["为什么理想和现实的差距这么大？",
                "感觉自己在虚度人生怎么办？"],
     "antithesis": ["是不是我注定就是个普通人？",
                    "现在努力还来得及吗？"],
     "synthesis": ["怎么找到自己真正想要的生活？",
                   "怎么在普通里过出意义感？"]},
    # ============ 家庭成员间 ============
    {"id": "fam-couple", "domain": "家庭", "need": "夫妻需要理解与分担",
     "conflict": "家务/育儿/经济压力分配不均 → 怨气积累",
     "thesis": ["为什么结婚后天天为家务吵架？",
                "为什么总是我付出多对方看不见？"],
     "antithesis": ["是不是我要求太高了？",
                    "离婚是不是比凑合过更好？"],
     "synthesis": ["怎么和伴侣分工不伤感情？",
                   "怎么在婚姻里保持新鲜感？"]},
    {"id": "fam-gener", "domain": "家庭", "need": "年轻人要自主+老人要被尊重",
     "conflict": "代际观念冲突（催婚/生育/养老/消费观）",
     "thesis": ["为什么父母总催婚催生？",
                "为什么老人总觉得我们乱花钱？"],
     "antithesis": ["不听老人的是不是不孝？",
                    "让老人带孩子是不是一定会起冲突？"],
     "synthesis": ["怎么和父母住一起不吵架？",
                   "怎么在孝顺和做自己之间平衡？"]},
    # ============ 教育制度 ============
    {"id": "edu-score", "domain": "教育制度", "need": "全面发展（兴趣/健康/创造力）",
     "conflict": "应试以分数为唯一筛选标准",
     "thesis": ["为什么现在的教育都只看分数？",
                "为什么素质教育喊了这么多年还是应试？"],
     "antithesis": ["没有高考分数，穷人怎么出头？",
                    "分数公平是不是已经是最公平的了？"],
     "synthesis": ["怎么在应试体系里保护好孩子的兴趣？",
                   "教育的本质到底是什么？"]},
    {"id": "edu-resource", "domain": "教育制度", "need": "每个孩子都得到好教育",
     "conflict": "教育资源向城市/名校集中，农村/薄弱校被稀释",
     "thesis": ["为什么城里的学校越来越好，农村的越来越差？",
                "为什么学区房这么贵？"],
     "antithesis": ["教育资源不集中，怎么培养顶尖人才？",
                    "名校靠掐尖，掐走的是不是农村的希望？"],
     "synthesis": ["怎么让教育资源更公平？",
                   "普通家庭的孩子怎么不输在起跑线？"]},
    # ============ 师生关系 ============
    {"id": "teach-authority", "domain": "师生", "need": "学生需要被尊重+老师需要权威",
     "conflict": "老师权威（我说了算）vs 学生质疑（凭什么）",
     "thesis": ["为什么老师不容许学生质疑？",
                "为什么老师总用成绩压人？"],
     "antithesis": ["学生都敢顶嘴，课还怎么上？",
                    "老师是不是也有老师的苦衷？"],
     "synthesis": ["怎么和老师有效沟通不被讨厌？",
                   "老师怎么既权威又让学生敢提问？"]},
    {"id": "teach-fair", "domain": "师生", "need": "每个学生被公平对待",
     "conflict": "老师偏爱成绩好的/听话的学生",
     "thesis": ["为什么老师总是偏心成绩好的？",
                "为什么差生总被放弃？"],
     "antithesis": ["成绩好的学生更努力，偏心是不是有道理？",
                    "老师也是人，能要求完全公平吗？"],
     "synthesis": ["差生怎么让老师刮目相看？",
                   "老师怎么做到不放弃每个学生？"]},
    # ============ 企业与员工 ============
    {"id": "work-pay", "domain": "企业员工", "need": "付出有回报（薪酬/晋升/尊重）",
     "conflict": "企业要利润最大化（压低成本）vs 员工要价值认可",
     "thesis": ["为什么干活最多的人工资不是最高？",
                "为什么涨工资永远轮不到我？"],
     "antithesis": ["老板要控制成本，是不是也合理？",
                    "能力不行还想要高薪，是不是贪心？"],
     "synthesis": ["怎么谈涨薪才不尴尬？",
                   "怎么让老板看到我的价值？"]},
    {"id": "work-loyalty", "domain": "企业员工", "need": "职业发展（成长/稳定）",
     "conflict": "忠诚于公司 vs 跳槽换发展",
     "thesis": ["为什么在公司干十年不如跳槽涨得快？",
                "年轻人为什么总想跳槽？"],
     "antithesis": ["频繁跳槽是不是简历就花了？",
                    "公司培养我，走了是不是忘恩负义？"],
     "synthesis": ["怎么判断该不该跳槽？",
                   "怎么在公司里持续成长不被淘汰？"]},
    # ============ 政府与企业 ============
    {"id": "gov-reg", "domain": "政企", "need": "企业要创新空间（快/灵活）",
     "conflict": "政府要监管（安全/合规/秩序）",
     "thesis": ["为什么监管总是跟不上创新？",
                "为什么一个行业一火就被管？"],
     "antithesis": ["不管的话，平台垄断/数据滥用怎么办？",
                    "创新和安全是不是天然冲突？"],
     "synthesis": ["怎么在监管和创新之间找到平衡？",
                   "为什么中国能同时有强监管和互联网巨头？"]},
    {"id": "gov-subsidy", "domain": "政企", "need": "企业要公平竞争（扶持vs市场）",
     "conflict": "政府补贴扶持有偏（产业政策）vs 市场公平",
     "thesis": ["为什么政府总补贴某些行业？",
                "补贴是不是破坏了公平竞争？"],
     "antithesis": ["没有补贴，新能源/芯片怎么起来？",
                    "发达国家是不是也补贴？"],
     "synthesis": ["怎么判断补贴是雪中送炭还是拔苗助长？",
                   "产业政策和市场竞争怎么配合？"]},
    # ============ 国家之间 ============
    {"id": "intl-tech", "domain": "国家之间", "need": "各国要技术自主（安全/发展）",
     "conflict": "技术领先国封锁 vs 追赶国自主突破",
     "thesis": ["为什么美国要封锁中国芯片？",
                "为什么中国非要自己搞芯片？"],
     "antithesis": ["封锁是不是也倒逼了中国自主创新？",
                    "全球化分工下各自擅长不是更好吗？"],
     "synthesis": ["技术脱钩会走向哪里？",
                   "怎么在封锁下实现技术突围？"]},
    {"id": "intl-trade", "domain": "国家之间", "need": "各国要贸易利益（市场/就业）",
     "conflict": "贸易逆差/产业竞争 → 关税战/贸易摩擦",
     "thesis": ["为什么会有贸易战？",
                "为什么国家之间不能好好做生意？"],
     "antithesis": ["逆差是不是就是吃亏？",
                    "关税是不是最后都转嫁给消费者？"],
     "synthesis": ["贸易摩擦会怎么收场？",
                   "全球化是不是在倒退？"]},
]

# 生成正反合完整链
items = []
for c in CONFLICTS:
    for q in c["thesis"]:
        items.append({"q": q, "conflict_id": c["id"], "domain": c["domain"],
                      "stage": "正题", "need": c["need"], "conflict": c["conflict"]})
    for q in c["antithesis"]:
        items.append({"q": q, "conflict_id": c["id"], "domain": c["domain"],
                      "stage": "反题", "need": c["need"], "conflict": c["conflict"]})
    for q in c["synthesis"]:
        items.append({"q": q, "conflict_id": c["id"], "domain": c["domain"],
                      "stage": "合题", "need": c["need"], "conflict": c["conflict"]})

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v2.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v2", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)

print(f"矛盾清单 v2: {len(CONFLICTS)} 个矛盾（7 域），{len(items)} 道测试题")
by_dom = {}
for c in CONFLICTS:
    by_dom[c["domain"]] = by_dom.get(c["domain"], 0) + 1
for d, n in by_dom.items():
    print(f"  {d}: {n} 矛盾")
