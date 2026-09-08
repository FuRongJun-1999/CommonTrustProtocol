# -*- coding: utf-8 -*-
"""seed_common_529_cards.py · 通识拓展批次529知识卡+题库（幂等）

529：1 张新卡 + 1 张存量卡补题·文房篆刻域
    （篆刻印章 kp_card_zhuanke 新卡——id 与语义等价卡名双重确认双零；
    文房四宝产地补题挂 kp_card_brush——与 QB-1377 不重复）。
预检已过（QB-1819~1821 可用）。
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
    ("kp_card_zhuanke",
     "篆刻印章",
     "传统艺术知识点内容（人话接口）", "艺术学堂",
     "篆刻印章——方寸之间的金石气：①**源流**——玺印起于商周，秦以后"
     "「玺」为天子专用、臣民称「印」；汉印法度鼎盛，篆刻讲「印宗秦汉"
     "」；②**文人流派**——明清文人以青田石、寿山石入印，「以刀代笔」"
     "自成艺术，与诗书画并称「诗书画印」四绝；③**刀法**——冲刀爽利、"
     "切刀顿挫，章法讲究疏可走马、密不透风；④**名石**——寿山田黄「石"
     "帝」（一两田黄三两金）、青田石脆润受刀、昌化鸡血石红如凝血；⑤**"
     "印泥**——朱砂印泥色沉百年不褪；⑥**西泠印社**——1904 年创于杭州"
     "孤山，吴昌硕首任社长，「天下第一名社」；⑦**种类**——名章、闲章"
     "（格言雅语）、引首章、收藏鉴赏章。",
     ["篆刻是什么", "印宗秦汉", "田黄", "西泠印社",
      "闲章", "印章的种类"],
     ["问书法", "问汉字六书"],
     "atomic", "",
     "篆刻印章=玺印商周秦后玺为天子专用汉印鼎盛印宗秦汉+明清文人青田"
     "寿山石以刀代笔诗书画印四绝+冲刀切刀疏可走马密不透风+田黄石帝一"
     "两田黄三两金鸡血石+朱砂印泥百年不褪+西泠印社1904孤山吴昌硕首任"
     "社长天下第一名社+名章闲章引首章。"),
]

QUESTIONS = [
    ("QB-1819", "篆刻为什么讲「印宗秦汉」？印章有哪些种类？",
     "传统文化", "技术直答",
     ["篆刻", "印宗秦汉", "汉印", "闲章"], "通识拓展529·新卡"),
    ("QB-1820", "「一两田黄三两金」说的什么石？西泠印社在哪里？",
     "传统文化", "技术直答",
     ["田黄", "寿山石", "西泠印社", "杭州"], "通识拓展529·新卡"),
    ("QB-1821", "文房四宝的著名产地分别在哪里？",
     "传统文化", "技术直答",
     ["文房四宝", "湖笔", "徽墨", "宣纸", "端砚"], "通识拓展529·存量补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展529"],
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
    bank["version"] = "v7.94"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
