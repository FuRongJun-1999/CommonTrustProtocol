# -*- coding: utf-8 -*-
"""seed_common_588_cards.py · 通识拓展批次588知识卡+题库（幂等）

588：1 张新卡 + 1 张存量卡补题·泥塑年画域
    （泥人张与惠山泥人 kp_card_nirenzhang 新卡——id 与语义等价卡名
    双重确认双零；年画四大产地补题挂 kp_card_nianhua2）。
预检已过（QB-1996~1998 可用）。
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
    ("kp_card_nirenzhang",
     "泥人张与惠山泥人",
     "传统工艺知识点内容（人话接口）", "传统文化",
     "泥人张与惠山泥人——泥巴里的传神写照：①**泥人张**——天津彩塑世"
     "家，清道光年间张明山创，塑戏文人物惟妙惟肖，徐悲鸿赞其「色调简雅"
     "高尚」，泥人张彩塑列入国家级非遗；②**惠山泥人**——江苏无锡惠山"
     "泥人，相传四百年历史，代表作「大阿福」胖娃憨态，寓意镇邪纳福，亦"
     "为国家级非遗；③**工艺**——取地下净土、过滤捶打、捏塑压光、彩绘"
     "开相，「三分塑七分彩」；④**南北对比**——北派（天津）写实传神、"
     "南派（无锡）丰满圆润；⑤**地位**——泥塑是「指尖上的塑形艺术」，"
     "与面塑、陶塑同宗而各具风韵。",
     ["泥人张", "张明山", "惠山泥人", "大阿福",
      "彩塑", "三分塑七分彩"],
     ["问泥人与面塑", "问玉文化"],
     "atomic", "",
     "泥人张惠山泥人=天津泥人张清道光张明山创塑戏文人物徐悲鸿赞色调简"
     "雅国家级非遗+惠山泥人无锡四百年大阿福镇邪纳福国家级非遗+取净土过"
     "滤捶打捏塑压光彩绘开相三分塑七分彩+北派写实传神南派丰满圆润+指尖"
     "塑形艺术与面塑陶塑同宗。"),
]

QUESTIONS = [
    ("QB-1996", "「泥人张」是谁开创的？他的作品有什么特点？",
     "传统文化", "技术直答",
     ["泥人张", "张明山", "彩塑", "天津"], "通识拓展588·新卡"),
    ("QB-1997", "惠山泥人在哪里？「大阿福」有什么寓意？",
     "传统文化", "技术直答",
     ["惠山泥人", "无锡", "大阿福", "镇邪"], "通识拓展588·新卡"),
    ("QB-1998", "年画的四大产地是哪四个地方？",
     "传统文化", "技术直答",
     ["年画", "杨柳青", "桃花坞", "杨家埠"], "通识拓展588·存量补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展588"],
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
    bank["version"] = "v8.53"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
