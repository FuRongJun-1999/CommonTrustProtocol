# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v5：新矛盾域扩展（AI伦理/新兴职业/人口/健康/教育新形态/职场新形态）

v1-v4 已覆盖 13 域 46 矛盾 277 题。v5 聚焦时代新矛盾：
  1. AI 伦理：AI替代工作/AI创作版权/算法偏见
  2. 新兴职业：自由职业/裸辞/数字游民
  3. 人口结构：生育成本/少子化
  4. 健康作息：熬夜/外卖/亚健康
  5. 教育新形态：网课/鸡娃
  6. 职场新形态：远程办公/整顿职场
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "ai-job", "domain": "AI伦理", "need": "工作被替代者的生计",
     "conflict": "AI提效（企业降本）vs 岗位消失（个人失业）",
     "linked": ["work-layoff", "work-age35"],
     "thesis": ["AI会取代哪些人的工作？",
                "我的工作会被AI替代吗？"],
     "antithesis": ["AI替代的是重复劳动，人去做创造，是不是更好？",
                    "淘汰落后岗位是不是进步的必然？"],
     "synthesis": ["怎么应对AI抢饭碗？",
                   "AI时代人还有什么不可替代？"]},
    {"id": "ai-copyright", "domain": "AI伦理", "need": "创作者的劳动被尊重",
     "conflict": "AI用人类作品训练 vs 创作者版权与收益",
     "linked": ["digit-privacy", "gov-reg"],
     "thesis": ["AI用我的画训练，算不算偷？",
                "AI生成的作品版权归谁？"],
     "antithesis": ["AI学习人类作品像人学习一样，算侵权吗？",
                    "AI生成的内容不比人差，凭什么不让用？"],
     "synthesis": ["创作者怎么在AI时代保护自己？",
                   "AI创作和人类创作怎么共处？"]},
    {"id": "ai-bias", "domain": "AI伦理", "need": "被算法公平对待",
     "conflict": "算法推荐/评分有偏见 vs 用户被不公对待",
     "linked": ["digit-privacy", "teach-fair"],
     "thesis": ["为什么算法推荐越刷越同质？",
                "AI评分会不会冤枉人？"],
     "antithesis": ["算法比人更客观，是不是不用怀疑？",
                    "大数据杀熟是不是算法故意的？"],
     "synthesis": ["怎么减少算法偏见？",
                   "被算法不公对待了怎么办？"]},
    {"id": "work-free", "domain": "新兴职业", "need": "自由与稳定",
     "conflict": "自由职业/裸辞的自由 vs 收入不稳/社保断缴",
     "linked": ["self-choice", "work-layoff"],
     "thesis": ["为什么越来越多人想裸辞？",
                "自由职业真的自由吗？"],
     "antithesis": ["没有稳定工作，老了怎么办？",
                    "自由职业是不是逃避职场？"],
     "synthesis": ["怎么判断自己适不适合自由职业？",
                   "自由职业怎么保证稳定收入？"]},
    {"id": "work-remote", "domain": "职场新形态", "need": "员工要灵活+企业要协作",
     "conflict": "远程/居家办公的便利 vs 沟通成本/监督难题",
     "linked": ["work-burnout", "work-loyalty"],
     "thesis": ["远程办公为什么又爱又恨？",
                "居家办公效率真的更高吗？"],
     "antithesis": ["老板看不见人，是不是不放心？",
                    "远程办公是不是迟早回办公室？"],
     "synthesis": ["怎么让远程办公高效又不失控？",
                   "远程和坐班怎么选？"]},
    {"id": "fam-birth", "domain": "人口结构", "need": "年轻人生育的意愿",
     "conflict": "生育成本（时间/金钱/职业）vs 家庭延续的期待",
     "linked": ["fam-eldercare", "fam-gener"],
     "thesis": ["为什么年轻人越来越不想生孩子？",
                "养一个孩子要花多少钱？"],
     "antithesis": ["不生孩子老了谁管你？",
                    "生孩子是不是被社会绑架了？"],
     "synthesis": ["怎么降低生育的代价？",
                   "生不生到底该听谁的？"]},
    {"id": "health-night", "domain": "健康作息", "need": "熬夜的自由",
     "conflict": "熬夜（工作/刷手机/夜生活）vs 健康",
     "linked": ["self-lazy", "work-burnout"],
     "thesis": ["为什么明知道熬夜伤身还是戒不掉？",
                "几点睡才算熬夜？"],
     "antithesis": ["白天那么忙，只有晚上是自己的，熬一下怎么了？",
                    "晚睡晚起是不是也算规律作息？"],
     "synthesis": ["怎么戒掉熬夜？",
                   "怎么在忙碌里保证睡眠？"]},
    {"id": "health-takeout", "domain": "健康作息", "need": "方便的饮食",
     "conflict": "外卖/快餐的便利 vs 健康/花费",
     "linked": ["digit-live", "work-burnout"],
     "thesis": ["为什么天天吃外卖还是戒不掉？",
                "外卖是不是真的不健康？"],
     "antithesis": ["不点外卖，加班吃什么？",
                    "外卖也可以点健康的，是不是矫情？"],
     "synthesis": ["怎么吃得健康又不费时间？",
                   "外卖族怎么自救？"]},
    {"id": "edu-online", "domain": "教育新形态", "need": "网课的便利",
     "conflict": "网课的灵活 vs 效果差（分心/缺监督）",
     "linked": ["edu-tutor", "youth-game"],
     "thesis": ["为什么网课效果总是不如线下？",
                "孩子上网课总走神怎么办？"],
     "antithesis": ["网课便宜又方便，不是更好吗？",
                    "网课不行是孩子自律问题，不是网课问题？"],
     "synthesis": ["怎么让网课有效果？",
                   "线上和线下教育怎么结合？"]},
    {"id": "edu-chicken", "domain": "教育新形态", "need": "孩子的竞争力",
     "conflict": "鸡娃（疯狂报班）vs 孩子童年/健康",
     "linked": ["edu-doublecut", "youth-game"],
     "thesis": ["为什么家长都拼命鸡娃？",
                "鸡娃到底有没有用？"],
     "antithesis": ["不鸡娃，孩子落后谁负责？",
                    "鸡娃鸡出心理问题，值吗？"],
     "synthesis": ["鸡娃和快乐教育怎么平衡？",
                   "怎么判断鸡娃的度？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v5.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v5", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v5: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
