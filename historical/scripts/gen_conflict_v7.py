# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v7：新矛盾域（军事/宗教/太空/气候经济/元宇宙/前沿科技）

v1-v6 已覆盖 25 域 64 矛盾 385 题。v7 新域：
  1. 军事安全：军备竞赛/代理人战争/国防开支
  2. 宗教文化：传统 vs 现代/宗教自由
  3. 太空探索：太空竞赛/资源分配
  4. 气候经济：碳税/绿色产业/转型阵痛
  5. 元宇宙数字身份：虚拟 vs 现实
  6. 前沿科技：基因编辑/脑机接口/量子计算
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "mil-race", "domain": "军事安全", "need": "国家安全（威慑）",
     "conflict": "军备竞赛（你增我也增）vs 资源浪费/紧张升级",
     "linked": ["intl-tech", "intl-energy"],
     "thesis": ["为什么国家之间要搞军备竞赛？",
                "军费花这么多值吗？"],
     "antithesis": ["我不扩军，别人扩了怎么办？",
                    "和平是打出来的还是谈出来的？"],
     "synthesis": ["军备竞赛怎么停下来？",
                   "军费和民生怎么平衡？"]},
    {"id": "mil-proxy", "domain": "军事安全", "need": "大国博弈的克制",
     "conflict": "大国不直接开战 vs 代理人战争（别国成战场）",
     "linked": ["mil-race", "intl-trade"],
     "thesis": ["为什么大国打仗要借别人的手？",
                "代理人战争苦了谁？"],
     "antithesis": ["不下场是不是就能避免大战？",
                    "小国是不是只能选边站？"],
     "synthesis": ["怎么避免代理人战争？",
                   "小国怎么在大国博弈中自保？"]},
    {"id": "relig-trad", "domain": "宗教文化", "need": "传统的延续",
     "conflict": "传统习俗/宗教规范 vs 现代价值观（平等/自由）",
     "linked": ["fam-gener", "intl-climate"],
     "thesis": ["为什么有些传统和现代生活冲突？",
                "传统习俗该不该保留？"],
     "antithesis": ["老祖宗的东西不能丢，是不是？",
                    "传统都是糟粕，该全丢？"],
     "synthesis": ["怎么区分精华和糟粕？",
                   "传统和现代怎么共存？"]},
    {"id": "space-race", "domain": "太空探索", "need": "太空资源与安全",
     "conflict": "太空竞赛/资源争夺 vs 和平开发合作",
     "linked": ["intl-tech", "mil-race"],
     "thesis": ["为什么各国都在抢着登月探火？",
                "太空探索花那么多钱值吗？"],
     "antithesis": ["地球上问题都没解决，搞太空干嘛？",
                    "太空资源是不是新的殖民地争夺？"],
     "synthesis": ["太空开发该怎么合作？",
                   "太空探索对人类的意义是什么？"]},
    {"id": "carbon-tax", "domain": "气候经济", "need": "减排 vs 成本",
     "conflict": "碳税/碳交易的成本 vs 企业利润/居民负担",
     "linked": ["gov-carbon", "intl-climate"],
     "thesis": ["为什么要收碳税？",
                "碳交易是不是变相收钱？"],
     "antithesis": ["收碳税是不是给企业加负担？",
                    "发达国家收的碳税是不是更多？"],
     "synthesis": ["碳税怎么收才公平？",
                   "个人怎么为碳中和出力？"]},
    {"id": "meta-identity", "domain": "元宇宙", "need": "虚拟体验",
     "conflict": "虚拟世界的沉浸 vs 现实生活的疏离",
     "linked": ["digit-live", "psy-lonely"],
     "thesis": ["元宇宙会不会让人更孤独？",
                "虚拟身份和现实身份哪个是真的？"],
     "antithesis": ["虚拟世界也是一种生活，不行吗？",
                    "元宇宙是不是资本炒作的泡沫？"],
     "synthesis": ["怎么健康地使用虚拟世界？",
                   "虚拟和现实怎么平衡？"]},
    {"id": "gene-edit", "domain": "前沿科技", "need": "治疗疾病的希望",
     "conflict": "基因编辑（治病的可能）vs 伦理（设计婴儿/脱靶）",
     "linked": ["tech-deepfake", "gov-reg"],
     "thesis": ["基因编辑治病变态还是危险？",
                "为什么基因编辑婴儿被禁止？"],
     "antithesis": ["能治绝症，为什么不放开？",
                    "人能不能设计自己的后代？"],
     "synthesis": ["基因编辑该怎么管？",
                   "医疗用途和优生学怎么划界？"]},
    {"id": "brain-computer", "domain": "前沿科技", "need": "脑机接口的突破",
     "conflict": "脑机接口（瘫痪者希望）vs 大脑安全/隐私/意识",
     "linked": ["digit-privacy", "tech-face"],
     "thesis": ["脑机接口是福音还是风险？",
                "把芯片装进大脑安全吗？"],
     "antithesis": ["能治瘫痪，为什么不全力推进？",
                    "思想被读取了怎么办？"],
     "synthesis": ["脑机接口该怎么发展？",
                   "意识和技术的关系是什么？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v7.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v7", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v7: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
