# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v14：新矛盾域（婚庆消费/二手交易/应急演练/家政服务/理财推销/小区物业/公共场所吸烟/网络交友）

v1-v13 已覆盖 75 域 117 矛盾 721 题。v14 新域（生活矛盾再细化）：
  1. 婚庆消费：结婚花钱 vs 简办
  2. 二手交易：二手买卖 vs 假货/纠纷
  3. 应急演练：演练形式化 vs 真有用
  4. 家政服务：请保姆 vs 信任/隐私
  5. 理财推销：银行理财 vs 亏损风险
  6. 小区物业：物业费 vs 服务质量
  7. 公共场所吸烟：吸烟自由 vs 他人健康
  8. 网络交友：网恋 vs 杀猪盘
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "fam-wedding", "domain": "婚嫁消费", "need": "婚礼的意义",
     "conflict": "结婚花钱 vs 简办/面子",
     "linked": ["fam-betrothal", "soc-consumer"],
     "thesis": ["为什么结婚这么贵？",
                "婚礼是给谁办的？"],
     "antithesis": ["一辈子一次，花钱有错吗？",
                    "简办婚礼丢人吗？"],
     "synthesis": ["婚礼怎么办省钱又不留遗憾？",
                   "结婚的钱怎么花才值？"]},
    {"id": "soc-secondhand", "domain": "循环消费", "need": "闲置变价值",
     "conflict": "二手买卖 vs 假货/纠纷",
     "linked": ["digit-live", "gov-reg"],
     "thesis": ["为什么二手平台这么火？",
                "闲鱼上买东西靠谱吗？"],
     "antithesis": ["卖二手回血有错吗？",
                    "买二手是抠门吗？"],
     "synthesis": ["二手买卖怎么避坑？",
                   "闲置怎么处理最划算？"]},
    {"id": "disaster-drill", "domain": "安全应急", "need": "关键时刻能保命",
     "conflict": "演练形式化 vs 真有用",
     "linked": ["disaster-dev", "edu-score"],
     "thesis": ["为什么演练总是走过场？",
                "地震来了真的会跑吗？"],
     "antithesis": ["演练耽误时间，有必要吗？",
                    "真出事靠演练有用吗？"],
     "synthesis": ["应急演练怎么才不白练？",
                   "家庭应急准备怎么做？"]},
    {"id": "fam-housekeeper", "domain": "家庭服务", "need": "家务有人管",
     "conflict": "请保姆 vs 信任/隐私",
     "linked": ["gen-house", "fam-couple"],
     "thesis": ["为什么好保姆这么难找？",
                "请保姆不放心怎么办？"],
     "antithesis": ["家务外包，是不是太矫情？",
                    "保姆也是人，将就一下不行吗？"],
     "synthesis": ["怎么找到靠谱的家政？",
                   "和保姆怎么相处？"]},
    {"id": "fin-wealth", "domain": "家庭理财", "need": "钱能生钱",
     "conflict": "理财收益 vs 亏损风险",
     "linked": ["fin-loan", "digit-scam"],
     "thesis": ["为什么银行也卖理财产品？",
                "理财为什么会亏钱？"],
     "antithesis": ["利息太低，不理财行吗？",
                    "亏了是银行的责任吗？"],
     "synthesis": ["普通人怎么理财不踩坑？",
                   "存款和理财怎么配？"]},
    {"id": "city-property", "domain": "社区治理", "need": "住得舒心",
     "conflict": "物业费 vs 服务质量",
     "linked": ["city-elevator", "gov-reg"],
     "thesis": ["为什么物业费年年涨？",
                "物业到底管了什么？"],
     "antithesis": ["不交物业费，物业就不管了？",
                    "物业不是服务者吗？"],
     "synthesis": ["怎么让物业好好干活？",
                   "物业纠纷怎么解决？"]},
    {"id": "health-smoke", "domain": "公共健康", "need": "呼吸干净空气",
     "conflict": "吸烟自由 vs 他人健康",
     "linked": ["public-civility", "medical-cost"],
     "thesis": ["为什么公共场合总有人抽烟？",
                "二手烟危害有多大？"],
     "antithesis": ["抽烟是我的自由，管得着吗？",
                    "控烟太严，烟民没人权吗？"],
     "synthesis": ["怎么让烟民不打扰别人？",
                   "公共场所抽烟怎么管？"]},
    {"id": "digit-dating", "domain": "数字婚恋", "need": "网恋的安全",
     "conflict": "网恋缘分 vs 杀猪盘",
     "linked": ["digit-scam", "relation-attach"],
     "thesis": ["为什么网恋容易翻车？",
                "网上的对象靠谱吗？"],
     "antithesis": ["网上认识也是缘分，有错吗？",
                    "网恋奔现丢人吗？"],
     "synthesis": ["网恋怎么不踩坑？",
                   "网上交友怎么保护自己？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v14.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v14", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v14: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
