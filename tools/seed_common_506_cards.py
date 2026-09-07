# -*- coding: utf-8 -*-
"""seed_common_506_cards.py · 通识拓展批次506知识卡+题库（幂等）

506：2 张新卡 + 1 张存量域补题·名著民俗域
    （呼啸山庄 kp_card_wuthering / 数九与三伏 kp_card_shujiusanfu 新卡——
    按卡名精确确认双零；勃朗特三姐妹补题挂呼啸山庄新卡，
    与 QB-1678/1747 不重复；中国神话已覆盖跳过）。
预检已过（QB-1750~1752 可用）。
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
    ("kp_card_wuthering",
     "呼啸山庄",
     "世界文学知识点内容（人话接口）", "艺术学堂",
     "《呼啸山庄》——艾米莉·勃朗特唯一的长篇小说：①**作者**——艾米莉"
     "·勃朗特，「勃朗特三姐妹」之一：夏洛蒂著《简·爱》、艾米莉著本书、"
     "安妮著《艾格妮丝·格雷》，三姐妹 1846 年曾以化名合出诗集；②**主"
     "线**——弃儿希斯克利夫被呼啸山庄老恩肖收养，与凯瑟琳青梅竹马，"
     "凯瑟琳却嫁给画眉田庄的林顿；希斯克利夫愤而出走，归来后展开横跨"
     "两代人的复仇——爱恨交织到近乎疯狂；③**风格**——荒野与风暴的哥"
     "特式氛围、倒叙结构（房客洛克伍德与管家耐莉轮流讲述），出版时因"
     "过于激烈遭冷遇，后被追认为经典；④**主题**——「我爱他不是因为他"
     "漂亮，而是因为他比我自己更像我自己」——灵魂层面的爱与毁灭性复"
     "仇；⑤**地位**——英国文学史上最激烈独特的爱情小说之一。",
     ["呼啸山庄是谁写的", "希斯克利夫", "凯瑟琳", "勃朗特三姐妹",
      "呼啸山庄讲什么", "艾米莉·勃朗特"],
     ["问简爱", "问傲慢与偏见"],
     "atomic", "",
     "呼啸山庄=艾米莉·勃朗特唯一长篇勃朗特三姐妹夏洛蒂简爱安妮艾格妮"
     "丝格雷1846合出诗集+弃儿希斯克利夫与凯瑟琳青梅竹马她嫁林顿他复"
     "仇两代人+荒野风暴哥特倒叙洛克伍德耐莉+灵魂之爱与毁灭性复仇出版"
     "遇冷后成经典。"),
    ("kp_card_shujiusanfu",
     "数九与三伏",
     "民俗历法知识点内容（人话接口）", "传统文化",
     "数九与三伏——中国民间计量寒暑的方法：①**数九**——从冬至当天起"
     "数，每九天为「一九」，数满九九八十一天「出九」，寒气消尽春耕开始"
     "；②**数九歌**——「一九二九不出手，三九四九冰上走，五九六九沿河"
     "看柳，七九河开，八九雁来，九九加一九，耕牛遍地走」；③**冷在三九"
     "**——冬至白昼虽最短，但地面热量仍在散失，滞后约三个九才到最冷"
     "（热量收支惯性）；④**三伏**——按干支纪日定：夏至后第三个庚日入"
     "初伏（头伏），第四个庚日为中伏，立秋后第一个庚日为末伏，伏天共"
     "30-40 天；⑤**热在中伏**——同理夏至日照最长但地温持续累积，到中"
     "伏前后最热；⑥**雅趣**——「九九消寒图」：梅花八十一瓣，每天染一"
     "瓣，染完即春深。",
     ["数九从哪天开始", "三九为什么最冷", "三伏天怎么算",
      "数九歌", "热在中伏", "九九消寒图"],
     ["问二十四节气", "问冬至"],
     "atomic", "",
     "数九三伏=冬至起数九天一九九九八十一天出九+数九歌一九二九不出手"
     "三九四九冰上走+冷在三九地面散热滞后惯性+三伏夏至三庚头伏四庚中"
     "伏立秋一庚末伏30到40天+热在中伏地温累积+九九消寒图梅花八十一瓣"
     "。"),
]

QUESTIONS = [
    ("QB-1750", "《呼啸山庄》是谁写的？勃朗特三姐妹各有什么代表作？",
     "文学常识", "技术直答",
     ["呼啸山庄", "艾米莉", "勃朗特三姐妹", "希斯克利夫"], "通识拓展506·新卡"),
    ("QB-1751", "数九从哪一天开始？为什么冷在三九？",
     "传统文化", "技术直答",
     ["数九", "冬至", "三九", "九九"], "通识拓展506·新卡"),
    ("QB-1752", "三伏天是怎么算出来的？为什么热在中伏？",
     "传统文化", "技术直答",
     ["三伏", "庚日", "中伏", "夏至"], "通识拓展506·存量补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展506"],
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
    bank["version"] = "v7.71"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
