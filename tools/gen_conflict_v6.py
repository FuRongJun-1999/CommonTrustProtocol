# -*- coding: utf-8 -*-
"""矛盾驱动盲区探索 v6：新矛盾域（法律/公共健康/文化心理/教育国际/科技伦理/自然灾害）

v1-v5 已覆盖 19 域 56 矛盾 337 题。v6 新域：
  1. 法律权益：维权成本/法律援助/判决公平
  2. 公共健康：疫苗犹豫/疫情措施/医美
  3. 文化心理：容貌焦虑/孤独/空巢青年
  4. 教育国际：留学/教育内卷国际化
  5. 科技伦理：人脸识别/监控/深度伪造
  6. 自然灾害：防灾vs发展/应急
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

CONFLICTS = [
    {"id": "law-rights", "domain": "法律权益", "need": "普通人的权益被保护",
     "conflict": "维权成本高（时间长/律师贵/举证难）vs 权益受损",
     "linked": ["soc-doctor", "gov-reg"],
     "thesis": ["为什么维权这么难这么贵？",
                "被坑了打官司值得吗？"],
     "antithesis": ["打官司费时费力，忍一忍是不是更划算？",
                    "法律是给有钱人准备的，普通人怎么办？"],
     "synthesis": ["普通人怎么低成本维权？",
                   "怎么判断值不值得打官司？"]},
    {"id": "health-vaccine", "domain": "公共健康", "need": "个人健康自主",
     "conflict": "疫苗/防疫措施的公共健康收益 vs 个人自由与担忧",
     "linked": ["health-takeout", "gov-reg"],
     "thesis": ["为什么有人不愿打疫苗？",
                "强制防疫是不是侵犯自由？"],
     "antithesis": ["不打疫苗的自由，会不会害了别人？",
                    "疫苗副作用是不是被隐瞒了？"],
     "synthesis": ["怎么看待疫苗犹豫？",
                   "公共健康和个人自由怎么平衡？"]},
    {"id": "psy-appearance", "domain": "文化心理", "need": "被接纳的自我形象",
     "conflict": "容貌焦虑（滤镜/审美标准）vs 接纳真实的自己",
     "linked": ["self-compare", "soc-consumer"],
     "thesis": ["为什么越来越多人容貌焦虑？",
                "不漂亮是不是就没人喜欢？"],
     "antithesis": ["变美有什么错，精致有错吗？",
                    "容貌焦虑是不是矫情？"],
     "synthesis": ["怎么摆脱容貌焦虑？",
                   "怎么看待医美/整容？"]},
    {"id": "psy-lonely", "domain": "文化心理", "need": "孤独青年的连接",
     "conflict": "城市化的原子化（空巢青年/社恐）vs 归属需要",
     "linked": ["soc-urban", "relation-attach"],
     "thesis": ["为什么越长大越孤独？",
                "空巢青年的孤独怎么来的？"],
     "antithesis": ["一个人也挺好，是不是不用刻意社交？",
                    "孤独是常态，习惯就好？"],
     "synthesis": ["怎么和孤独相处？",
                   "怎么建立真心的朋友关系？"]},
    {"id": "edu-abroad", "domain": "教育国际", "need": "更好教育的选择",
     "conflict": "留学的高成本/风险 vs 视野/学历回报",
     "linked": ["edu-score", "intl-tech"],
     "thesis": ["为什么越来越多家庭送孩子留学？",
                "留学到底值不值？"],
     "antithesis": ["国外教育一定更好吗？",
                    "留学回来找不到工作，是不是白花钱？"],
     "synthesis": ["怎么判断该不该留学？",
                   "留学的真正价值是什么？"]},
    {"id": "tech-face", "domain": "科技伦理", "need": "便利+安全",
     "conflict": "人脸识别/监控的便利 vs 隐私/滥用",
     "linked": ["digit-privacy", "ai-bias"],
     "thesis": ["为什么到处都装人脸识别？",
                "刷脸真的安全吗？"],
     "antithesis": ["没有监控，坏人怎么抓？",
                    "我又没干坏事，怕什么监控？"],
     "synthesis": ["怎么看待无处不在的监控？",
                   "技术和隐私怎么平衡？"]},
    {"id": "tech-deepfake", "domain": "科技伦理", "need": "信息真实",
     "conflict": "深度伪造（AI换脸/假视频）的传播 vs 真相/名誉",
     "linked": ["ai-copyright", "digit-privacy"],
     "thesis": ["AI换脸视频为什么这么危险？",
                "怎么识别视频是不是假的？"],
     "antithesis": ["换脸只是娱乐，是不是大惊小怪？",
                    "技术无罪，用的人才有罪？"],
     "synthesis": ["怎么防范深度伪造伤害？",
                   "平台和立法该怎么管AI伪造？"]},
    {"id": "disaster-dev", "domain": "自然灾害", "need": "安全的生活",
     "conflict": "防灾投入（钱/地/时间）vs 经济发展",
     "linked": ["gov-carbon", "fam-eldercare"],
     "thesis": ["为什么明知道有风险还在河边/地震带建房？",
                "防灾投入为什么总是不够？"],
     "antithesis": ["把资源都拿去防灾，发展怎么办？",
                    "天灾躲不过，防了也白防？"],
     "synthesis": ["怎么在发展和防灾之间平衡？",
                   "普通家庭怎么做好应急准备？"]},
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

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v6.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v6", "conflicts": len(CONFLICTS),
               "items": items}, f, ensure_ascii=False, indent=1)
print(f"矛盾清单 v6: {len(CONFLICTS)} 矛盾，{len(items)} 题")
for c in CONFLICTS:
    print(f"  [{c['id']}] {c['domain']}: 关联 -> {c.get('linked', [])}")
