# -*- coding: utf-8 -*-
"""seed_common_354_cards.py · 通识拓展批次354知识卡+题库（幂等）

354：文化-端午节/文化-重阳节（传统节日细节新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1299/1300+双id可用）。
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
    ("kp_card_duanwu2",
     "端午节",
     "传统节日知识点内容（人话接口）", "文化",
     "端午节——粽叶飘香的纪念：①**时间**——农历五月初五（「端」为开端，"
     "五月第一个五日）；②**起源**——纪念战国楚国诗人屈原投汨罗江（百姓"
     "划船打捞投粽防鱼啄）；亦有吴越龙图腾祭祀/恶月驱疫等更早源头说；③"
     "**习俗**——赛龙舟（缘起打捞竞渡）/吃粽子（角黍）/挂艾草菖蒲（驱"
     "虫避秽）/佩香囊/系五彩绳/饮雄黄酒（含砷现已不提倡）；④**科学性**"
     "——五月湿热疫病高发，挂艾草熏香卫生活动实为夏季防疫智慧；⑤**地位**"
     "——中国首个入选世界非遗的节日（2009 年）；⑥**文化符号**——屈原"
     "《离骚》「路漫漫其修远兮，吾将上下而求索」精神与端午绑定。",
     ["端午节是怎么来的", "端午节为什么要吃粽子", "赛龙舟的由来",
      "端午节挂艾草", "端午节是几月几号", "屈原投江"],
     ["问端午南北习俗差异", "问其他传统节日"],
     "atomic", "",
     "端午=农历五月初五纪念屈原投汨罗江+赛龙舟吃粽子挂艾草菖蒲佩香囊"
     "系五彩绳+五月湿热实为夏季防疫智慧+2009年中国首个入选世界非遗节日"
     "+离骚求索精神绑定。"),
    ("kp_card_chongyang2",
     "重阳节",
     "传统节日知识点内容（人话接口）", "文化",
     "重阳节——登高敬老的节日：①**时间**——农历九月初九（《易经》九为"
     "阳数，双九重阳）；②**习俗**——登高避灾（秋天瘟气说）/插茱萸/赏菊"
     "饮菊花酒（陶渊明「采菊东篱下」/王维「遥知兄弟登高处，遍插茱萸少"
     "一人」）/吃重阳糕（「糕」谐「高」）；③**现代转型**——1989 年定为"
     "「老人节」（敬老爱老主题），2013 年《老年人权益保障法》法定老年"
     "节；④**文化意涵**——九九谐音「久久」长寿之意，登高远望亦有怀人"
     "思乡传统；⑤**健康智慧**——秋高气爽宜登高锻炼，赏菊调节情志——"
     "传统节日暗合养生节律。",
     ["重阳节是哪一天", "重阳节为什么要登高", "遍插茱萸少一人",
      "重阳节和老人节", "重阳糕", "菊花酒"],
     ["问重阳诗词", "问敬老文化"],
     "atomic", "",
     "重阳=农历九月初九双九阳数+登高插茱萸赏菊饮菊花酒吃重阳糕谐久久"
     "长寿+王维九月九日忆山东兄弟+1989老人节2013法定老年节+秋日登高"
     "锻炼赏菊情志暗合养生。"),
]

QUESTIONS = [
    ("QB-1299", "端午节是怎么来的？有哪些习俗？", "文化", "技术直答",
     ["屈原", "粽子", "龙舟", "艾草"], "通识拓展354"),
    ("QB-1300", "重阳节是哪一天？为什么叫重阳？有什么习俗？", "文化", "技术直答",
     ["九月初九", "登高", "茱萸", "老人节"], "通识拓展354"),
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
                               "level:L2", "status:verified", "batch:通识拓展354"],
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
    bank["version"] = "v6.20"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
