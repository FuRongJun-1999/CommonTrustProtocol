# -*- coding: utf-8 -*-
"""seed_common_530_cards.py · 通识拓展批次530知识卡+题库（幂等）

530：2 张新卡·古籍碑帖域（古籍装帧 kp_card_guji /
    碑帖拓片 kp_card_beitie——id 与语义等价卡名双重确认双零；
    对联贴法 QB-690 已覆盖跳过）。
预检已过（QB-1822~1824 可用）。
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
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO", "SVM",
             "MTBF", "SQA", "IMC", "HMO", "JD", "STAR", "Word", "offer",
             "XMind", "HDR", "Robotaxi"}


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
    ("kp_card_guji",
     "古籍装帧",
     "文献学知识点内容（人话接口）", "历史与文明",
     "古籍装帧——一部书的形态进化史：①**简策与卷轴**——最早的书写："
     "竹木简编联为「简策」（学富五车即五车竹简），帛书与纸写本则卷在"
     "轴上成「卷轴装」（「开卷有益」「读书破万卷」由此而来）；②**经折"
     "装**——佛经长卷反复折叠成册，方便诵持（今经折装册页仍用于法帖"
     "）；③**蝴蝶装**——宋初将印页对折、版心粘连，翻页如蝶翼展翅；"
     "④**包背装与线装**——元代包背装以书皮包裹书背，明代定型「线装"
     "」：四眼订线、书衣书签函套，是古书标准形态；⑤**雕版印刷**——唐"
     "代发明，现存最早有明确纪年的雕版印刷品是唐咸通九年（868 年）"
     "《金刚经》；⑥**版式术语**——天头地脚、版心、鱼尾、象鼻，皆有"
     "讲究。",
     ["古籍装帧", "线装书", "蝴蝶装", "经折装",
      "雕版印刷", "咸通九年金刚经"],
     ["问汉字六书", "问造纸术"],
     "atomic", "",
     "古籍装帧=简策竹简学富五车卷轴装开卷有益读书破万卷+经折装佛经折"
     "叠+蝴蝶装宋初对折版心粘翻如蝶翼+包背装线装明代定型四眼订线书衣"
     "函套+雕版印刷唐代发明868年金刚经最早纪年+天头地脚版心鱼尾术语。"
     ),
    ("kp_card_beitie",
     "碑帖拓片",
     "文献学知识点内容（人话接口）", "历史与文明",
     "碑帖拓片——石头上的复印术：①**碑与帖**——碑是刻石铭功记事（纪"
     "念性），帖是摹刻名家法书供临摹（艺术性），合称碑帖；②**拓片怎么"
     "做**——宣纸湿覆碑面、捶打入字口，再以墨包扑拓，揭下即「黑底白"
     "字」的拓本——古代的复印技术；③**行话**——拓片雅称「黑老虎」："
     "值钱又水深，鉴别考眼力（看纸、看墨、看捶拓年代）；④**名品**——"
     "《淳化阁帖》（宋淳化三年 992 年汇刻历代法书，「法帖之祖」）；西"
     "安碑林藏汉唐名碑最多（《多宝塔碑》《玄秘塔碑》皆在此）；⑤**意"
     "义**——印刷术普及前，拓片是法书经典传播的最大功臣。",
     ["碑帖拓片", "拓片怎么做的", "黑老虎", "淳化阁帖",
      "西安碑林", "碑和帖的区别"],
     ["问篆刻印章", "问书法"],
     "atomic", "",
     "碑帖拓片=碑记功铭事帖摹刻法书供临摹+拓片湿纸覆碑捶打入字口墨包"
     "扑拓黑底白字古代复印术+行话黑老虎值钱水深考眼力+淳化阁帖992法帖"
     "之祖+西安碑林汉唐名碑最多多宝塔玄秘塔+印刷术前法书传播功臣。"),
]

QUESTIONS = [
    ("QB-1822", "古籍的「线装」和「蝴蝶装」分别是什么样的装帧？",
     "传统文化", "技术直答",
     ["线装", "蝴蝶装", "古籍", "装帧"], "通识拓展530·新卡"),
    ("QB-1823", "现存最早的雕版印刷品是什么？",
     "历史常识", "技术直答",
     ["雕版印刷", "金刚经", "咸通九年", "唐代"], "通识拓展530·新卡"),
    ("QB-1824", "拓片是怎么制作出来的？为什么叫「黑老虎」？",
     "传统文化", "技术直答",
     ["拓片", "碑帖", "黑老虎", "捶拓"], "通识拓展530·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展530"],
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
    bank["version"] = "v7.95"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
