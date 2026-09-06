# -*- coding: utf-8 -*-
"""seed_common_352_cards.py · 通识拓展批次352知识卡+题库（幂等）

352：历史-造纸术/历史-印刷术（四大发明补全）
KCCS 四要素+题干原句触发词。预检已过（QB-1293/1294+双id可用）。
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
    ("kp_card_papermaking",
     "造纸术",
     "历史知识点内容（人话接口）", "历史",
     "造纸术的发明与传播：①**前身**——纸出现前中国人用竹简（重）丝绸"
     "（贵）书写，考古发现西汉已有麻纸（粗糙）；②**蔡伦改进**——东汉"
     "蔡伦（105 年）总结改进造纸术：树皮/麻头/破布/旧渔网为原料，"
     "沤煮捣浆抄帘晾晒——原料便宜工艺成熟可量产，称「蔡侯纸」；③"
     "**传播路线**——4 世纪传入朝鲜，7 世纪经朝鲜入日本，8 世纪怛罗斯"
     "之战后造纸工匠被阿拉伯人俘获，造纸术传入撒马尔罕再传欧洲（12 世纪"
     "西班牙），取代昂贵的羊皮纸与埃及莎草纸；④**意义**——知识记录与"
     "传播成本骤降，是文明加速的引擎（欧洲文艺复兴/宗教改革离不开纸张"
     "普及）；⑤**工艺精髓**——将植物纤维分散再重新交织成膜（本质是"
     "纤维重组技术）。",
     ["造纸术是谁改进的", "蔡伦造纸", "造纸术怎么传到欧洲",
      "纸出现之前用什么写字", "造纸术的意义", "蔡侯纸"],
     ["问印刷术", "问古纸考古"],
     "atomic", "",
     "造纸术=西汉麻纸粗糙→东汉蔡伦105年改进（树皮麻头破布渔网沤煮捣浆"
     "抄帘晾晒便宜可量产蔡侯纸）+4世纪朝鲜7世纪日本8世纪怛罗斯之战传入"
     "阿拉伯12世纪欧洲取代羊皮纸莎草纸+知识传播成本骤降文明加速引擎+"
     "植物纤维分散重组技术。"),
    ("kp_card_printing",
     "印刷术的发明",
     "历史知识点内容（人话接口）", "历史",
     "从雕版到活字的印刷革命：①**雕版印刷**——唐初成熟（868 年《金刚"
     "经》是现存最早有明确纪年的雕版印刷品），一页一版整块雕刻；②**"
     "活字革命**——北宋庆历年间毕昇发明胶泥活字（一字一印，排版排版"
     "重复用），元代王祯转轮排字盘+木活字；③**金属活字**——朝鲜15世纪"
     "铸铜活字，欧洲古腾堡1450年代铅活字+印刷机（印刷《圣经》），推动"
     "宗教改革与文艺复兴（知识不再被教会垄断）；④**中国印刷术西传**"
     "——活字理念经西域影响欧洲（古腾堡独立改进的可能性学界有讨论），"
     "但雕版与活字技术源头在中国无疑；⑤**为什么活字在中国未普及**——"
     "汉字字数太多（几万字活字刻制成本高），雕版反更适合中文（一版可"
     "反复印刷存量书版），这是技术与文字特性的适配问题。",
     ["印刷术是谁发明的", "毕昇活字印刷", "雕版印刷",
      "古腾堡印刷机", "活字印刷为什么在中国没普及", "印刷术的意义"],
     ["问套版印刷", "问近代铅印"],
     "atomic", "",
     "印刷术=唐初雕版成熟(868金刚经最早纪年)+北宋毕昇胶泥活字(一字一印"
     "排版重复用)+王祯转轮排字盘木活字+古腾堡1450铅活字印刷机推动宗教"
     "改革文艺复兴+活字中国未普及因汉字字数多雕版更适合+印刷打破知识"
     "垄断。"),
]

QUESTIONS = [
    ("QB-1293", "造纸术是谁改进的？纸出现之前人们用什么写字？", "历史", "技术直答",
     ["蔡伦", "竹简", "丝绸", "蔡侯纸"], "通识拓展352"),
    ("QB-1294", "活字印刷是谁发明的？雕版印刷和活字印刷有什么区别？", "历史", "技术直答",
     ["毕昇", "雕版", "活字", "胶泥"], "通识拓展352"),
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
                               "level:L2", "status:verified", "batch:通识拓展352"],
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
    bank["version"] = "v6.18"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
