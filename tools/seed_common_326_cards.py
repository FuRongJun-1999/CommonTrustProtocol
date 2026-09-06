# -*- coding: utf-8 -*-
"""seed_common_326_cards.py · 通识拓展批次326知识卡+题库（幂等）

326：安全-洪水避险/安全-泥石流逃生（灾害安全延续）
KCCS 四要素+题干原句触发词。预检已过（QB-1217/1218+双id可用）。
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
    ("kp_card_floodsafe",
     "洪水避险",
     "安全常识知识点内容（人话接口）", "生活常识",
     "洪水来了怎么保命：①**预警准备**——关注暴雨预警信号，低洼地区提前"
     "转移到高处（备手电/饮用水/干粮/充电宝）；②**室内转移**——往高层"
     "转移前切断电源煤气（防止水淹漏电爆炸），关闭门窗；③**室外逃生**——"
     "向高处跑（高地/楼房高层），**远离**电线杆变压器（水中漏电）、下水道"
     "井口（井盖被冲开漩涡吞人）、围墙危房（水泡易塌）；④**水域红线**——"
     "流速超过膝盖深的水流就能冲倒成人，切勿冒险蹚水过马路/河流；⑤"
     "**被围困**——上屋顶/树上等显眼高处等待救援，挥动鲜艳衣物/手电"
     "求救，勿独自泅水逃生；⑥**车被淹**——立即弃车往高处（水淹车门"
     "打不开时从车窗逃生）。",
     ["洪水来了怎么办", "洪水避险", "被洪水围困怎么求救",
      "蹚水过马路危险吗", "车被水淹怎么逃生", "暴雨预警"],
     ["问水库泄洪", "问城市内涝治理"],
     "atomic", "",
     "洪水=低洼提前转移备物资+室内断电煤气再上高层+室外高处远离电线"
     "井口危房+过膝水流能冲倒成人勿蹚+围困上屋顶鲜艳求救勿独泅+车淹"
     "弃车砸窗+水电气安全先断。"),
    ("kp_card_debrisflow2",
     "泥石流逃生",
     "安全常识知识点内容（人话接口）", "生活常识",
     "泥石流逃生的关键方向：①**发生征兆**——山区暴雨后溪流突然断流或"
     "变浑浊（上游滑坡堵河或泥沙涌入）、山体出现裂缝异响——立即警觉；"
     "②**逃生方向=垂直于泥石流流动方向向两侧高处山坡跑**——绝对不能"
     "顺着沟谷往下跑（泥石流速度比人快得多），也不能往沟谷下游躲；③"
     "**扎营选址**——露营切不可扎在沟口/河道转弯处/紧贴山脚（泥石流"
     "冲出扇形覆盖区）；④**泥石流 vs 洪水**——泥石流含大量泥沙石块密度"
     "大破坏力更强，可推倒房屋巨石，人被裹挟几乎无自救可能——唯有提前"
     "跑对方向；⑤**雨后风险**——泥石流多发于暴雨中及雨停后数小时"
     "（土壤饱和），大雨后山区仍要保持警惕。",
     ["泥石流来了往哪跑", "泥石流逃生方向", "山区暴雨后注意什么",
      "露营怎么避开泥石流", "泥石流征兆", "泥石流和洪水的区别"],
     ["问滑坡避险", "问地质灾害监测"],
     "atomic", "",
     "泥石流逃生=垂直于流动方向向两侧高处跑(勿顺沟跑泥速快于人)+征兆"
     "溪流断流变浑山体裂缝异响+露营避开沟口河道弯山脚+密度大破坏强无"
     "自救可能唯有提前跑+暴雨中及雨停后数小时高发。"),
]

QUESTIONS = [
    ("QB-1217", "洪水来了怎么避险？被洪水围困应该怎么做？", "生活常识", "技术直答",
     ["高处", "断电", "求救", "蹚水"], "通识拓展326"),
    ("QB-1218", "泥石流来了应该往哪个方向跑？露营时怎么避开危险？", "生活常识", "技术直答",
     ["垂直", "两侧高处", "沟口", "暴雨"], "通识拓展326"),
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
                               "level:L2", "status:verified", "batch:通识拓展326"],
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
    bank["version"] = "v5.96"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
