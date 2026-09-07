# -*- coding: utf-8 -*-
"""seed_common_383_cards.py · 通识拓展批次383知识卡+题库（幂等）

383：1 张存量卡补题（二维码 kp_card_qrcode，已在库）
    + 2 张新卡（圆珠笔 kp_card_ballpen / 雨伞 kp_card_umbrella）。
KCCS 四要素+题干原句触发词。预检已过（QB-1387~1389 可用，
圆珠笔/雨伞题库卡库双零，二维码题库 0 覆盖）。
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
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO", "SVM"}


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
    ("kp_card_ballpen",
     "圆珠笔",
     "文具常识知识点内容（人话接口）", "生活常识",
     "圆珠笔——最常见的书写工具：①**结构原理**——笔尖一颗微小钢制球珠"
     "嵌在球座里，写字时球珠滚动，把黏稠油墨均匀带到纸上——像「滚筒印"
     "章」的微缩版；②**油墨特点**——黏稠、快干、防水不易晕染（对比钢"
     "笔水性墨易洇纸），一支能写很远（约两三公里字迹）；③**发明**——"
     "1938 年匈牙利记者比罗兄弟申请专利：记者受不了钢笔在报纸上洇墨，"
     "改用报纸油墨般的黏稠墨水+滚珠笔尖；④**写不出来了怎么办**——多"
     "是油墨在球珠处干结或温度低变稠，在纸上快速画圈让球珠摩擦生热、"
     "或换新笔；⑤**优点**——便宜、耐用、免灌墨，是目前全球产量最大的"
     "笔种。",
     ["圆珠笔原理", "圆珠笔是谁发明的", "圆珠笔为什么写不出",
      "圆珠笔和钢笔区别", "球珠的作用", "圆珠笔油墨"],
     ["问钢笔", "问铅笔"],
     "atomic", "",
     "圆珠笔=笔尖球珠滚动带黏稠油墨像滚筒印章+油墨黏稠快干防水不洇纸"
     "一支写两三公里+1938匈牙利记者比罗兄弟发明专利+写不出多因油墨干"
     "结或低温变稠画圈摩擦生热可救+便宜耐用免灌墨产量最大。"),
    ("kp_card_umbrella",
     "雨伞",
     "生活常识知识点内容（人话接口）", "生活常识",
     "雨伞——最日常的雨具：①**起源**——中国传说是鲁班妻子云氏发明"
     "（「能收拢的亭子」）；古代称「簦」，早期还承担礼仪象征（帝王仪仗"
     "华盖）；②**防水原理**——伞面涂层让雨水不浸润，加上伞面张紧、"
     "水滴以珠状滚落；现代多配防水涂层（疏水处理），遮阳伞另加防紫外"
     "线黑胶/银胶层；③**伞为什么会被风吹翻**——伞面上凸呈弧形，强风"
     "从下方钻入产生向上的压差（与飞机机翼升力同理），把伞面顶翻；"
     "「反向伞/抗风伞」把骨架反装或留泄风口，风从缝隙走就不翻；④**"
     "使用提示**——大风天伞骨最易折（收伞背风）；湿伞收起前抖两下水；"
     "遮阳伞淋雨会加速涂层老化，尽量专伞专用。",
     ["雨伞是谁发明的", "伞为什么会被风吹翻", "雨伞防水原理",
      "遮阳伞和雨伞区别", "反向伞是什么", "怎么选雨伞"],
     ["问雨衣", "问防水材料"],
     "atomic", "",
     "雨伞=传说鲁班妻子云氏发明古代称簦+伞面涂层疏水水珠滚落遮阳伞加"
     "防紫外线黑胶+被风吹翻因伞面弧形下钻风压差同机翼升力+反向伞骨架"
     "反装留泄风口+大风天收伞背风遮阳伞淋雨涂层易老化。"),
]

QUESTIONS = [
    ("QB-1387", "二维码是什么原理？为什么破损了还能扫出来？",
     "信息科技", "技术直答",
     ["二维码", "定位", "容错", "纠错"], "通识拓展383·存量卡补题"),
    ("QB-1388", "圆珠笔是怎么写出字来的？为什么有时写不出油？",
     "生活常识", "技术直答",
     ["圆珠笔", "球珠", "油墨", "书写"], "通识拓展383"),
    ("QB-1389", "雨伞为什么会被大风吹翻？遮阳伞能当雨伞用吗？",
     "生活常识", "技术直答",
     ["雨伞", "吹翻", "遮阳伞", "涂层"], "通识拓展383"),
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
                               "level:L2", "status:verified", "batch:通识拓展383"],
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
    bank["version"] = "v6.53"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
