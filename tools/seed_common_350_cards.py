# -*- coding: utf-8 -*-
"""seed_common_350_cards.py · 通识拓展批次350知识卡+题库（幂等）

350：文学-《西游记》/文学-《红楼梦》（四大名著细节新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1289/1290+双id可用）。
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
    ("kp_card_xyj2",
     "《西游记》：取经团队",
     "文学知识点内容（人话接口）", "文学",
     "《西游记》取经团队的象征：①**作者与背景**——吴承恩（明），以玄奘"
     "西行取经史实为底本的神魔小说；②**取经团队=一人一性的象征**——"
     "唐僧（信念坚定但肉眼凡胎不辨妖魔）、孙悟空（能力担当/桀骜不驯，"
     "七十二变筋斗云金箍棒）、猪八戒（欲望与懒惰/憨直可爱）、沙僧"
     "（任劳任怨/存在感低）、白龙马（默默负重）；③**经典情节**——大闹"
     "天宫/三打白骨精（团队信任危机）/真假美猴王（心魔外化）/三借芭蕉扇"
     "；④**八十一难**——磨难是修行的必经之路（取经即修心）；⑤**孙悟空"
     "成长线**——从大闹天宫的叛逆到成「斗战胜佛」的成熟；⑥**文化影响**"
     "——孙悟空是世界级文化 IP（影响日本漫画/全球影视游戏改编无数）。",
     ["西游记作者是谁", "取经团队", "三打白骨精",
      "真假美猴王", "八十一难", "斗战胜佛"],
     ["问大闹天宫细节", "问西游记原型玄奘"],
     "atomic", "",
     "西游记=吴承恩神魔小说玄奘西行为底本+团队象征唐僧信念悟空能力"
     "八戒欲望沙僧坚韧+三打白骨精信任危机真假美猴王心魔+八十一难修行"
     "必经+悟空叛逆到斗战胜佛成长+世界级IP。"),
    ("kp_card_hlm2",
     "《红楼梦》：封建社会的百科全书",
     "文学知识点内容（人话接口）", "文学",
     "《红楼梦》为什么是古典小说巅峰：①**作者**——曹雪芹「批阅十载，"
     "增删五次」，前 80 回曹著，后 40 回一般认为高鹗续；②**主线**——"
     "贾宝玉林黛玉薛宝钗的爱情悲剧 + 贾史王薛四大家族由盛转衰；③**人物"
     "群像**——400 多人有名有姓：多愁善感的黛玉/端庄世故的宝钗/精明"
     "强干的王熙凤/率真的湘云/叛逆的宝玉——「正邪两赋」的立体人物；④"
     "**细节**——大观园诗社/黛玉葬花/刘姥姥进大观园/元妃省亲；⑤**"
     "主题**——「假作真时真亦假」的哲思 + 对封建末世的挽歌（女儿悲剧"
     "与家族衰亡互文）；⑥**红学**——因一书成学（版本学/曹学/探佚学），"
     "研究热度延续两百余年。",
     ["红楼梦作者是谁", "红楼梦讲什么", "金陵十二钗",
      "黛玉葬花", "红楼梦后四十回", "红学"],
     ["问红楼人物关系图", "问大观园"],
     "atomic", "",
     "红楼梦=曹雪芹批阅十载增删五次前80回后40高鹗续+宝黛钗爱情悲剧"
     "+四大家族由盛转衰+400多人物立体群像+大观园诗社黛玉葬花+假作真"
     "时真亦假封建末世挽歌+红学一书成学。"),
]

QUESTIONS = [
    ("QB-1289", "《西游记》的作者是谁？取经团队各有什么特点？", "文学", "学科直答",
     ["吴承恩", "孙悟空", "猪八戒", "唐僧"], "通识拓展350"),
    ("QB-1290", "《红楼梦》的作者是谁？它为什么被称为古典小说巅峰？", "文学", "学科直答",
     ["曹雪芹", "贾宝玉", "林黛玉", "四大家族"], "通识拓展350"),
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
                               "level:L2", "status:verified", "batch:通识拓展350"],
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
    bank["version"] = "v6.16"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
