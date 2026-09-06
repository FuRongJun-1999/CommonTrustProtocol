# -*- coding: utf-8 -*-
"""seed_common_294_cards.py · 通识拓展批次294知识卡+题库（幂等）

294：地理-海啸的成因与逃生/气象-龙卷风的形成
KCCS 四要素+题干原句触发词。预检已过（QB-1111/1112+双id可用）。
注：地震已有4题覆盖，本批海啸取海洋灾害角度避让。
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
             "BCS"}


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
    ("kp_card_tsunami",
     "海啸的成因与逃生",
     "地理通识知识点内容（人话接口）", "地理学",
     "海啸逃生的生死知识：①**成因**——海底地震（海底浅源强震最常见）/海底"
     "火山喷发/滑坡，使大范围海水整体位移形成波长数百公里的长波——不是"
     "「大浪」而是「整片海平面抬升的巨量水体」；②**天然预警**——强震后"
     "**海水异常快速退去露出海床**（波谷先到）是海啸将至的明确信号，立即"
     "向高处跑，切勿去捡鱼看热闹（多数死难者死于回看）；③**速度差**——"
     "深海传播时速 700-800 公里（接近客机），近岸减速但浪高暴增（浅水"
     "挤压能量）；④**逃生要点**——跑向内陆高地而非沿海防波堤（巨浪可"
     "越过）、远离河流入海口（溯河而上）、听到预警或多船异常晃动立即上岸"
     "高地；⑤**多波次**——第一波不一定是最大，后续波更猛，警报解除前"
     "勿回海岸；⑥**预警系统**——太平洋海啸预警中心靠地震台+海底压力计"
     "+浮标网络。",
     ["海啸是怎么形成的", "海啸前海水为什么会退去",
      "海啸来了怎么逃生", "海啸能跑过吗", "海啸预警", "第一波最大吗"],
     ["问核爆海啸", "问海堤工程"],
     "atomic", "",
     "海啸=海底强震位移巨量水体长波(非大浪)+强震后海水异常快退=波谷先到"
     "明确信号立即向高处跑勿捡鱼+深海时速700-800km近岸浪高暴增+逃内陆"
     "高地非防波堤+多波次第一波非最大+预警靠海底压力计浮标网。"),
    ("kp_card_tornado",
     "龙卷风的形成",
     "气象通识知识点内容（人话接口）", "地理学",
     "龙卷风怎么「拧」出来：①**必要条件**——强雷暴云（超级单体）中：低层"
     "暖湿气流+高层冷干气流叠加形成强不稳定+水平风切变使空气像「滚轴」"
     "旋转；②**旋转竖起**——上升气流把水平旋转的滚轴「拧」竖起来形成"
     "中气旋，继续收紧加速（角动量守恒：半径越小转越快——滑冰"
     "收臂同原理），中心气压骤降吸起地面尘土碎屑成漏斗状；③**特点**——"
     "直径几十到几百米、风速可达 400+ km/h（地表最强风）、路径窄生命短"
     "（多几分钟到几十分钟）——所以难以预报到具体位置，只能提前预警"
     "「龙卷风警告」；④**美国龙卷走廊**——落基山东侧平原暖湿冷干交汇"
     "最频发（每年上千个）；中国相对少但也有（江苏/广东强对流季）；⑤"
     "**避险**——牢固建筑最低层内间（远离窗户）/地下室最佳；户外勿躲"
     "车内（车会被卷起），就近低洼沟渠伏地护头。",
     ["龙卷风是怎么形成的", "龙卷风和台风的区别", "遇到龙卷风怎么躲",
      "美国为什么龙卷风多", "龙卷风风速多少", "中气旋"],
     ["问尘卷风", "问风等级划分"],
     "atomic", "",
     "龙卷=超级单体强雷暴+风切变滚轴旋转被上升气流拧竖成中气旋+角动量"
     "守恒收紧加速(滑冰收臂同理)+风速400+km/h地表最强路径窄生命短难定位"
     "预报+美国龙卷走廊+避牢固建筑最底层/户外伏低洼护头勿躲车内。"),
]

QUESTIONS = [
    ("QB-1111", "海啸是怎么形成的？海水异常退去说明什么？该怎么逃生？",
     "地理学", "技术直答",
     ["海底", "退去", "高处", "多波次"], "通识拓展294"),
    ("QB-1112", "龙卷风是怎么形成的？遇到龙卷风该怎么躲避？", "地理学", "技术直答",
     ["雷暴", "旋转", "风速", "躲避"], "通识拓展294"),
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
                               "level:L2", "status:verified", "batch:通识拓展294"],
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
    bank["version"] = "v5.65"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
