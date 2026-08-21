# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v23：社会变化激化新矛盾（婚前同居/男性婚育压力/婚后原生家庭边界/全职爸爸/姐弟恋/丁克/婚前财产协议/独生女养老）

v1-v22 已覆盖 147 域 189 矛盾 1153 题。v23 聚焦婚恋家庭领域的观念激化新矛盾：
  1. 婚前同居：试婚 vs 传统观念
  2. 男性婚育压力：男方买房彩礼 vs 压力分担
  3. 婚后原生家庭边界：婚后与父母边界
  4. 全职爸爸：男性全职带娃 vs 观念
  5. 姐弟恋：年龄差 vs 观念
  6. 丁克：主动不生育 vs 家庭压力
  7. 婚前财产协议：婚前公证 vs 感情
  8. 独生女养老：独生女 vs 养老压力
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "fam-cohabit", "domain": "婚恋观念", "need": "试出合适",
     "conflict": "婚前同居 vs 传统观念",
     "linked": ["fam-date", "fam-gener"],
     "thesis": ["为什么越来越多人婚前同居？",
                "同居是试婚还是风险？"],
     "antithesis": ["同居是婚前必备？",
                    "不同居，怎么知道合不合适？"],
     "synthesis": ["婚前同居怎么决定？",
                   "同居怎么不伤感情？"]},
    {"id": "gen-malepressure", "domain": "婚育压力", "need": "压力分担",
     "conflict": "男方买房彩礼 vs 压力分担",
     "linked": ["fam-betrothal", "gen-income"],
     "thesis": ["为什么男性婚育压力这么大？",
                "男方要买房彩礼，公平吗？"],
     "antithesis": ["男性压力大，是矫情吗？",
                    "婚育是两个人的事，凭什么男方扛？"],
     "synthesis": ["婚育压力怎么分担？",
                   "男性压力怎么缓解？"]},
    {"id": "fam-boundary", "domain": "家庭边界", "need": "小家主权",
     "conflict": "婚后与父母边界 vs 亲情",
     "linked": ["fam-mil3", "fam-couple"],
     "thesis": ["为什么婚后和父母边界这么难？",
                "婚后父母还管你，怎么办？"],
     "antithesis": ["父母关心有错吗？",
                    "划清边界，是不孝吗？"],
     "synthesis": ["婚后和父母怎么处？",
                   "原生家庭和小家怎么平衡？"]},
    {"id": "gen-staydad", "domain": "育儿分工", "need": "分工不看性别",
     "conflict": "男性全职带娃 vs 观念",
     "linked": ["gen-stayhome", "gen-house"],
     "thesis": ["为什么全职爸爸这么少？",
                "男性全职带娃，丢人吗？"],
     "antithesis": ["男人带孩子，像话吗？",
                    "全职爸爸是逃避工作吗？"],
     "synthesis": ["全职爸爸怎么当？",
                   "带娃谁全职怎么定？"]},
    {"id": "fam-agediff", "domain": "婚恋选择", "need": "年龄不是问题",
     "conflict": "姐弟恋 vs 年龄差观念",
     "linked": ["fam-date", "fam-gener"],
     "thesis": ["为什么姐弟恋争议这么大？",
                "年龄差是问题吗？"],
     "antithesis": ["姐弟恋有错吗？",
                    "年龄差大，合适吗？"],
     "synthesis": ["姐弟恋怎么处？",
                   "年龄差怎么看？"]},
    {"id": "fam-dink", "domain": "生育选择", "need": "生育自主",
     "conflict": "丁克 vs 家庭压力",
     "linked": ["fam-birth", "fam-gener"],
     "thesis": ["为什么越来越多人选择丁克？",
                "丁克会后悔吗？"],
     "antithesis": ["不生孩子有错吗？",
                    "丁克老了怎么办？"],
     "synthesis": ["丁克怎么面对压力？",
                   "生育怎么决定？"]},
    {"id": "fam-prenup", "domain": "婚姻财产", "need": "财产与感情兼得",
     "conflict": "婚前财产协议 vs 感情",
     "linked": ["fam-aa", "fam-betrothal"],
     "thesis": ["为什么婚前财产公证越来越多？",
                "婚前公证伤感情吗？"],
     "antithesis": ["公证是保护自己，有错吗？",
                    "还没结婚就防着，怎么过？"],
     "synthesis": ["婚前财产怎么安排？",
                   "公证和感情怎么平衡？"]},
    {"id": "fam-onlychild", "domain": "养老责任", "need": "独生女不独扛",
     "conflict": "独生女 vs 养老压力",
     "linked": ["fam-eldercare", "fam-birth"],
     "thesis": ["为什么独生女养老压力这么大？",
                "独生女嫁人，父母谁管？"],
     "antithesis": ["女儿养老有错吗？",
                    "独生女压力大，是矫情吗？"],
     "synthesis": ["独生女怎么平衡养老？",
                   "女儿养老怎么支持？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v23.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v23", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v23: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
