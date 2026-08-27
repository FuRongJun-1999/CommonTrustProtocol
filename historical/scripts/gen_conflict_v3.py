# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v3：矛盾域细化 + 矛盾间关联（荣方法论）

v1（6域8矛盾49题）+ v2（7域14矛盾84题）已 100%。
v3 目标：
  1. 矛盾域再细化：家庭→婆媳/养老/单亲；企业→35岁危机/裁员/内卷；
     政企→平台经济/数据跨境/碳中和；国际→汇率/能源/气候；教育→双减/补习；
     师生→校园霸凌；自我→拖延/焦虑/攀比
  2. 矛盾间关联（linked）：显式标注矛盾链——一个矛盾的合题是另一矛盾的正题
     （如 教育压力→亲子冲突→青春期恋爱；职场内卷→婚姻疲劳→离婚）
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    # ============ 家庭·细化 ============
    {"id": "fam-motherinlaw", "domain": "家庭", "need": "妻子需要小家庭自主权",
     "conflict": "婆婆的介入（育儿/家务/生活方式的代际主权之争）",
     "linked": ["fam-couple", "fam-gener"],
     "thesis": ["为什么婆婆总爱插手我们小家庭的事？",
                "婆媳关系为什么这么难处？"],
     "antithesis": ["婆婆帮忙带孩子，是不是就该听她的？",
                    "老公夹在中间，是不是我该让步？"],
     "synthesis": ["怎么和婆婆相处又不丢边界？",
                   "老公怎么当婆媳之间的桥梁？"]},
    {"id": "fam-eldercare", "domain": "家庭", "need": "老人被照顾+年轻人不被拖垮",
     "conflict": "养老责任（时间/金钱/情感）vs 年轻人的工作与生活",
     "linked": ["fam-gener", "work-burnout"],
     "thesis": ["为什么养老压力全压在我一个人身上？",
                "爸妈老了，我和兄弟姐妹谁管？"],
     "antithesis": ["送养老院是不是不孝？",
                    "为了照顾老人放弃工作值得吗？"],
     "synthesis": ["怎么规划养老不让自己崩溃？",
                   "兄弟姐妹怎么分担养老责任？"]},
    # ============ 教育·细化 ============
    {"id": "edu-doublecut", "domain": "教育制度", "need": "孩子轻松+家长放心",
     "conflict": "双减减负 vs 升学竞争不减（剧场效应）",
     "linked": ["edu-score", "edu-resource"],
     "thesis": ["双减之后为什么家长更焦虑了？",
                "不让补课了，孩子落后怎么办？"],
     "antithesis": ["减负是不是让有钱人请私教更不公平？",
                    "不卷了，孩子以后怎么竞争？"],
     "synthesis": ["双减之后家长怎么不焦虑？",
                   "不补课孩子怎么保持竞争力？"]},
    {"id": "edu-tutor", "domain": "教育制度", "need": "孩子成绩提升",
     "conflict": "补习班花钱花时间 vs 效果不确定/孩子抵触",
     "linked": ["edu-score", "edu-doublecut"],
     "thesis": ["为什么报了那么多补习班成绩还是上不去？",
                "孩子抵触补习班怎么办？"],
     "antithesis": ["不补课是不是就落后了？",
                    "补习班是不是在贩卖焦虑？"],
     "synthesis": ["怎么判断孩子需要补什么？",
                   "怎么让孩子主动想学？"]},
    # ============ 师生·细化 ============
    {"id": "teach-bully", "domain": "师生", "need": "每个孩子安全+被尊重",
     "conflict": "校园霸凌 vs 学校息事宁人/受害者不敢说",
     "linked": ["teach-fair", "fam-couple"],
     "thesis": ["为什么被欺负了老师也不管？",
                "孩子在学校被欺负了怎么办？"],
     "antithesis": ["打回去是不是最好的办法？",
                    "告老师没用，是不是只能忍？"],
     "synthesis": ["怎么让孩子敢说被欺负的事？",
                   "学校和家长怎么联手反霸凌？"]},
    # ============ 企业·细化 ============
    {"id": "work-age35", "domain": "企业员工", "need": "中年人的职业安全感",
     "conflict": "35岁危机（被嫌弃年龄/晋升瓶颈/裁员优先）vs 经验价值",
     "linked": ["work-loyalty", "work-burnout"],
     "thesis": ["为什么35岁就被职场嫌弃？",
                "35岁以后还能找到好工作吗？"],
     "antithesis": ["年轻人便宜有干劲，企业选他们是不是合理？",
                    "35岁被裁是不是自己没跟上？"],
     "synthesis": ["怎么提前布局不被35岁淘汰？",
                   "中年转行/创业靠谱吗？"]},
    {"id": "work-layoff", "domain": "企业员工", "need": "稳定就业",
     "conflict": "企业降本（裁员）vs 员工生存（还贷养家）",
     "linked": ["work-age35", "work-pay"],
     "thesis": ["为什么公司一不行就裁员？",
                "被裁员了怎么办？"],
     "antithesis": ["公司都亏钱了，不裁难道等死？",
                    "裁员是不是总裁老实人？"],
     "synthesis": ["被裁之后怎么快速翻身？",
                   "怎么让自己成为裁不掉的人？"]},
    # ============ 政企·细化 ============
    {"id": "gov-platform", "domain": "政企", "need": "平台要发展+从业者要保障",
     "conflict": "平台经济（外卖/网约车/直播）的灵活用工 vs 社保/权益保障",
     "linked": ["gov-reg", "work-pay"],
     "thesis": ["为什么外卖骑手没有社保？",
                "平台到底算不算雇佣关系？"],
     "antithesis": ["灵活就业就该自己担风险吗？",
                    "平台给了机会，凭什么还要求保障？"],
     "synthesis": ["怎么保障骑手又不压垮平台？",
                   "平台用工的制度出路在哪？"]},
    {"id": "gov-carbon", "domain": "政企", "need": "经济发展（企业利润）",
     "conflict": "碳中和/环保要求 vs 高耗能产业的成本与就业",
     "linked": ["gov-subsidy", "intl-energy"],
     "thesis": ["为什么环保要求越来越严，工厂怎么办？",
                "碳中和是不是让企业更难做了？"],
     "antithesis": ["不搞环保，子孙后代怎么办？",
                    "发达国家是不是也这么严？"],
     "synthesis": ["企业怎么转型又不倒闭？",
                   "环保和发展真的不能兼得吗？"]},
    # ============ 国际·细化 ============
    {"id": "intl-energy", "domain": "国家之间", "need": "各国的能源安全",
     "conflict": "能源资源争夺（石油/天然气/稀土）vs 绿色转型",
     "linked": ["intl-tech", "gov-carbon"],
     "thesis": ["为什么石油这么重要，连年打仗都跟它有关？",
                "为什么稀土能卡别人脖子？"],
     "antithesis": ["新能源普及了，石油是不是就没用了？",
                    "资源多的国家是不是就该富裕？"],
     "synthesis": ["能源转型会怎么改变世界格局？",
                   "怎么摆脱对单一能源的依赖？"]},
    {"id": "intl-climate", "domain": "国家之间", "need": "全球共同应对气候",
     "conflict": "减排责任分摊（历史排放vs当前排放/发达vs发展中）",
     "linked": ["gov-carbon", "intl-energy"],
     "thesis": ["为什么减排责任总是谈不拢？",
                "发达国家该不该为历史排放负责？"],
     "antithesis": ["发展中国家也要发展，凭什么限排？",
                    "气候协议是不是发达国家设的局？"],
     "synthesis": ["气候合作还有希望吗？",
                   "怎么让各国都愿意减排？"]},
    # ============ 自我·细化 ============
    {"id": "self-procrast", "domain": "家庭个体", "need": "完成任务",
     "conflict": "拖延（畏难/完美主义/即时满足）vs 截止日期",
     "linked": ["self-lazy", "work-burnout"],
     "thesis": ["为什么越重要的事越拖？",
                "拖延症还有救吗？"],
     "antithesis": ["拖延是不是就是懒？",
                    "deadline才有动力，是不是也正常？"],
     "synthesis": ["怎么根治拖延？",
                   "怎么在压力下也能开始行动？"]},
    {"id": "self-compare", "domain": "家庭个体", "need": "自我价值感",
     "conflict": "攀比（同辈压力/社交媒体）vs 自己的节奏",
     "linked": ["self-ideal", "self-choice"],
     "thesis": ["为什么看到别人过得比我好就焦虑？",
                "同学都买房结婚了，我还在原地怎么办？"],
     "antithesis": ["不比较是不是就不进步了？",
                    "别人确实更优秀，我是不是该承认？"],
     "synthesis": ["怎么停止和别人比较？",
                   "怎么找到自己的节奏？"]},
]

# 正反合生成
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v3.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v3", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)

print(f"矛盾清单 v3: {len(CONFLICTS)} 矛盾，{len(items)} 题")
print("\n矛盾及关联:")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
