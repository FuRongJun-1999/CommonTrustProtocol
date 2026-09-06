# -*- coding: utf-8 -*-
"""seed_common_340_cards.py · 通识拓展批次340知识卡+题库（幂等）

340：人际-怎么安慰人/人际-真诚道歉（人际沟通新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1259/1260+双id可用）。
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
    ("kp_card_comfort2",
     "怎么安慰人",
     "人际沟通知识点内容（人话接口）", "生活常识",
     "安慰人的正确姿势：①**先共情后建议**——对方倾诉时先接住情绪（「这"
     "确实很难受」），别急着讲道理/比惨（「我当年更惨」是安慰大忌）/急着"
     "给方案；②**倾听为主**——让对方把话说完，点头回应比打断分析更有"
     "用——多数人要的是「被理解」不是「被指导」；③**无效安慰清单**——"
     "「想开点」「别难过了」「这有什么大不了」（否定情绪=二次伤害）；④"
     "**有效动作**——具体帮忙（带饭/陪跑一趟医院）胜过万句安慰，陪伴"
     "本身就是力量；⑤**给希望但不画饼**——「会过去的」要配上「我陪着"
     "你」；⑥**分寸**——对方不想说就不追问，留出空间也是安慰。",
     ["怎么安慰人", "朋友难过怎么安慰", "安慰人的话",
      "共情是什么", "安慰的大忌", "倾听的力量"],
     ["问心理咨询区别", "问安慰失恋朋友"],
     "atomic", "",
     "安慰=先共情接住情绪再建议+倾听为主被理解非被指导+忌比惨讲道理"
     "否定情绪+具体帮忙胜万语+会过去配我陪你+不追问留空间分寸。"),
    ("kp_card_apology2",
     "真诚道歉",
     "人际沟通知识点内容（人话接口）", "生活常识",
     "道歉怎么才算真诚：①**四要素**——说「对不起」（明确承认错误）+说"
     "清错在哪（理解对方的损失与感受）+表达悔意+给出改正行动——缺一步"
     "都像走过场；②**大忌话术**——「但是」开头（道歉变辩解）、「如果"
     "让你不舒服」（如果=不认错）、「我都道歉了你还想怎样」（要挟式"
     "道歉）；③**不找借口**——解释原因可以有，但不能盖过认错本身；④"
     "**行动补过**——能弥补的弥补（赔偿/修复），改了才是道歉的完成态；"
     "⑤**对方不原谅**——道歉是自己的责任，原谅是对方的权利，给对方"
     "时间，别逼「我都道歉了你还要怎样」；⑥**及时**——越拖越难开口，"
     "隔阂越结越深。",
     ["怎么道歉才真诚", "道歉的技巧", "对不起怎么说",
      "道歉对方不原谅怎么办", "道歉需要行动", "真诚道歉四要素"],
     ["问职场道歉", "问原谅心理学"],
     "atomic", "",
     "真诚道歉=四要素对不起+认错内容+悔意+改正行动缺一像走过场+忌但是"
     "开头如果开头要挟式+不找借口盖过认错+行动补过才是完成态+原谅是"
     "对方权利给时间+越拖越难开口及时。"),
]

QUESTIONS = [
    ("QB-1259", "朋友心情不好怎么安慰？安慰人有什么技巧？", "生活常识", "技术直答",
     ["共情", "倾听", "陪伴", "建议"], "通识拓展340"),
    ("QB-1260", "怎么道歉才真诚？道歉时要注意什么？", "生活常识", "技术直答",
     ["道歉", "认错", "行动", "改正"], "通识拓展340"),
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
                               "level:L2", "status:verified", "batch:通识拓展340"],
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
    bank["version"] = "v6.09"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
