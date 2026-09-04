# -*- coding: utf-8 -*-
"""seed_common_56_cards.py · 通识拓展批次56知识卡+题库（幂等）

56：物理学-核能/化学-氧气的用途/生物学-大熊猫/地理学-青藏铁路
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_nucleare",
     "核能与核电站",
     "基础科学知识点内容（人话接口）", "物理学",
     "核能来自原子核的变化：①核裂变——重核（铀-235）被中子撞击分裂成两个中等"
     "核，释放巨大能量并放出更多中子（链式反应）——原子弹与核电站都用裂变，核电"
     "站靠控制棒控制反应速率让能量平稳释放；②核聚变——轻核（氘氚）聚合成重核，"
     "太阳发光的原理，氢弹是不可控聚变；「人造太阳」可控核聚变（ITER/中国EAST）"
     "是终极清洁能源方向。核电站能量链：核能→水蒸气内能→汽轮机机械能→电能（本质"
     "还是烧水发电，只是「炉子」是反应堆）。安全：三代核电技术（华龙一号）双层安"
     "全壳+非能动冷却；核废料需深地质处置。1 千克铀-235 裂变≈2700 吨标准煤。",
     ["核电站利用的是什么能", "核裂变和核聚变的区别", "什么是链式反应",
      "人造太阳是什么", "核电站的能量转化过程", "华龙一号是什么"],
     ["问核辐射防护", "问聚变点火里程碑"],
     "atomic", "",
     "核能=裂变(铀-235·链式反应·核电+原子弹)/聚变(氘氚·太阳·氢弹)；核电链=核→内→机械→电(本质烧水)；华龙一号三代安全；1kg 铀≈2700t 标准煤。"),
    ("kp_card_o2uses",
     "氧气的性质与用途",
     "基础科学知识点内容（人话接口）", "化学",
     "氧气的性质：无色无味气体、不易溶于水、密度略大于空气；化学性质活泼——支持"
     "燃烧（助燃性）和供给呼吸，是「氧化剂」。两大用途由此而来：①供给呼吸——医"
     "疗急救（急救吸氧）、潜水/登山（氧气瓶）、高空飞行；②支持燃烧——炼钢（富氧"
     "强化冶炼）、气焊气割（氧炔焰温度可达 3000℃ 以上）、航天（火箭氧化剂液氧）。"
     "实验室制法（o2lab 呼应）：过氧化氢+二氧化锰。自然界氧气循环：光合作用（绿"
     "色植物/藻类）产生氧、动植物呼吸与燃烧消耗氧——大气氧含量稳定在约 21%。氧"
     "气本身不可燃（不是燃料）——「氧气是助燃剂不是可燃物」是易错点。",
     ["氧气有哪些用途", "氧气的化学性质", "氧气能燃烧吗", "氧炔焰的温度",
      "大气中氧气是怎么循环的", "液氧的用途"],
     ["问氧气的检验方法复习", "问氧化反应分类"],
     "atomic", "",
     "氧气性质=助燃+供呼吸(活泼氧化剂·本身不可燃)；用途=医疗/潜水/登山+炼钢/气焊(氧炔焰 3000℃+)/火箭液氧；循环=光合产氧 vs 呼吸燃烧耗氧(大气 21%)。"),
    ("kp_card_panda",
     "大熊猫为什么是国宝",
     "基础科学知识点内容（人话接口）", "生物学",
     "大熊猫是中国特有珍稀动物，被称为「国宝」「活化石」：①孑遗物种——祖先是史"
     "前食肉动物（小种大熊猫），约 800 万年前就存在，同期物种大多灭绝；②特有性"
     "——野生种群只分布在中国四川、陕西、甘肃的深山竹林（约 1800 余只野生+人工"
     "繁育，降级由「濒危」到「易危」说明保护见效）；③食性奇特——属于食肉目却 99"
     "% 吃竹子（保留了食肉动物的消化系统却演化出伪拇指握竹），每天吃 12-16 小时"
     "竹子；④繁殖困难——发情期短、幼崽极小（约母体千分之一重）。外交名片：熊猫"
     "外交始于唐代（武则天赠日本）；WWF 世界自然基金会会徽就是大熊猫。同为国宝级"
     "的还有朱鹮、金丝猴、羚牛、麋鹿（「国宝五宝」说法）。",
     ["大熊猫为什么是国宝", "大熊猫吃什么", "大熊猫是濒危动物吗",
      "大熊猫生活在哪里", "什么是孑遗物种", "WWF的会徽是什么动物"],
     ["问熊猫消化系统研究", "问濒危等级标准"],
     "atomic", "",
     "大熊猫=国宝：孑遗活化石(800 万年)+中国特有(川陕甘竹林)+食肉目却吃竹(伪拇指)+繁衍难；已从濒危降易危；WWF 会徽；外交名片自唐。"),
    ("kp_card_qingzangrail",
     "青藏铁路：天路",
     "人文通识知识点内容（人话接口）", "地理学",
     "青藏铁路是世界上海拔最高的铁路（「天路」）：西宁—格尔木段 1984 年通车，格"
     "尔木—拉萨段 2006 年通车，全长 1956 公里；穿越青藏高原，途经唐古拉山口（海"
     "拔 5072 米——世界铁路最高点）。两大工程难题：①多年冻土——冻土夏融冬胀破坏"
     "路基，解法=「以桥代路」（清水河特大桥）+热棒（无动力制冷棒把地基热量导"
     "出）；②高寒缺氧与生态——列车供氧系统、沿线设 33 处野生动物通道（藏羚羊迁"
     "徙廊道）。意义：结束西藏不通铁路的历史，西藏与内地时空距离剧减。三大世纪工"
     "程之外（南水北调/西气东输/西电东送），青藏铁路常与之并列为中国基建名片。"
     "拉林铁路（2021，复兴号开上高原）进一步延伸。",
     ["青藏铁路穿越什么高原", "青藏铁路的两大工程难题", "热棒是干什么用的",
      "世界铁路海拔最高点", "为什么要建野生动物通道", "拉林铁路是什么"],
     ["问冻土工程案例对比", "问藏羚羊迁徙路线"],
     "atomic", "",
     "青藏铁路(2006 全线·1956km·海拔最高·唐古拉山口 5072m)：难题=冻土(以桥代路+热棒)+高寒缺氧(供氧)+生态(33 处动物通道)；「天路」；拉林铁路延伸。"),
]

QUESTIONS = [
    ("QB-357", "核电站利用的是什么能", "物理学", "技术直答",
     ["核能", "核裂变"], "通识拓展56"),
    ("QB-358", "氧气有哪些用途", "化学", "技术直答",
     ["医疗", "炼钢", "供呼吸"], "通识拓展56"),
    ("QB-359", "大熊猫为什么是国宝", "生物学", "技术直答",
     ["特有", "珍稀"], "通识拓展56"),
    ("QB-360", "青藏铁路穿越什么高原", "地理学", "技术直答",
     ["青藏高原"], "通识拓展56"),
]


def ensure_seed() -> dict:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    inserted = updated = skipped = 0
    for nid, name, domain, dgroup, content, conds, negs, ktype, sub_route, direct in NODES:
        sa = {
            "name": name,
            "kind": "knowledge_point",
            "knowledge_type": ktype,
            "sub_route": sub_route,
            "domain": domain,
            "domain_group": dgroup,
            "edu_level": "",
            "comment": {
                "name": f"{name}（{dgroup}·通识知识卡）",
                "生效条件": conds,
                "子功能": f"{name}——通识高频问题知识条目",
                "执行": direct or content,
                "不适用条件": negs,
            },
        }
        payload = json.dumps(sa, ensure_ascii=False)
        row = cur.execute("SELECT state_attributes FROM nodes WHERE id=?",
                          (nid,)).fetchone()
        if row and isinstance(row[0], str) and row[0] == payload:
            skipped += 1
            continue
        if not row:
            tags = json.dumps(["knowledge_point", f"domain:{domain}",
                               "level:L2", "status:verified", "batch:通识拓展56"],
                              ensure_ascii=False)
            cur.execute(
                "INSERT INTO nodes (id, content, modality, tags, importance,"
                " confidence, layer, state_attributes, created_at,"
                " spatial_coordinates, temporal_coordinate, condition_space,"
                " semantic_coordinates) VALUES "
                "(?,?,?,?,?,?,?,?," + "CAST(strftime('%s','now') AS INTEGER),"
                 "'[]', '[0,0,0]', '{}', '{}')",
                (nid, content, "text", tags, 0.8, 1.0, "knowledge", payload))
            inserted += 1
        else:
            cur.execute("UPDATE nodes SET state_attributes=?, content=?, "
                        "created_at=CAST(strftime('%s','now') AS INTEGER) "
                        "WHERE id=?", (payload, content, nid))
            updated += 1
    conn.commit()
    conn.close()

    bank = json.load(open(BANK, encoding="utf-8"))
    qs = bank["questions"]
    have = {q["id"] for q in qs}
    added = 0
    for qid, question, domain, qtype, keywords, source in QUESTIONS:
        if qid in have:
            continue
        qs.append({"id": qid, "question": question, "domain": domain,
                   "type": qtype, "keywords": keywords, "source": source,
                   "added": "2026-09-04"})
        added += 1
    bank["version"] = "v1.48"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
