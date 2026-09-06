# -*- coding: utf-8 -*-
"""seed_common_366_cards.py · 通识拓展批次366知识卡+题库（幂等）

366：地理-火山喷发的原理/地理-间歇泉的成因
KCCS 四要素+题干原句触发词。预检已过（QB-1325/1326+双id可用）。
注：QB-356 日本多火山地震已有，本批取火山喷发与间歇泉角度避让。
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
             "BCS", "B2H6", "borrow", "Rust", "sin", "cos", "tan",
             "Dijkstra", "Bellman", "Floyd", "logV"}


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
    ("kp_card_volcano2",
     "火山喷发的原理",
     "地理通识知识点内容（人话接口）", "地理学",
     "火山为什么会喷发：①**能量来源**——地球内部放射性元素衰变产热+地幔"
     "对流，局部岩石熔化成岩浆（比周围岩石轻就向上涌）；②**喷发机制**——"
     "岩浆聚集在岩浆房压力累积，冲破地壳薄弱处喷出（含溶解气体像开汽水"
     "骤然释压气泡爆炸）；③**喷发类型**——溢流式（夏威夷基拉韦厄流动性"
     "强温和喷发）vs 爆发式（维苏威/圣海伦斯黏稠岩浆气体多猛烈爆炸）；④"
     "**产物**——熔岩流/火山灰（可掩埋城市影响全球气候——坦博拉 1815 年"
     "造成「无夏之年」）/火山弹/火山气体；⑤**监测**——地震仪（岩浆移动"
     "微震）/地表形变测量/气体成分分析可提前预警疏散；⑥**富饶的另一面**"
     "——火山灰土壤肥沃（庞贝周边农业发达）+地热温泉资源。",
     ["火山为什么会喷发", "火山喷发的原理", "熔岩和岩浆的区别",
      "维苏威火山", "火山灰影响气候", "火山能预测吗"],
     ["问超级火山", "问火山岛形成"],
     "atomic", "",
     "火山喷发=内部衰变热+地幔对流熔岩浆上涌压力累积冲破薄弱地壳"
     "（溶解气体像汽水释压爆炸增强）+溢流式夏威夷vs爆发式维苏威+产物"
     "熔岩火山灰火山弹+火山灰掩埋城市影响全球气候（坦博拉1815无夏之年）"
     "+地震仪形变气体监测预警+火山灰土壤肥沃地热温泉。"),
    ("kp_card_geyser",
     "间歇泉的成因",
     "地理通识知识点内容（人话接口）", "地理学",
     "间歇泉为什么定时喷发：①**形成条件三要素**——地下高温热源（浅层"
     "岩浆）+特殊的地下水通道（储水腔+收窄的喉管）+充足水源补给——三"
     "者缺一不可（全球间歇泉稀少的原因）；②**喷发机制**——地下储水腔"
     "的水被岩浆加热超过 100°C（高压下不沸腾），一旦水温升至沸点或压力"
     "骤降，水瞬间汽化体积暴增一千多倍把整腔水猛地喷出（过热水汽化）"
     "——喷完重新注水加热循环；③**代表**——美国黄石公园老忠实泉（"
     "约 90 分钟喷一次，高度 30-55 米）、冰岛大间歇泉（英文「间歇泉」一词"
     "的来源）、西藏羊八井；④**新西兰陶波地热区**——间歇泉与泥火山"
     "共生；⑤**应用警示**——地热发电过度抽取会「熄灭」间歇泉（冰岛/"
     "新西兰教训），地热资源须节制开发。",
     ["间歇泉是怎么形成的", "老忠实泉多久喷一次", "冰岛间歇泉",
      "间歇泉为什么会喷发", "羊八井地热", "间歇泉为什么稀少"],
     ["问地热发电", "问温泉类型"],
     "atomic", "",
     "间歇泉=地下高温热源+储水腔收窄喉管+水源三要素缺一不可+高压过热"
     "水汽化体积暴增喷出后重新注水循环+黄石老忠实泉约90分钟喷30-55m"
     "+冰岛大间歇泉词源+西藏羊八井+地热过度开发会熄灭间歇泉。"),
]

QUESTIONS = [
    ("QB-1325", "火山为什么会喷发？火山灰有什么影响？", "地理学", "技术直答",
     ["岩浆", "地壳", "火山灰", "气候"], "通识拓展366"),
    ("QB-1326", "间歇泉是怎么形成的？为什么会定时喷发？", "地理学", "技术直答",
     ["间歇泉", "热源", "储水腔", "喷发"], "通识拓展366"),
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
                               "level:L2", "status:verified", "batch:通识拓展366"],
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
                   "added": "2026-09-07"})
        added += 1
    bank["version"] = "v6.32"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
