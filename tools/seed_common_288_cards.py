# -*- coding: utf-8 -*-
"""seed_common_288_cards.py · 通识拓展批次288知识卡+题库（幂等）

288：文化-孙子兵法核心思想/文化-三十六计（兵法智谋新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1090/1091+双id可用）。
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
    ("kp_card_sunzi",
     "孙子兵法核心思想",
     "文化知识点内容（人话接口）", "文化",
     "《孙子兵法》十三篇核心：①**最高境界**——「不战而屈人之兵，善之善者"
     "也」——不通过血战取胜才是最高明（全胜思想）；②**知彼知己**——「知"
     "彼知己，百战不殆」——情报与自我认知是胜负前提；③**先胜后战**——"
     "「胜兵先胜而后求战」——打有准备的仗，计算（庙算）赢了再打；④**"
     "诡道与虚实**——「兵者诡道也」「避实击虚」——调动敌人制造局部优势；"
     "⑤**地形与用间**——「地形者兵之助」+「三军之事莫亲于间」——用间"
     "（情报战）是全书压轴篇；⑥**影响**——春秋末孙武所著，世界最早军事"
     "理论著作之一，译成数十种语言，商战/管理学广泛借用（孙正义等称以"
     "此为师）；⑦**名句辨伪**——「三十六计走为上」不在《孙子兵法》里"
     "（出自三十六计体系）。",
     ["孙子兵法的核心思想", "不战而屈人之兵", "知彼知己百战不殆",
      "孙子兵法是谁写的", "先胜后战什么意思", "兵者诡道也"],
     ["问十三篇逐篇解析", "问克劳塞维茨对比"],
     "atomic", "",
     "孙子兵法=春秋末孙武十三篇+不战而屈人之兵全胜+知彼知己百战不殆+"
     "先胜后战庙算+避实击虚诡道+地形用间压轴+世界最早军事理论之一商管"
     "借用+「三十六计走为上」非本书。"),
    ("kp_card_36ji",
     "三十六计",
     "文化知识点内容（人话接口）", "文化",
     "三十六计速览：①**体系**——明清成书（作者存疑），按阴阳六六之数分六"
     "套：胜战计/敌战计/攻战计/混战计/并战计/败战计，每套六计共三十六；"
     "②**名计速记**——胜战：瞒天过海/围魏救赵（攻其必救）/借刀杀人；"
     "敌战：无中生有/声东击西；攻战：调虎离山/欲擒故纵；混战：浑水摸鱼/"
     "金蝉脱壳；并战：偷梁换柱；败战：走为上计（败局中保全为上）；③**"
     "与孙子兵法区别**——三十六计是计谋清单（战术技巧集），孙子兵法是"
     "战略理论体系，成书年代晚千年；④**哲理内核**——每计皆阴阳转换："
     "示假隐真、以退为进、借力打力；⑤**现代借用**——商业谈判/竞技/"
     "法务策略常用语，但注意道德与法律边界（商业欺诈不因「计谋」合法）；"
     "⑥**名计背后故事**——围魏救赵（孙膑攻魏都迫庞涓回援解赵围）=攻其"
     "必救的经典。",
     ["三十六计有哪些", "围魏救赵的典故", "走为上计是哪一计",
      "三十六计和孙子兵法区别", "欲擒故纵什么意思", "瞒天过海"],
     ["问每计史例解析", "问兵家其他著作"],
     "atomic", "",
     "三十六计=明清成书六套各六计+胜敌攻混并败+名计围魏救赵(攻其必救)"
     "声东击西欲擒故纵走为上+计谋清单vs孙子战略理论成书晚+哲理阴阳"
     "转换示假隐真+现代借用守法律道德边界。"),
]

QUESTIONS = [
    ("QB-1090", "《孙子兵法》的核心思想是什么？「不战而屈人之兵」怎么理解？",
     "文化", "技术直答",
     ["不战", "知彼知己", "先胜", "全胜"], "通识拓展288"),
    ("QB-1091", "「围魏救赵」是什么典故？三十六计和孙子兵法有什么区别？",
     "文化", "技术直答",
     ["围魏救赵", "三十六计", "计谋", "区别"], "通识拓展288"),
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
                               "level:L2", "status:verified", "batch:通识拓展288"],
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
    bank["version"] = "v5.59"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
