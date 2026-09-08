# -*- coding: utf-8 -*-
"""seed_common_561_cards.py · 通识拓展批次561知识卡+题库（幂等）

561：2 张新卡·民间信仰域（钟馗与门神 kp_card_zhongkui /
    财神与民间信仰 kp_card_caishen——id 与语义等价卡名双重确认双零；
    关公 QB-1805 已有历史题，本批财神角度不重复）。
预检已过（QB-1915~1917 可用）。
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
    ("kp_card_zhongkui",
     "钟馗与门神",
     "民俗信仰知识点内容（人话接口）", "传统文化",
     "钟馗与门神——守门的正义想象：①**钟馗**——传说唐玄宗病中梦小鬼"
     "盗物，终南山进士钟馗捉鬼啖之；玄宗醒后病愈，命吴道子绘《钟馗捉鬼"
     "图》；端午、除夕挂钟馗像驱邪镇宅，「钟馗嫁妹」也是名段；②**门神"
     "最早**——神荼、郁垒：上古神话中在度朔山大桃树下缚鬼喂虎的二神，"
     "桃符（春联前身）即刻二神之名；③**唐代门神**——秦琼（秦叔宝）与"
     "尉迟恭（尉迟敬德）为唐太宗守夜退邪，后画像贴于门上，成为民间最常"
     "见门神组合；④**年画门神**——杨柳青、桃花坞等年画产地把门神印成"
     "年年更新的张贴画；⑤**意涵**——门神承载的是百姓「家宅平安」最"
     "朴素的祈愿。",
     ["钟馗", "门神", "神荼郁垒", "秦琼尉迟恭",
      "钟馗捉鬼", "年画门神"],
     ["问财神", "问年画"],
     "atomic", "",
     "钟馗门神=唐玄宗梦钟馗捉鬼啖之吴道子绘像端午除夕驱邪+神荼郁垒度"
     "朔山大桃树缚鬼桃符前身+秦琼尉迟恭为太宗守夜画像贴门民间最常见门"
     "神组合+杨柳青桃花坞年画年年更新+家宅平安朴素祈愿。"),
    ("kp_card_caishen",
     "财神与民间信仰",
     "民俗信仰知识点内容（人话接口）", "传统文化",
     "财神与民间信仰——把好日子过出来的祈愿：①**正财神**——赵公明（"
     "玄坛真君），道教神祇，麾下有招宝、纳珍、招财、利市四神，专司财源"
     "；②**武财神关公**——商人重其义气守信，奉为护财之神（关羽另有"
     "历史与佛教伽蓝护法身份）；③**文财神**——比干（被剖心，无心故"
     "「不偏心」办事公道）、范蠡（弃官经商三聚三散的陶朱公）；④**迎财"
     "神**——正月初五「破五」迎财神，商家开市；⑤**民间信仰谱系**——"
     "灶王爷（腊月二十三祭灶上天言好事）、土地公、城隍、月老——处处"
     "体现「举头三尺有神明」的自律与温情。",
     ["财神", "赵公明", "武财神关公", "文财神比干",
      "迎财神", "灶王爷"],
     ["问关公", "问八仙过海"],
     "atomic", "",
     "财神民间信仰=正财神赵公明玄坛真君招宝纳珍招财利市四神+武财神关公"
     "义气守信+文财神比干无心不偏心范蠡陶朱公三聚三散+正月初五破五迎财"
     "神商家开市+灶王爷土地公城隍月老举头三尺有神明自律温情。"),
]

QUESTIONS = [
    ("QB-1915", "钟馗捉鬼的传说是什么？钟馗像什么时候挂？",
     "传统文化", "技术直答",
     ["钟馗", "唐玄宗", "吴道子", "驱邪"], "通识拓展561·新卡"),
    ("QB-1916", "门神最早是谁？秦琼和尉迟恭为什么成了门神？",
     "传统文化", "技术直答",
     ["门神", "神荼郁垒", "秦琼", "尉迟恭"], "通识拓展561·新卡"),
    ("QB-1917", "民间信奉的财神有哪几位？「迎财神」在哪一天？",
     "传统文化", "技术直答",
     ["财神", "赵公明", "比干", "迎财神"], "通识拓展561·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展561"],
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
    bank["version"] = "v8.26"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
