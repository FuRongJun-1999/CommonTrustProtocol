# -*- coding: utf-8 -*-
"""seed_common_477_cards.py · 通识拓展批次477知识卡+题库（幂等）

477：3 张新卡·世界经典名著三连（《小王子》 kp_card_littleprince /
    《鲁滨逊漂流记》 kp_card_crusoe / 《爱丽丝漫游奇境》
    kp_card_alice）。预检已过（QB-1666~1668 可用，
    三主题题库卡库双零）。
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
    ("kp_card_littleprince",
     "《小王子》",
     "世界文学知识点内容（人话接口）", "世界文化",
     "《小王子》——圣埃克苏佩里（法国作家兼飞行员）1943 年出版的哲理"
     "童话：①**故事**——来自 B-612 小行星的小王子游历各个星球（傲慢"
     "的国王、爱慕虚荣的人、忙碌的商人……最后到地球遇见狐狸），最终"
     "借毒蛇之助回到他的玫瑰身边；②**金句**——狐狸说「真正重要的东西，"
     "用眼睛是看不见的，要用心去看」；「你为你的玫瑰花费的时间，让她变"
     "得如此重要」；③**主题**——用孩子的眼睛反观成人世界：爱、责任、"
     "孤独与纯真；④**地位**——全球销量仅次于《圣经》与《双城记》的"
     "图书之一，被译成 300 多种语言。",
     ["小王子是谁写的", "小王子讲了什么", "小王子的玫瑰",
      "驯养的狐狸", "B-612小行星", "圣埃克苏佩里"],
     ["问安徒生童话", "问世界名著"],
     "atomic", "",
     "小王子=圣埃克苏佩里1943年哲理童话法国飞行员作家+B-612小行星游历"
     "各星球傲慢国王虚荣商人到地球遇狐狸最终回玫瑰身边+狐狸说真正重要"
     "的东西用眼睛看不见要用心看你为玫瑰花费的时间让她重要+孩子眼睛反"
     "观成人世界爱责任孤独纯真+译成300多种语言。"),
    ("kp_card_crusoe",
     "《鲁滨逊漂流记》",
     "世界文学知识点内容（人话接口）", "世界文化",
     "《鲁滨逊漂流记》——笛福（英国）1719 年出版，被誉为英国现实主义"
     "小说的开山之作：①**故事**——鲁滨逊海难流落无人荒岛 28 年，靠"
     "双手搭建住所、种大麦水稻、驯养山羊、救下野人「星期五」为伴，"
     "最终获救回国；②**精神内核**——人类面对绝境的顽强意志与开拓"
     "精神：「一个人的荒岛生存史」；③**时代背景**——大航海与殖民"
     "贸易时代的产物，歌颂劳动、进取与实用理性；④**影响**——出版"
     "即轰动，模仿作品众多（「鲁滨逊式」文学），至今是青少年必读"
     "经典。",
     ["鲁滨逊漂流记是谁写的", "鲁滨逊在岛上待了几年",
      "星期五是谁", "笛福", "荒岛求生", "英国现实主义小说"],
     ["问海明威", "问探险故事"],
     "atomic", "",
     "鲁滨逊漂流记=笛福1719年英国现实主义小说开山+海难流落荒岛28年搭"
     "住所种麦驯羊救野人星期五获救回国+精神内核绝境顽强意志开拓精神"
     "+大航海时代歌颂劳动进取实用理性+出版轰动鲁滨逊式文学青少年必读"
     "经典。"),
    ("kp_card_alice",
     "《爱丽丝漫游奇境》",
     "世界文学知识点内容（人话接口）", "世界文化",
     "《爱丽丝漫游奇境》——刘易斯·卡罗尔（英国数学家刘易斯·卡罗尔，"
     "本名道奇森）1865 年出版的奇幻童话：①**故事**——爱丽丝追着穿背"
     "心的白兔掉进兔子洞，进入奇境：身体忽大忽小、疯帽子茶会、柴郡猫"
     "的笑容、红心王后「砍掉他的头」；②**特色**——满篇逻辑悖论与文字"
     "游戏（作者本是牛津数学家），荒诞外表下藏着对维多利亚时代教育"
     "的温和讽刺；③**影响**——「爱丽丝式」成为奇幻文学代名词，被改编"
     "为电影/戏剧无数；④**冷知识**——「柴郡猫的微笑」：没有猫的笑"
     "容，成为哲学与流行文化引用的经典意象。",
     ["爱丽丝漫游奇境是谁写的", "柴郡猫", "疯帽子茶会",
      "刘易斯卡罗尔", "奇幻童话", "爱丽丝的故事"],
     ["问小王子", "问童话文学"],
     "atomic", "",
     "爱丽丝漫游奇境=刘易斯卡罗尔本名道奇森牛津数学家1865年奇幻童话+"
     "追白兔掉进兔子洞忽大忽小疯帽子茶会柴郡猫笑容红心王后砍头+逻辑悖"
     "论文字游戏荒诞外衣温和讽刺维多利亚教育+爱丽丝式成奇幻文学代名词"
     "改编无数。"),
]

QUESTIONS = [
    ("QB-1666", "《小王子》是谁写的？「驯养的狐狸」讲什么道理？",
     "世界文学", "技术直答",
     ["小王子", "圣埃克苏佩里", "狐狸", "驯养"], "通识拓展477"),
    ("QB-1667", "《鲁滨逊漂流记》讲了什么故事？鲁滨逊在岛上待了多少年？",
     "世界文学", "技术直答",
     ["鲁滨逊", "荒岛", "星期五", "笛福"], "通识拓展477"),
    ("QB-1668", "《爱丽丝漫游奇境》的作者是谁？故事有什么特色？",
     "世界文学", "技术直答",
     ["爱丽丝", "卡罗尔", "奇境", "童话"], "通识拓展477"),
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
                               "level:L2", "status:verified", "batch:通识拓展477"],
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
    bank["version"] = "v7.46"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
