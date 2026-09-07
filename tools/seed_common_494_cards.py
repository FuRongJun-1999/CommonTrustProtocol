# -*- coding: utf-8 -*-
"""seed_common_494_cards.py · 通识拓展批次494知识卡+题库（幂等）

494：3 张新卡·华夏古迹三连（三星堆 kp_card_sanxingdui /
    殷墟与甲骨文 kp_card_yinxu / 乐山大佛 kp_card_leshanbuddha）。
预检已过（QB-1714~1716 可用，三主题题库卡库双零）。
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
    ("kp_card_sanxingdui",
     "三星堆",
     "考古常识知识点内容（人话接口）", "历史与文明",
     "三星堆——四川广汉的古蜀文明遗址：①**年代**——距今约 3000-5000 年"
     "（相当于中原夏商周时期），证明长江上游同样存在高度发达的青铜文明"
     "；②**惊世文物**——青铜大立人（高 2.6 米）、青铜神树（近 4 米）、"
     "纵目面具（眼球柱状凸出、大耳）、黄金面具与金杖——造型奇诡，"
     "「沉睡三千年，一醒惊天下」；③**未解之谜**——文字尚未发现、"
     "奇异物像的文化来源（本土发展还是外来交流）仍在研究；④**地位**"
     "——2021 年新一批祭祀坑发掘再出土海量文物，入选百年百大考古"
     "发现；三星堆遗址列入《中国世界文化遗产预备名单》。",
     ["三星堆在哪里", "三星堆青铜面具", "三星堆是哪个朝代",
      "青铜神树", "纵目面具", "古蜀文明"],
     ["问殷墟", "问金沙遗址"],
     "atomic", "",
     "三星堆=四川广汉古蜀文明距今3000到5000年长江上游青铜文明+青铜大"
     "立人2.6米神树近4米纵目面具黄金面具金杖奇诡沉睡三千年一醒惊天下+"
     "文字未发现文化来源未解+2021新祭祀坑发掘百年百大考古发现+预备名"
     "单。"),
    ("kp_card_yinxu",
     "殷墟与甲骨文",
     "考古常识知识点内容（人话接口）", "历史与文明",
     "殷墟——商代晚期都城遗址（河南安阳）：①**甲骨文**——刻在龟甲兽骨"
     "上的商代文字（占卜记录），1899 年王懿荣首次从「龙骨」药材上识出"
     "，把中国有文字可考的历史上推到商代——现代汉字由它演变而来；②**"
     "重要文物**——后母戊鼎（原称司母戊鼎，重 832.84 千克，世界最大"
     "青铜器之一）；③**妇好墓**——商王武丁之妻妇好的墓葬，出土 1900"
     " 余件文物（女将军的陪葬）；④**地位**——2006 年列入世界遗产；"
     "殷墟甲骨文入选「世界记忆名录」；⑤**意义**——证实了商代的真实"
     "存在（王国维以甲骨文证《史记·殷本纪》基本可信）。",
     ["殷墟在哪里", "甲骨文是谁发现的", "后母戊鼎",
      "妇好墓", "甲骨文的价值", "商朝都城"],
     ["问三星堆", "问中国文字演变"],
     "atomic", "",
     "殷墟=商代晚期都城河南安阳+甲骨文刻龟甲兽骨占卜记录1899王懿荣从龙"
     "骨药材识出现代汉字演变来源把有文字可考历史上推商代+后母戊鼎832."
     "84千克世界最大青铜器之一+妇好墓1900余件文物女将军+2006世界遗产"
     "甲骨文世界记忆名录证实商代真实存在。"),
    ("kp_card_leshanbuddha",
     "乐山大佛",
     "世界遗产知识点内容（人话接口）", "传统文化",
     "乐山大佛——世界最大的古代石刻坐佛：①**规模**——位于四川乐山"
     "岷江、青衣江、大渡河三江汇流处，通高约 71 米，仅脚背就可坐百人；"
     "②**修建**——唐开元元年（713 年）起由海通禅师发起，为「镇水患"
     "」而建，前后历时约 90 年才完工；③**巧思**——大佛依凌云山崖壁"
     "凿刻，发髻内藏排水廊道、衣褶间设排水沟，让雨水顺沟排走不积存，"
     "保护佛像千年不被侵蚀——古代工程的智慧；④**地位**——与峨眉山共同列入世界文化与"
     "自然双遗产（1996）；⑤**参观**——「九曲栈道」可从佛头沿崖壁下"
     "到佛脚，近距离感受巨佛的震撼。",
     ["乐山大佛在哪里", "乐山大佛是谁修建的", "乐山大佛有多高",
      "乐山大佛修了多久", "海通禅师", "峨眉山乐山大佛世界遗产"],
     ["问云冈石窟", "问龙门石窟"],
     "atomic", "",
     "乐山大佛=四川乐山三江汇流处通高约71米脚背可坐百人世界最大古代石"
     "刻坐佛+唐开元元年713年海通禅师发起为镇水患前后约90年完工+发髻内"
     "藏排水廊道保护佛像古代工程智慧+与峨眉山共同1996年双遗产+九曲栈"
     "道可从佛头下到佛脚。"),
]

QUESTIONS = [
    ("QB-1714", "三星堆遗址在哪里？出土了哪些惊世文物？",
     "历史常识", "技术直答",
     ["三星堆", "青铜", "纵目面具", "古蜀"], "通识拓展494·新卡"),
    ("QB-1715", "甲骨文是在哪里发现的？它有什么重要价值？",
     "历史常识", "技术直答",
     ["殷墟", "甲骨文", "商朝", "文字"], "通识拓展494·新卡"),
    ("QB-1716", "乐山大佛有多高？它是为什么而建的？",
     "历史常识", "技术直答",
     ["乐山大佛", "海通", "镇水", "石刻"], "通识拓展494·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展494"],
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
    bank["version"] = "v7.59"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
