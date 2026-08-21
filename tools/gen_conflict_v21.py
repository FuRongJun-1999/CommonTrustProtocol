# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v21：新矛盾域（儿童防溺水/代际财产/宠物美容/家庭监控/晒娃/毕业旅行/家装装修/跟团旅游）

v1-v20 已覆盖 131 域 173 矛盾 1057 题。v21 新域（生活矛盾再细化，收尾代）：
  1. 儿童防溺水：游泳安全 vs 家长看护
  2. 代际财产：老人财产分配 vs 子女期待
  3. 宠物美容：宠物美容贵 vs 必要
  4. 家庭监控：装监控 vs 隐私
  5. 晒娃：分享快乐 vs 隐私风险
  6. 毕业旅行：仪式 vs 烧钱
  7. 家装装修：装修 vs 踩坑
  8. 跟团旅游：跟团 vs 自由行
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "health-drowning", "domain": "儿童安全", "need": "水边安全",
     "conflict": "溺水风险 vs 家长看护",
     "linked": ["health-medicine", "edu-punish"],
     "thesis": ["为什么儿童溺水这么多？",
                "孩子学游泳有用吗？"],
     "antithesis": ["溺水是意外，防得住吗？",
                    "让孩子玩水，有错吗？"],
     "synthesis": ["儿童防溺水怎么做？",
                   "孩子游泳怎么保证安全？"]},
    {"id": "fam-property", "domain": "家庭财产", "need": "分产不伤情",
     "conflict": "老人财产分配 vs 子女期待",
     "linked": ["fam-elderlove", "fam-gener"],
     "thesis": ["为什么老人财产分配总闹矛盾？",
                "老人的钱该给谁？"],
     "antithesis": ["子女争财产，是贪心吗？",
                    "老人自己花，不行吗？"],
     "synthesis": ["老人财产怎么分不伤感情？",
                   "子女怎么面对老人财产？"]},
    {"id": "pet-grooming", "domain": "养宠消费", "need": "宠物整洁",
     "conflict": "宠物美容贵 vs 必要",
     "linked": ["pet-boarding", "city-pet"],
     "thesis": ["为什么宠物美容这么贵？",
                "宠物美容有必要吗？"],
     "antithesis": ["给宠物美容，是矫情吗？",
                    "宠物美容是生意，赚钱有错吗？"],
     "synthesis": ["宠物美容怎么选？",
                   "宠物美容的钱怎么花？"]},
    {"id": "digit-camera", "domain": "家庭科技", "need": "安全与信任",
     "conflict": "装监控 vs 隐私",
     "linked": ["digit-privacy", "fam-housekeeper"],
     "thesis": ["为什么家里要装监控？",
                "装监控是对家人不信任吗？"],
     "antithesis": ["监控能防意外，有错吗？",
                    "保姆在监控下工作，公平吗？"],
     "synthesis": ["家庭监控怎么装不伤感情？",
                   "监控和隐私怎么平衡？"]},
    {"id": "digit-baby", "domain": "数字育儿", "need": "分享与保护",
     "conflict": "晒娃 vs 隐私风险",
     "linked": ["digit-privacy", "soc-consumer"],
     "thesis": ["为什么家长爱晒娃？",
                "晒娃有什么风险？"],
     "antithesis": ["晒娃是分享快乐，有错吗？",
                    "别人爱看不看，管得着吗？"],
     "synthesis": ["晒娃怎么晒不危险？",
                   "孩子的照片怎么保护？"]},
    {"id": "edu-trip", "domain": "青春仪式", "need": "旅行的意义",
     "conflict": "毕业旅行 vs 钱/仪式",
     "linked": ["edu-parttime", "tourism-trap"],
     "thesis": ["为什么毕业都要旅行？",
                "毕业旅行是仪式还是烧钱？"],
     "antithesis": ["辛苦几年，犒劳自己错了吗？",
                    "没钱就不去，不行吗？"],
     "synthesis": ["毕业旅行怎么规划？",
                   "旅行和钱怎么平衡？"]},
    {"id": "housing-renovation", "domain": "居住消费", "need": "装修不踩坑",
     "conflict": "装修 vs 踩坑/费用",
     "linked": ["housing", "gov-reg"],
     "thesis": ["为什么装修这么贵？",
                "装修为什么总踩坑？"],
     "antithesis": ["装修是手艺活，贵有贵的道理？",
                    "装修被坑，怪自己不懂行？"],
     "synthesis": ["装修怎么不踩坑？",
                   "装修预算怎么控制？"]},
    {"id": "tourism-group", "domain": "旅行方式", "need": "玩得明白",
     "conflict": "跟团 vs 自由行",
     "linked": ["tourism-trap", "digit-live"],
     "thesis": ["为什么跟团游总被吐槽？",
                "跟团游和自由行怎么选？"],
     "antithesis": ["跟团省心，有错吗？",
                    "低价团购物，是行业规则？"],
     "synthesis": ["跟团游怎么避坑？",
                   "旅游方式怎么选？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v21.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v21", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v21: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
