# -*- coding: utf-8 -*-
"""seed_common_47_cards.py · 通识拓展批次47知识卡+题库（幂等）

47：物理学-分子热运动/化学-小苏打/生物学-蚯蚓与土壤/历史-开元盛世
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_diffusion",
     "分子的热运动与扩散",
     "基础科学知识点内容（人话接口）", "物理学",
     "一切物质的分子都在不停地做无规则运动——温度越高运动越剧烈（所以叫「热运"
     "动」）。扩散现象是它的直接证据：闻到远处的花香（气体扩散）、红墨水在水里"
     "散开（液体扩散）、金块和铅块压在一起互相渗入（固体扩散，最慢）。温度越高扩"
     "散越快（热牛奶里糖化得快）。相关现象辨析：灰尘飞舞/柳絮飘动是宏观物体机"
     "械运动，不是分子运动（分子肉眼看不见）；腌咸蛋时盐渗进去也是扩散。分子间"
     "还有引力和斥力（固体难拉断、难压缩的原因）——分子动理论三要点：物质由分"
     "子组成、分子永不停息无规则运动、分子间存在作用力。",
     ["闻到花香说明什么", "什么是扩散现象", "温度和分子运动的关系",
      "灰尘飞舞是分子运动吗", "腌咸蛋的原理", "分子动理论的内容"],
     ["问布朗运动", "问物态变化微观解释"],
     "atomic", "",
     "分子永不停息无规则热运动(温度越高越烈)；扩散=直接证据(花香/墨水散开/腌咸蛋)；灰尘柳絮=机械运动非分子；分子间有引斥力。"),
    ("kp_card_bakingsoda",
     "小苏打与纯碱",
     "基础科学知识点内容（人话接口）", "化学",
     "小苏打是碳酸氢钠（NaHCO₃）——白色细小晶体，受热分解产生二氧化碳（2NaHCO₃"
     "→Na₂CO₃+H₂O+CO₂↑），这是烘焙面团蓬松的原理；胃酸过多也可服用（弱碱性中"
     "和盐酸）。纯碱是碳酸钠（Na₂CO₃，苏打）——碱性更强，用于玻璃制造/洗涤（俗"
     "名「纯碱」「洗涤碱」，注意它是盐不是碱）。两者区分是常考点：做馒头用小苏"
     "打，工业玻璃用纯碱。膨松原理补充：酵母发酵（生物产气）与泡打粉（含小苏打"
     "+酸性粉遇水产气）都是「产气使面团疏松」。侯德榜联合制碱法（1943）打破国外"
     "垄断，是中国化工史的里程碑。",
     ["小苏打的化学名称", "小苏打和纯碱的区别", "面团为什么会蓬松",
      "胃酸过多吃什么中和", "纯碱是碱吗", "侯德榜制碱法"],
     ["问碳酸两种盐转化", "问发酵生物学"],
     "atomic", "",
     "小苏打=NaHCO₃(受热产气·烘焙蓬松·中和胃酸)；纯碱=Na₂CO₃(是盐非碱·玻璃/洗涤)；酵母=生物产气；侯德榜联合制碱 1943。"),
    ("kp_card_earthworm",
     "蚯蚓与土壤改良",
     "基础科学知识点内容（人话接口）", "生物学",
     "蚯蚓是环节动物（身体由许多相似的环状体节构成），被称为「土壤工程师」：①"
     "钻穴松土——增加土壤透气性和透水性；②改良肥力——吞食落叶泥土排出粪便是优"
     "质有机肥；③降解有机垃圾——可用于堆肥处理。呼吸方式特殊：没有肺，用**湿润"
     "的皮肤**呼吸（氧气溶解在体表黏液里渗入）——所以雨后蚯蚓纷纷钻出地面（土壤"
     "缝隙充满水缺氧）；这也是为什么不能用手直接久抓蚯蚓（皮肤会被搓干窒息）。切"
     "成两段能否再生：前端（有环带的一段）可再生出后端，不是两段都能活。达尔文晚"
     "年专门研究蚯蚓，称赞它为「地球上最有价值的动物」之一。",
     ["蚯蚓对土壤有什么好处", "蚯蚓用什么呼吸", "雨后蚯蚓为什么爬出来",
      "蚯蚓切成两段都能活吗", "蚯蚓属于什么动物", "什么是环带"],
     ["问环节动物其他成员", "问土壤生态循环"],
     "atomic", "",
     "蚯蚓=环节动物·土壤工程师(松土/粪便肥田/降解垃圾)；用湿润皮肤呼吸(雨后出土因缺氧)；再生=有环带前端段可活；达尔文盛赞。"),
    ("kp_card_kaiyuan",
     "开元盛世",
     "人文通识知识点内容（人话接口）", "历史",
     "开元盛世：唐玄宗李隆基统治前期的鼎盛局面（713-741 年，年号「开元」）——"
     "任用姚崇、宋璟等贤相，整顿吏治、发展生产、提倡文教，唐朝国力达到顶峰：人"
     "口约五六千万、长安成为百万人口的国际大都会、杜甫忆「忆昔开元全盛日，小邑"
     "犹藏万家室」。后期转折：玄宗晚年宠杨贵妃、怠政享乐（「从此君王不早朝」），"
     "755 年安史之乱爆发，盛唐戛然而止——「开元盛世」与「安史之乱」同一个皇帝，"
     "是盛极而衰的经典案例。同期文化：李白杜甫的诗歌、书法颜真卿、画圣吴道子。 "
     "与「贞观之治」（唐太宗）、「康乾盛世」并列为治世教科书。",
     ["开元盛世是哪个皇帝时期的", "开元盛世的表现", "姚崇宋璟是谁的宰相",
      "忆昔开元全盛日是谁写的", "唐朝由盛转衰的转折", "贞观之治和开元盛世哪个早"],
     ["问唐代经济制度", "问安史之乱成因"],
     "atomic", "",
     "开元盛世=唐玄宗李隆基前期(713-741)：用姚崇宋璟·国力顶峰·长安百万人口；晚年怠政→755 安史之乱由盛转衰；杜甫「忆昔开元全盛日」。"),
]

QUESTIONS = [
    ("QB-321", "闻到花香说明什么", "物理学", "技术直答",
     ["分子运动", "扩散"], "通识拓展47"),
    ("QB-322", "小苏打的化学名称", "化学", "技术直答",
     ["碳酸氢钠"], "通识拓展47"),
    ("QB-323", "蚯蚓对土壤有什么好处", "生物学", "技术直答",
     ["松土", "肥力"], "通识拓展47"),
    ("QB-324", "开元盛世是哪个皇帝时期的", "历史", "技术直答",
     ["唐玄宗", "李隆基"], "通识拓展47"),
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
                               "level:L2", "status:verified", "batch:通识拓展47"],
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
    bank["version"] = "v1.39"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
