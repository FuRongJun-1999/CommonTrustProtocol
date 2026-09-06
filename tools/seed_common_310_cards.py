# -*- coding: utf-8 -*-
"""seed_common_310_cards.py · 通识拓展批次310知识卡+题库（幂等）

310：历史-印加帝国/历史-玛雅文明（美洲古文明新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1163/1164+双id可用）。
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
    ("kp_card_inca",
     "印加帝国",
     "历史知识点内容（人话接口）", "历史",
     "印加——南美洲的「云中帝国」：①**版图与首都**——15-16 世纪南美最大"
     "帝国（安第斯山脉纵贯 4000 公里，「四方之地」），首都库斯科；"
     "②**马丘比丘**——海拔 2400 米山脊上的「失落之城」（石头城不用灰浆"
     "严丝合缝刀插不进——抗震巧思），1911 年被宾厄姆重新「发现」；③**"
     "无文字靠结绳（奇普）记事**——绳结颜色/位置/数量编码信息（统计人口"
     "粮仓），至今未完全破译；④**梯田农业**——安第斯陡坡修梯田种土豆"
     "玉米（土豆/玉米/番茄/辣椒驯化于美洲），山地引水灌溉；⑤**道路与"
     "通信**——两万余公里印加路网（「无马之路」），接力信使（查斯基）"
     "日行百里传递结绳；⑥**灭国**——1533 年皮萨罗 168 人利用内战+天花"
     "+钢铁武器俘虏阿塔瓦尔帕（勒索一屋子黄金后仍处决），帝国崩塌。",
     ["印加帝国", "马丘比丘在哪里", "结绳记事", "印加为什么灭亡",
      "印加路网", "安第斯文明"],
     ["问阿兹特克", "问哥伦布前美洲"],
     "atomic", "",
     "印加=15-16世纪安第斯4000km帝国都库斯科+马丘比丘2400m无灰浆石城"
     "+奇普结绳记事未破译+梯田种土豆+2万km路网接力信使+1533皮萨罗168人"
     "凭内战天花钢铁灭国。"),
    ("kp_card_maya",
     "玛雅文明",
     "历史知识点内容（人话接口）", "历史",
     "玛雅——丛林里的数学家：①**分布与城邦**——中美洲（尤卡坦半岛等地），"
     "从未统一为帝国，而是城邦林立（蒂卡尔/帕伦克/奇琴伊察互相争霸）；"
     "②**金字塔与天文**——阶梯金字塔（库库尔坎金字塔春分蛇影奇观），"
     "天文历法精确：太阳年 365.242 天（误差极小），独立发明「零」概念"
     "（二十进制，比欧洲用于计算更早）；③**文字**——美洲唯一成体系的"
     "成熟文字（象形+音节，800+ 符号），20 世纪中叶才基本破译（纪念碑"
     "记载王族历史而非仅宗教）；④**其他成就**——橡胶球赛（最早的橡胶"
     "利用）、壁画与玉器工艺；⑤**衰落之谜**——公元 9 世纪南部城邦接连"
     "废弃（长期干旱+战争+人口压力多因说），北部玛雅延续到西班牙人到"
     "来；⑥**2012「末日」辟谣**——长纪历一个周期结束被误读为世界末日，"
     "玛雅历法根本没这说法。",
     ["玛雅文明在哪里", "玛雅金字塔", "玛雅文字破译了吗",
      "玛雅历法2012末日", "玛雅为什么衰落", "玛雅人发明了零吗"],
     ["问阿兹特克帝国", "问美洲文明对比"],
     "atomic", "",
     "玛雅=中美洲城邦林立从未统一+阶梯金字塔库库尔坎春分蛇影+太阳年"
     "365.242天独立发明零(二十进制)+美洲唯一成熟文字20世纪中叶破译"
     "+橡胶球赛+9世纪南部衰落(干旱战争多因)+2012末日系周期误读。"),
]

QUESTIONS = [
    ("QB-1163", "印加帝国在哪里？马丘比丘有什么特别之处？", "历史", "技术直答",
     ["印加", "安第斯", "马丘比丘", "结绳"], "通识拓展310"),
    ("QB-1164", "玛雅文明有什么成就？2012 年「世界末日」是怎么回事？",
     "历史", "技术直答",
     ["玛雅", "历法", "零", "末日"], "通识拓展310"),
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
                               "level:L2", "status:verified", "batch:通识拓展310"],
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
    bank["version"] = "v5.80"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
