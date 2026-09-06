# -*- coding: utf-8 -*-
"""seed_common_286_cards.py · 通识拓展批次286知识卡+题库（幂等）

286：文学-宋词豪放婉约流派/文学-词牌是什么
KCCS 四要素+题干原句触发词。预检已过（QB-1083/1084+双id可用）。
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
    ("kp_card_songci",
     "宋词的豪放与婉约",
     "文学知识点内容（人话接口）", "文化",
     "宋词两大流派：①**婉约派**——题材多闺情离愁/伤春悲秋，风格含蓄细腻"
     "音律谐婉：柳永（市井慢词，「杨柳岸晓风残月」）、李清照（前期清丽"
     "后期沉郁，「帘卷西风人比黄花瘦」，词论「别是一家」）、秦观（「两情"
     "若是久长时」）；②**豪放派**——苏轼开宗（「大江东去」「明月几时有"
     "「但愿人长久」——豪放旷达写进词里，把词从「歌女唱的小曲」提升为"
     "言志文体），辛弃疾集大成（「醉里挑灯看剑」「气吞万里如虎」——"
     "英雄气与家国恨，稼轩体）；③**中间派**——周邦彦精于格律集北宋"
     "大成，姜夔清空骚雅；④**词的演变**——晚唐五代花间派（温庭筠/李煜"
     "「问君能有几多愁」）→北宋柳永铺叙慢词→苏轼拓境→南宋辛弃疾爱国"
     "词；⑤**婉约豪放是风格概括不是门派铁律**——苏轼也有「十年生死两"
     "茫茫」的婉约，李清照也有「生当作人杰」的豪气。",
     ["宋词的豪放派和婉约派", "苏轼辛弃疾是哪一派", "李清照是什么派",
      "宋词代表人物", "大江东去是谁写的", "别是一家"],
     ["问词的格律", "问花间派"],
     "atomic", "",
     "宋词=婉约(柳永市井慢词/李清照别是一家/秦观)细腻谐婉+豪放(苏轼开宗"
     "大江东去拓境言志/辛弃疾稼轩体集大成家国恨)+周邦彦格律姜夔骚雅+"
     "花间派溯源+风格概括非铁律苏亦有婉约李亦有豪气。"),
    ("kp_card_cipai",
     "词牌是什么",
     "文学知识点内容（人话接口）", "文化",
     "词牌常识：①**词牌=填词的曲调格律模板**——词最初是配乐唱的歌词，"
     "每个词牌规定字数/句式/平仄/押韵（如《水调歌头》95 字双调），词牌名"
     "与内容通常无关（《念奴娇》本是歌女名）；②**「填词」由此得名**——"
     "按谱填字，不是自由写诗；③**常见词牌字数**——小令（58 字内，《如梦"
     "令》33 字《浣溪沙》42 字）、中调（59-90 字，《蝶恋花》60 字）、长调"
     "（91 字上，《水调歌头》95 字《满江红》93 字）；④**词牌名来源**——"
     "人名（《念奴娇》歌女/《西江月》）、地名（《扬州慢》）、乐府旧题、"
     "诗句摘字（《忆江南》）；⑤**上下阕**——双调词分两段，上阕写景起兴"
     "下阕抒情议论是常见章法；⑥**词与诗的区别**——词有长短句（「诗余」"
     "「长短句」别名）、依谱而作、最初供宴饮演唱，题材被视作「艳科」直到"
     "苏轼拓展。",
     ["词牌是什么意思", "水调歌头多少字", "填词是什么",
      "词牌名和内容有关系吗", "小令中调长调怎么分", "上下阕"],
     ["问词谱格律细节", "问曲牌对比"],
     "atomic", "",
     "词牌=配乐歌词的曲调格律模板(定字数句式平仄押韵)+按谱填词词牌名与"
     "内容通常无关+小令58内中调59-90长调91上+来源人名地名乐府诗句+双调"
     "上下阕景起情承+词=诗余长短句初为艳科。"),
]

QUESTIONS = [
    ("QB-1083", "宋词的豪放派和婉约派各有什么特点？代表人物是谁？", "文化", "技术直答",
     ["豪放", "婉约", "苏轼", "李清照"], "通识拓展286"),
    ("QB-1084", "词牌是什么意思？为什么写词叫「填词」？", "文化", "技术直答",
     ["词牌", "格律", "填词", "曲调"], "通识拓展286"),
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
                               "level:L2", "status:verified", "batch:通识拓展286"],
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
    bank["version"] = "v5.57"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
