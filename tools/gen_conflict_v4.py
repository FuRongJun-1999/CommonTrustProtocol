# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v4：新矛盾域扩展（荣方法论）

v1-v3 已覆盖 9 大域 35 矛盾 211 题。v4 扩展新域：
  1. 家庭新形态：重组家庭/单亲/留守
  2. 青少年：网瘾/追星/游戏
  3. 数字生活：直播电商/数据隐私/算法推荐
  4. 社会：老龄化/城乡流动/医患/消费主义/内卷躺平
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "fam-remarry", "domain": "家庭", "need": "重组家庭的成员被接纳",
     "conflict": "继父母/继子女/亲生子女的认同与偏心之争",
     "linked": ["fam-couple", "teach-bully"],
     "thesis": ["重组家庭的孩子为什么难相处？",
                "继父/继母该怎么和继子女建立关系？"],
     "antithesis": ["不是亲生的，能当成亲生的吗？",
                    "重组家庭的孩子是不是更敏感？"],
     "synthesis": ["重组家庭怎么减少冲突？",
                   "怎么让继子女接受新家庭？"]},
    {"id": "fam-leftbehind", "domain": "家庭", "need": "留守儿童的亲情与教育",
     "conflict": "父母外出打工挣钱 vs 孩子缺陪伴缺教育",
     "linked": ["fam-eldercare", "edu-resource"],
     "thesis": ["为什么那么多孩子成了留守儿童？",
                "留守儿童的心理问题怎么来的？"],
     "antithesis": ["不出去打工，家里怎么生活？",
                    "爷爷奶奶带和父母带差别真的那么大吗？"],
     "synthesis": ["外出打工的父母怎么弥补对孩子的亏欠？",
                   "怎么让留守儿童健康成长？"]},
    {"id": "youth-game", "domain": "青少年", "need": "孩子的娱乐与社交",
     "conflict": "游戏/短视频成瘾 vs 学业/健康",
     "linked": ["self-lazy", "edu-score"],
     "thesis": ["为什么孩子一玩游戏就停不下来？",
                "孩子沉迷手机游戏怎么办？"],
     "antithesis": ["游戏是不是就是精神鸦片？",
                    "堵不如疏，是不是该让孩子玩？"],
     "synthesis": ["怎么帮孩子戒掉游戏瘾？",
                   "怎么让孩子分清娱乐和沉迷？"]},
    {"id": "youth-idol", "domain": "青少年", "need": "追星的归属感与自我投射",
     "conflict": "追星投入（时间/金钱/情感）vs 家长认为不务正业",
     "linked": ["fam-gener", "youth-game"],
     "thesis": ["孩子为什么疯狂追星？",
                "追星花的钱是不是太离谱了？"],
     "antithesis": ["追星是不是浪费时间？",
                    "不让孩子追星是不是太专制？"],
     "synthesis": ["怎么看待孩子追星？",
                   "怎么把追星的热情引导到正途？"]},
    {"id": "digit-live", "domain": "数字生活", "need": "商家要销量+消费者要实惠",
     "conflict": "直播电商的冲动消费/套路 vs 真实需求",
     "linked": ["gov-reg", "self-lazy"],
     "thesis": ["为什么看直播总忍不住买东西？",
                "直播带货为什么这么火？"],
     "antithesis": ["直播的东西真的便宜吗？",
                    "不买直播的是不是落伍了？"],
     "synthesis": ["怎么理性消费不被直播套路？",
                   "直播电商会一直火下去吗？"]},
    {"id": "digit-privacy", "domain": "数字生活", "need": "用户要便利+隐私",
     "conflict": "APP收集数据（个性化推荐）vs 隐私泄露风险",
     "linked": ["gov-platform", "intl-tech"],
     "thesis": ["为什么APP什么权限都要？",
                "我的数据到底被谁拿走了？"],
     "antithesis": ["不用数据换便利，能用免费APP吗？",
                    "隐私重要还是方便重要？"],
     "synthesis": ["怎么保护自己的数据隐私？",
                   "数据该归谁？平台还是用户？"]},
    {"id": "soc-aging", "domain": "社会", "need": "老人的晚年保障",
     "conflict": "老龄化加速 vs 养老金/医疗/照护供给不足",
     "linked": ["fam-eldercare", "gov-subsidy"],
     "thesis": ["为什么养老金越来越不够用？",
                "老了以后谁来照顾我们这一代？"],
     "antithesis": ["生孩子的意义是不是就是养老？",
                    "延迟退休是不是坑年轻人？"],
     "synthesis": ["怎么规划自己的养老？",
                   "社会怎么应对老龄化？"]},
    {"id": "soc-urban", "domain": "社会", "need": "流动人口的融入与权益",
     "conflict": "进城务工/落户 vs 户籍/教育/医疗壁垒",
     "linked": ["fam-leftbehind", "work-layoff"],
     "thesis": ["为什么在城市打工多年还是没归属感？",
                "外地孩子上学为什么这么难？"],
     "antithesis": ["城市资源有限，凭什么全开放？",
                    "回老家发展是不是更轻松？"],
     "synthesis": ["城市和乡村怎么选？",
                   "怎么让流动人口真正融入城市？"]},
    {"id": "soc-doctor", "domain": "社会", "need": "患者要治愈+医生要尊重",
     "conflict": "医患信息不对称（期望vs现实）→ 冲突",
     "linked": ["work-burnout", "social-boundary"],
     "thesis": ["为什么医患关系越来越紧张？",
                "为什么看病这么难这么贵？"],
     "antithesis": ["医生忙得连轴转，患者抱怨是不是过分？",
                    "患者花了钱没治好，生气是不是正常？"],
     "synthesis": ["医患之间怎么互相理解？",
                   "怎么让看病不再难？"]},
    {"id": "soc-consumer", "domain": "社会", "need": "物质满足 vs 意义感",
     "conflict": "消费主义（买买买=幸福）vs 空虚/债务",
     "linked": ["self-compare", "self-ideal"],
     "thesis": ["为什么东西越买越多却不快乐？",
                "为什么总想买新东西？"],
     "antithesis": ["赚钱不花难道留着下崽？",
                    "消费是不是拉动经济的手段？"],
     "synthesis": ["怎么摆脱消费主义？",
                   "怎么分清需要和想要？"]},
    {"id": "soc-lieflat", "domain": "社会", "need": "年轻人要意义与公平",
     "conflict": "努力也难翻身（内卷）vs 躺平被批判",
     "linked": ["work-age35", "self-ideal"],
     "thesis": ["为什么越来越多人选择躺平？",
                "内卷到底是怎么来的？"],
     "antithesis": ["躺平是不是不负责任？",
                    "不努力还想有好生活，是不是做梦？"],
     "synthesis": ["躺平还是奋斗，怎么选？",
                   "怎么在卷和躺之间找到自己的位置？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v4.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v4", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v4: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
