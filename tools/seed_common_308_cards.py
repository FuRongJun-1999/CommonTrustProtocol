# -*- coding: utf-8 -*-
"""seed_common_308_cards.py · 通识拓展批次308知识卡+题库（幂等）

308：历史-威尼斯水城/历史-美第奇家族与文艺复兴（文艺复兴专题新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1157/1158+双id可用）。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

WHITELIST = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
             "effect", "OR6A2", "ghrelin", "DOMS", "DHT", "frisson",
             "AlphaGo", "CFOP", "Transformer", "LLM", "GPT", "BERT",
             "CYP3A4", "ACID", "CNN", "RNN", "LSTM", "Krebs", "NADH",
             "FADH2", "Vmax", "Km", "RNA", "DNA", "mRNA", "KCL", "KVL",
             "BCS", "B2H6", "borrow", "Rust"}


def foreign_word_check(text: str) -> list:
    """西里尔字符一律报警；长英文词(≥4)非白名单报警。只扫中文内容字段。"""
    bad = []
    if re.search(r"[\u0400-\u04FF]", text):
        bad.append("cyrillic:" + re.search(r"[\u0400-\u04FF]+", text).group())
    for w in re.findall(r"[A-Za-z]{4,}", text):
        if w not in WHITELIST:
            bad.append("latin:" + w)
    return bad


NODES = [
    ("kp_card_venice",
     "威尼斯水城",
     "历史地理知识点内容（人话接口）", "地理学",
     "威尼斯为什么建在水上：①**出生**——公元 5 世纪蛮族入侵，威尼托居民"
     "逃进亚得里亚海北端的泻湖群岛避难——「难民营」长成海上商业帝国；"
     "②**怎么建的**——泻湖泥滩打百万根木桩入淤泥（橡木/榆木水下缺氧千年"
     "不腐——「泡在咸水里反而长存」），木桩上铺石板建城，118 个岛 400+ "
     "桥连接；③**商业帝国**——十字军东征运输承包+东西方贸易枢纽（丝绸"
     "香料转口），金币「杜卡特」成地中海硬通货，马可·波罗即威尼斯商人；"
     "④**贡多拉**——黑色平底船（窄长适应窄水巷），船夫单桨左划（船身"
     "不对称抵消偏航——造船法的活化石）；⑤**今日危机**——地基沉降+"
     "海平面上升，每年秋汛「水淹威尼斯」，「摩西」活动闸门工程救城；"
     "⑥**无车城市**——主岛禁汽车，船就是车，桥就是路。",
     ["威尼斯为什么建在水上", "威尼斯怎么建的", "贡多拉是什么",
      "威尼斯共和国", "马可波罗是哪国人", "威尼斯水患"],
     ["问泻湖生态", "问阿姆斯特丹对比"],
     "atomic", "",
     "威尼斯=5世纪泻湖避难所长成海上商业帝国+百万木桩入淤泥缺氧千年不腐"
     "+118岛400桥+杜卡特硬通货马可波罗+贡多拉不对称船身活化石+沉降与"
     "海平面上升危机「摩西」闸门救城+主岛无车船为车桥为路。"),
    ("kp_card_medici",
     "美第奇家族与文艺复兴",
     "历史知识点内容（人话接口）", "历史",
     "美第奇家族怎么「买」出文艺复兴：①**发家**——佛罗伦萨银行业（美第"
     "奇银行分行遍布欧洲，教皇的钱庄），15 世纪实际统治佛罗伦萨（无冕之"
     "王，老科西莫/「豪华者」洛伦佐）；②**赞助艺术**——资助米开朗基罗"
     "（少年即被洛伦佐收养培养）/波提切利（《维纳斯的诞生》为其作）/"
     "达芬奇早期；重建圣母百花大教堂穹顶（布鲁内莱斯基）——「把"
     "钱变成美」；③**柏拉图学院**——洛伦佐庇护学者翻译古希腊文献"
     "（人文主义思想库）；④**两位教皇+两任法国王后**——家族走出利奥十"
     "世/克莱孟七世教皇（与米开朗基罗西斯廷恩怨）、凯瑟琳与玛丽两位法国"
     "王后；⑤**马基雅维利**——《君主论》作者即佛罗伦萨外交官，见证"
     "美第奇兴复；⑥**启示**——艺术繁荣背后是商业资本+权力庇护+思想"
     "解放（黑死病动摇教会权威后市民财富寻找新出口）的三重合力。",
     ["美第奇家族", "文艺复兴为什么发生在佛罗伦萨",
      "洛伦佐赞助了谁", "美第奇和米开朗基罗", "君主论作者", "无冕之王"],
     ["问佛罗伦萨建筑", "问文艺复兴三杰"],
     "atomic", "",
     "美第奇=佛罗伦萨银行业教皇钱庄无冕之王(老科西莫豪华者洛伦佐)+赞助"
     "米开朗基罗波提切利达芬奇+布鲁内莱斯基穹顶+柏拉图学院人文主义库+"
     "两教皇两法王后+马基雅维利见证+商业资本权力庇护思想解放三重合力。"),
]

QUESTIONS = [
    ("QB-1157", "威尼斯为什么建在水上？木桩为什么千年不腐？", "历史", "技术直答",
     ["威尼斯", "木桩", "缺氧", "泻湖"], "通识拓展308"),
    ("QB-1158", "美第奇家族对文艺复兴起了什么作用？他们赞助了谁？", "历史", "技术直答",
     ["美第奇", "赞助", "米开朗基罗", "佛罗伦萨"], "通识拓展308"),
]


def ensure_seed() -> dict:
    for nid, *_ in NODES:
        conn = sqlite3.connect(DB)
        row = conn.execute("SELECT id FROM nodes WHERE id=?", (nid,)).fetchone()
        conn.close()
        assert not row, f"id 撞车：{nid} 已存在"
    bank = json.load(open(BANK, encoding="utf-8"))
    have = {q["id"] for q in bank["questions"]}
    for qid, *_ in QUESTIONS:
        assert qid not in have, f"QB 撞车：{qid} 已存在"

    all_text = ""
    for n in NODES:
        all_text += n[1] + " " + n[4] + " " + " ".join(n[5]) + " " \
            + " ".join(n[6]) + " " + n[9] + " "
    for q in QUESTIONS:
        all_text += q[1] + " " + " ".join(q[4]) + " "
    bad = foreign_word_check(all_text)
    assert not bad, f"外文词混入：{bad}"

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
                               "level:L2", "status:verified", "batch:通识拓展308"],
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

    qs = bank["questions"]
    added = 0
    for qid, question, domain, qtype, keywords, source in QUESTIONS:
        if qid in have:
            continue
        qs.append({"id": qid, "question": question, "domain": domain,
                   "type": qtype, "keywords": keywords, "source": source,
                   "added": "2026-09-06"})
        added += 1
    bank["version"] = "v5.78"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
