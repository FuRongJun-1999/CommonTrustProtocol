# -*- coding: utf-8 -*-
"""seed_common_515_cards.py · 通识拓展批次515知识卡+题库（幂等）

515：2 张新卡·晚清小说补位（镜花缘 kp_card_jinghuayuan /
    老残游记 kp_card_laocan——id 与语义等价卡名双重确认零覆盖）。
预检已过（QB-1777~1779 可用）。
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
    ("kp_card_jinghuayuan",
     "镜花缘",
     "古典文学知识点内容（人话接口）", "艺术学堂",
     "《镜花缘》——奇想与学问兼备的神魔小说：①**作者**——李汝珍"
     "（约 1763-1830），久居江苏海州板浦，精通音韵之学，积十余年写成"
     "全书一百回；②**缘起**——武则天寒冬醉令百花齐放，百花仙子失察"
     "被贬凡间为才女；③**主线**——秀才唐敖随妻兄林之洋、舵工多九公"
     "扬帆海外，游历君子国、女儿国、黑齿国等三四十国；④**名场面**——"
     "君子国人「好让不争」，买卖双方互相让价；女儿国男女角色完全颠倒，"
     "林之洋被选为「王妃」险遭缠足——讽刺性别压迫的天才之笔；黑齿国"
     "通国皆是才女；⑤**主旨**——前半海外奇游后半女科考试百位才女齐"
     "聚，主张女子才学不让须眉，兼炫音韵、棋弈、酒令之学。",
     ["镜花缘是谁写的", "李汝珍", "女儿国", "君子国",
      "镜花缘讲什么", "百花仙子"],
     ["问西游记", "问聊斋志异"],
     "atomic", "",
     "镜花缘=李汝珍久居海州板浦精通音韵一百回+武则天醉令百花齐放百花"
     "仙子贬凡+唐敖林之洋多九公海外游历三四十国+君子国好让不争女儿国"
     "男女颠倒林之洋险缠足黑齿国才女+后半女试百位才女女子才学不让须眉"
     "。"),
    ("kp_card_laocan",
     "老残游记",
     "古典文学知识点内容（人话接口）", "艺术学堂",
     "《老残游记》——晚清四大谴责小说之一：①**作者**——刘鹗（1857-"
     "1909），字铁云，小说之外更是金石学家——所著《铁云藏龟》是甲骨文"
     "著录的开山之作；②**主人公**——摇串铃行医的郎中铁英，号老残，"
     "以医者眼光看乱世；③**名场面**——第二回「明湖居听书」白妞说书"
     "，用通感写声音「如一线钢丝抛入天际」，是古典白话写音乐的绝唱；"
     "④**独特批判**——「赃官可恨，人人知之；清官尤可恨，人多不知」："
     "玉贤靠酷刑博「路不拾遗」之名、刚弼刚愎滥断，揭示以道德自饰的"
     "「清官」比贪官更害人；⑤**地位**——与《官场现形记》《二十年目睹"
     "之怪现状》《孽海花》并称晚清四大谴责小说。",
     ["老残游记是谁写的", "刘鹗", "明湖居听书", "白妞说书",
      "清官尤可恨", "谴责小说"],
     ["问儒林外史", "问官场现形记"],
     "atomic", "",
     "老残游记=刘鹗字铁云铁云藏龟甲骨文著录开山+晚清四大谴责小说之一"
     "+老残摇串铃行医郎中+明湖居听书白妞说书钢丝抛天际通感绝唱+清官尤"
     "可恨玉贤刚弼以道德自饰比赃官害人+官场现形记怪现状孽海花并称。"),
]

QUESTIONS = [
    ("QB-1777", "《镜花缘》的作者是谁？书中的女儿国有什么特别之处？",
     "文学常识", "技术直答",
     ["镜花缘", "李汝珍", "女儿国", "男女颠倒"], "通识拓展515·新卡"),
    ("QB-1778", "《老残游记》的作者是谁？「明湖居听书」写的是什么？",
     "文学常识", "技术直答",
     ["老残游记", "刘鹗", "明湖居", "白妞说书"], "通识拓展515·新卡"),
    ("QB-1779", "晚清四大谴责小说是哪四部？",
     "文学常识", "技术直答",
     ["谴责小说", "老残游记", "官场现形记", "孽海花"], "通识拓展515·存量补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展515"],
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
    bank["version"] = "v7.80"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
