# -*- coding: utf-8 -*-
"""seed_common_513_cards.py · 通识拓展批次513知识卡+题库（幂等）

513：1 张新卡 + 1 张存量卡补题·航海名楼域
    （江南三大名楼 kp_card_minglou 新卡；郑和改存量补题挂
    kp_card_zhenghe——id 撞车断言拦截后的修正，QB-226 仅问朝代，
    本批补深度角度不重复；玄奘 kp_card_xuanzang 已有卡跳过）。
预检已过（QB-1771~1773 可用）。
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
    ("kp_card_minglou",
     "江南三大名楼",
     "建筑文学知识点内容（人话接口）", "传统文化",
     "江南三大名楼——楼以文传的典范：①**黄鹤楼**——武汉蛇山，崔颢《"
     "黄鹤楼》「昔人已乘黄鹤去，此地空余黄鹤楼」令李白搁笔叹「眼前有景"
     "道不得」，李白另留《黄鹤楼送孟浩然之广陵》「烟花三月下扬州」；"
     "②**岳阳楼**——湖南岳阳洞庭湖畔，范仲淹《岳阳楼记》「先天下之忧"
     "而忧，后天下之乐而乐」，滕子京谪守重修嘱文；③**滕王阁**——南昌"
     "赣江边，唐高祖之子滕王李元婴始建，王勃即席挥毫《滕王阁序》「落霞"
     "与孤鹜齐飞，秋水共长天一色」；④**北方名楼**——山西永济鹳雀楼"
     "（王之涣「欲穷千里目，更上一层楼」）、山东蓬莱阁常与三大名楼并列"
     "「四大」之选；⑤**共同点**——名楼之名不在楼而在诗文，建筑屡毁"
     "屡建，文脉千年不断。",
     ["江南三大名楼", "黄鹤楼", "岳阳楼记", "滕王阁序",
      "落霞与孤鹜齐飞", "鹳雀楼"],
     ["问范仲淹", "问王勃"],
     "atomic", "",
     "江南三大名楼=黄鹤楼武汉崔颢昔人已乘黄鹤去李白搁笔烟花三月下扬州"
     "+岳阳楼洞庭范仲淹先天下之忧而忧滕子京重修+滕王阁南昌王勃落霞与"
     "孤鹜齐飞秋水共长天一色+鹳雀楼王之涣欲穷千里目+楼以文传屡毁屡建"
     "文脉不断。"),
]

QUESTIONS = [
    ("QB-1771", "郑和下西洋最远到达了哪里？比哥伦布首航早多少年？",
     "历史常识", "技术直答",
     ["郑和", "下西洋", "非洲东海岸", "哥伦布"], "通识拓展513·存量补题"),
    ("QB-1772", "江南三大名楼是哪三座？分别有哪些名篇？",
     "文学常识", "技术直答",
     ["黄鹤楼", "岳阳楼", "滕王阁", "名楼"], "通识拓展513·新卡"),
    ("QB-1773", "「先天下之忧而忧」出自哪篇文章？作者写它时登的是哪座楼？",
     "文学常识", "技术直答",
     ["岳阳楼记", "范仲淹", "岳阳楼", "先天下之忧"], "通识拓展513·存量补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展513"],
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
    bank["version"] = "v7.78"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
