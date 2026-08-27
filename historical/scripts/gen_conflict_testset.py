# -*- coding: utf-8 -*-
"""矛盾驱动补盲 · 矛盾清单 v1（荣方法论 · 2026-08-21）

核心：对话盲区从生活实际矛盾出发。矛盾 = 人的需要 × 现实约束的张力，
对话随矛盾发展而变化（矛盾论 · 反者道之动 · 负反馈）。

每个矛盾结构：
  domain  矛盾域（教育/家庭/职场/亲密关系…）
  need    人的需要（对话的驱动力）
  conflict 需要与现实之间的张力（矛盾本身）
  thesis  正题：初始困惑/典型提问（矛盾显现）
  antithesis 反题：对立面/质疑/反弹（矛盾发展，反者道之动）
  synthesis 合题：理解/行动/超越（负反馈收敛或新矛盾起点）

用途：成组生成测试对话（正→反→合完整链），系统性补盲——
一组矛盾一次补全，而非单题孤立补卡。
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    # ============ 教育系统矛盾（测试中已见雏形） ============
    {
        "id": "edu-strict",
        "domain": "教育",
        "need": "学生需要自由成长与娱乐空间",
        "conflict": "应试制度需要高投入学习，挤压自由时间",
        "thesis": ["为什么老师管的这么严？学生一点娱乐时间都没有。",
                   "为什么作业这么多？晚上十点都写不完。"],
        "antithesis": ["如果老师不管，学生能自觉学习吗？",
                       "国外学生玩得多，是不是学得差？",
                       "管这么严有用吗？为什么还是学不好？"],
        "synthesis": ["怎么在严格和学习兴趣之间平衡？",
                      "怎样才能让学习既有效又不痛苦？"],
    },
    {
        "id": "edu-romance",
        "domain": "教育",
        "need": "青春期学生需要亲密感与归属",
        "conflict": "学业要求压抑情感需求，恋爱被视为分心",
        "thesis": ["为什么班里的学生总是在谈恋爱？为什么不把心思用在学习上？",
                   "学生早恋正常吗？"],
        "antithesis": ["恋爱真的影响学习吗？有没有正面例子？",
                       "禁止早恋会不会适得其反？"],
        "synthesis": ["怎么引导青春期恋爱而不压制？",
                      "恋爱和学习可以兼顾吗？"],
    },
    {
        "id": "edu-teaching",
        "domain": "教育",
        "need": "学生需要听得懂、学得会、有成就感",
        "conflict": "灌输式教学违背认知机制，讲了不会",
        "thesis": ["老师讲课为什么总是很无聊？为什么不能做的像故事书一样有趣？",
                   "为什么学生总是学不会？讲过多次还是会犯错。"],
        "antithesis": ["有趣的教学会不会降低知识密度？",
                       "考试要考，怎么可能都讲成故事？"],
        "synthesis": ["怎么把枯燥的知识讲得有趣又不失严谨？",
                      "怎么让学生真正掌握而不是背过？"],
    },
    # ============ 家庭关系矛盾 ============
    {
        "id": "family-expect",
        "domain": "家庭",
        "need": "孩子需要被理解与自主",
        "conflict": "父母期望（成绩/前途）与孩子自主选择的冲突",
        "thesis": ["爸妈总让我考公务员，我不想怎么办？",
                   "父母为什么总拿我和别人家孩子比？"],
        "antithesis": ["父母管我是为我好，我是不是不该顶嘴？",
                       "不听父母的，以后后悔了怎么办？"],
        "synthesis": ["怎么和父母沟通我的选择？",
                      "父母反对我的梦想，怎么坚持又不伤感情？"],
    },
    # ============ 职场矛盾 ============
    {
        "id": "work-burnout",
        "domain": "职场",
        "need": "工作意义感与生活平衡",
        "conflict": "加班文化/绩效压力 vs 个人生活与健康",
        "thesis": ["为什么工作永远做不完？下班了还觉得心累。",
                   "996 真的有必要吗？"],
        "antithesis": ["不拼命工作，会不会被淘汰？",
                       "别人都在加班，我不加是不是不合群？"],
        "synthesis": ["怎么在工作和生活之间划清边界？",
                      "怎么判断该坚持还是该换工作？"],
    },
    # ============ 亲密关系矛盾 ============
    {
        "id": "relation-attach",
        "domain": "亲密关系",
        "need": "安全感的依恋与自由独立",
        "conflict": "依恋需要（怕失去）vs 独立需要（怕被束缚）",
        "thesis": ["为什么恋爱中总是患得患失？",
                   "对象不回消息，是我想太多了吗？"],
        "antithesis": ["是不是我太黏人了，才会这样？",
                       "不查手机不报备，是不是不重视我？"],
        "synthesis": ["怎么建立安全的依恋而不焦虑？",
                      "感情里怎么平衡亲密和独立？"],
    },
    # ============ 自我发展矛盾 ============
    {
        "id": "self-choice",
        "domain": "自我发展",
        "need": "做想做的事 vs 稳妥的路径",
        "conflict": "理想追求与安全感的拉扯",
        "thesis": ["该选喜欢但不确定的路，还是稳定但无趣的路？",
                   "为什么我总在纠结选择？"],
        "antithesis": ["坚持理想失败了怎么办？",
                       "选择稳定是不是就放弃自己了？"],
        "synthesis": ["怎么在不确定里做选择？",
                      "怎么接受选择带来的代价？"],
    },
    # ============ 人际边界矛盾 ============
    {
        "id": "social-boundary",
        "domain": "人际",
        "need": "被喜欢（合群）与做自己（边界）",
        "conflict": "讨好他人 vs 维护自我边界",
        "thesis": ["为什么我总是不会拒绝别人？",
                   "怕得罪人，什么忙都答应，好累。"],
        "antithesis": ["拒绝了朋友，会不会显得冷漠？",
                       "不讨好别人，是不是就没有朋友了？"],
        "synthesis": ["怎么温和地拒绝而不伤关系？",
                      "怎么分辨该帮和不该帮？"],
    },
]

# 生成测试集：正反合完整链
items = []
for c in CONFLICTS:
    for q in c["thesis"]:
        items.append({"q": q, "conflict_id": c["id"], "domain": c["domain"],
                      "stage": "正题", "need": c["need"]})
    for q in c["antithesis"]:
        items.append({"q": q, "conflict_id": c["id"], "domain": c["domain"],
                      "stage": "反题", "need": c["need"]})
    for q in c["synthesis"]:
        items.append({"q": q, "conflict_id": c["id"], "domain": c["domain"],
                      "stage": "合题", "need": c["need"]})

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v1.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v1", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)

print(f"矛盾清单 v1: {len(CONFLICTS)} 个矛盾域，{len(items)} 道测试题")
print("\n各矛盾:")
for c in CONFLICTS:
    n = len(c["thesis"]) + len(c["antithesis"]) + len(c["synthesis"])
    print(f"  [{c['id']}] {c['domain']}: {c['need'][:18]}…（{n} 题：正{len(c['thesis'])}反{len(c['antithesis'])}合{len(c['synthesis'])}）")
