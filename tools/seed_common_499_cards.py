# -*- coding: utf-8 -*-
"""seed_common_499_cards.py · 通识拓展批次499知识卡+题库（幂等）

499：1 张新卡 + 2 张存量卡补题·地理天文域
    （世界河流之最 kp_card_riverrecords 新卡，
    哈雷彗星/京杭大运河 存量补题）。
预检已过（QB-1729~1731 可用；坎儿井/元素周期/黑洞均已覆盖跳过）。
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
    ("kp_card_riverrecords",
     "世界河流之最",
     "地理常识知识点内容（人话接口）", "地球家园",
     "世界河流之最——高频地理考点合集：①**最长**——尼罗河（非洲，约"
     "6650 公里）是世界第一长河，古埃及文明沿它而生；②**流量最大**—"
     "—亚马逊河（南美）：流量占全球入海河流约五分之一，流域面积约 700"
     " 万平方公里（世界第一），长度与尼罗河之争尚有争议；③**亚洲最长"
     "**——长江（约 6300 公里），世界第三长河；④**含沙量最大**——黄"
     "河，「一碗水半碗沙」，中华母亲河；⑤**流经国家最多**——多瑙河"
     "（欧洲，流经约 10 国，欧洲第二长河，被称为「蓝色多瑙河」）；⑥"
     "**记忆口诀**——「尼罗最长、亚马逊最旺、长江亚一、黄河最黄」。",
     ["世界最长的河流", "亚马逊河和尼罗河谁长", "世界流量最大的河",
      "亚洲最长的河流", "多瑙河流经几个国家", "河流之最"],
     ["问长江黄河", "问湖泊之最"],
     "atomic", "",
     "世界河流之最=尼罗河非洲约6650公里第一长河古埃及母亲河+亚马逊流"
     "量占全球五分之一流域700万平方公里第一长度有争议+长江6300公里亚"
     "洲最长世界第三+黄河含沙量最大一碗水半碗沙+多瑙河流经约10国最多"
     "蓝色多瑙河。"),
]

QUESTIONS = [
    ("QB-1729", "世界最长的河流是哪条？流量最大的又是哪条？",
     "地理常识", "技术直答",
     ["尼罗河", "亚马逊河", "河流之最", "流量"], "通识拓展499·新卡"),
    ("QB-1730", "哈雷彗星多少年回归一次？下次什么时候能看到？",
     "科学常识", "技术直答",
     ["哈雷彗星", "76年", "2061", "周期"], "通识拓展499·存量卡补题"),
    ("QB-1731", "京杭大运河全长多少？沟通了哪五大水系？",
     "地理常识", "技术直答",
     ["京杭大运河", "五大水系", "1794公里", "世界遗产"], "通识拓展499·存量卡补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展499"],
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
    bank["version"] = "v7.64"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
