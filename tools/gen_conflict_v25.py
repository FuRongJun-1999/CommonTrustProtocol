# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v25：社会变化激化新矛盾（产后抑郁/男性育婴假/女性职场穿搭/大龄男性婚恋/婚姻沉默成本/生育补贴/女性酒局/女性年龄焦虑）

v1-v24 已覆盖 163 域 205 矛盾 1249 题。v25 聚焦性别与家庭的社会激化新矛盾：
  1. 产后抑郁：产后情绪 vs 家庭支持
  2. 男性育婴假：男性休育儿假 vs 观念/职场
  3. 女性职场穿搭：穿衣自由 vs 职场规范
  4. 大龄男性婚恋：剩男 vs 婚恋市场
  5. 婚姻沉默成本：将就 vs 离婚
  6. 生育补贴：补贴 vs 生育意愿
  7. 女性酒局：酒局 vs 安全/边界
  8. 女性年龄焦虑：怕老 vs 自我接纳
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "gen-postpartum", "domain": "产后心理", "need": "产后被理解",
     "conflict": "产后情绪 vs 家庭支持",
     "linked": ["gen-stayhome", "psy-anxiety"],
     "thesis": ["为什么产后会抑郁？",
                "产后情绪低落是矫情吗？"],
     "antithesis": ["当妈了还矫情？",
                    "产后抑郁需要治疗吗？"],
     "synthesis": ["产后抑郁怎么防？",
                   "家人怎么帮产后妈妈？"]},
    {"id": "gen-paternity", "domain": "育婴假制度", "need": "爸爸也能休假",
     "conflict": "男性休育儿假 vs 观念/职场",
     "linked": ["gen-hiring", "fam-parenting"],
     "thesis": ["为什么男性休育儿假的少？",
                "男人休产假丢人吗？"],
     "antithesis": ["育儿假是女性的专属？",
                    "男性休育儿假，企业会歧视吗？"],
     "synthesis": ["男性育儿假怎么休？",
                   "育儿假制度怎么完善？"]},
    {"id": "gen-dress", "domain": "职场形象", "need": "穿得自在",
     "conflict": "穿衣自由 vs 职场规范",
     "linked": ["gen-work", "public-night"],
     "thesis": ["为什么职场对女性穿着这么多要求？",
                "女性职场穿搭自由吗？"],
     "antithesis": ["职场有规范，穿得体不对吗？",
                    "穿衣自由和责任怎么平衡？"],
     "synthesis": ["女性职场怎么穿得体又自在？",
                   "职场穿搭规范怎么合理？"]},
    {"id": "gen-maleunmarried", "domain": "男性婚恋", "need": "大龄不被嘲笑",
     "conflict": "大龄男性婚恋 vs 婚恋市场",
     "linked": ["gen-genderratio", "fam-gener"],
     "thesis": ["为什么大龄男性更难结婚？",
                "剩男和剩女一样吗？"],
     "antithesis": ["男性晚婚，有压力吗？",
                    "光棍是个人问题吗？"],
     "synthesis": ["大龄男性怎么面对婚恋？",
                   "男性婚恋压力怎么解？"]},
    {"id": "fam-sunkcost", "domain": "婚姻抉择", "need": "婚姻不将就",
     "conflict": "婚姻将就 vs 放手",
     "linked": ["fam-couple", "psy-anxiety"],
     "thesis": ["为什么婚姻里将就的人这么多？",
                "都这么多年了，离了可惜？"],
     "antithesis": ["将就是为孩子好？",
                    "婚姻不好就离，对吗？"],
     "synthesis": ["婚姻将就还是放手？",
                   "婚姻怎么判断该不该继续？"]},
    {"id": "fam-birthsubsidy", "domain": "生育政策", "need": "生得起",
     "conflict": "生育补贴 vs 生育意愿",
     "linked": ["fam-birth", "gov-subsidy"],
     "thesis": ["生育补贴能提高生育率吗？",
                "补贴生娃，是买卖吗？"],
     "antithesis": ["补贴有用，为什么没人多生？",
                    "不补贴，谁愿意生？"],
     "synthesis": ["生育支持怎么做？",
                   "生娃的成本谁来担？"]},
    {"id": "public-toast", "domain": "酒桌安全", "need": "酒局不被灌",
     "conflict": "女性酒局 vs 安全/边界",
     "linked": ["social-toast", "public-night"],
     "thesis": ["为什么女性在酒局更危险？",
                "女性被劝酒，怎么办？"],
     "antithesis": ["酒局不喝酒，行吗？",
                    "女性酒局被灌，怪谁？"],
     "synthesis": ["女性酒局怎么保护自己？",
                   "酒局文化怎么变？"]},
    {"id": "gen-ageanxiety", "domain": "女性心理", "need": "不怕老",
     "conflict": "怕老 vs 自我接纳",
     "linked": ["psy-appearance", "gen-labels"],
     "thesis": ["为什么女性比男性更怕老？",
                "30岁/40岁是女性的坎吗？"],
     "antithesis": ["怕老是不是矫情？",
                    "怕老有错吗？"],
     "synthesis": ["女性怎么面对年龄？",
                   "年龄焦虑怎么破？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v25.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v25", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v25: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
