# -*- coding: utf-8 -*-
"""seed_common_364_cards.py · 通识拓展批次364知识卡+题库（幂等）

364：天文-小行星与陨石/考古-秦始皇陵兵马俑
KCCS 四要素+题干原句触发词。预检已过（QB-1321/1322+双id可用）。
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
    ("kp_card_asteroid2",
     "小行星与陨石",
     "天文通识知识点内容（人话接口）", "基础科学",
     "小行星与陨石：①**小行星带**——火星与木星轨道之间环绕太阳的数十万"
     "颗小行星（谷神星最大直径约 940 公里——现归类矮行星），是太阳系"
     "演化「未完成的行星」原料；②**陨石三类**——石陨石（最常见）/铁"
     "陨石（镍铁合金，纹路独特）/石铁陨石（稀有）；③**流星与陨石**——"
     "流星是尘埃颗粒烧蚀的光迹，未烧尽的残块落到地面才叫陨石；④**撞击"
     "史**——约 6600 万年前一颗直径约 10 公里的小行星撞击墨西哥尤卡坦"
     "半岛（希克苏鲁伯陨石坑），引发环境剧变导致非鸟恐龙灭绝；⑤**近地"
     "监测**——全球多个巡天项目持续搜索近地小行星（潜在撞击威胁评估与"
     "轨道预测），人类首次行星防御撞击实验（改变小行星轨道）2022 年"
     "年成功；⑥**陨石科研价值**——保存太阳系最早期物质，比地球最老岩石"
     "还古老。",
     ["小行星是什么", "陨石从哪来", "恐龙灭绝和小行星",
      "近地小行星监测", "行星防御撞击实验", "陨石的种类"],
     ["问陨石收藏", "问小行星采矿"],
     "atomic", "",
     "小行星=火星木星轨道间数十万颗(谷神星最大940km矮行星)太阳系演化"
     "原料+陨石三类石/铁/石铁+流星是尘埃烧蚀光迹落地残块才叫陨石+"
     "6600万年前10km小行星撞尤卡坦致非鸟恐龙灭绝+近地巡天监测+撞击实验"
     "2022撞击改轨实验成功+陨石保存太阳系最早期物质。"),
    ("kp_card_terracotta_w",
     "秦始皇陵兵马俑",
     "考古通识知识点内容（人话接口）", "历史",
     "秦始皇陵兵马俑——世界第八大奇迹：①**发现**——1974 年陕西西安"
     "临潼农民打井偶然发现，此后建成遗址博物馆；②**规模**——秦始皇陵"
     "园区巨大，兵马俑坑为陪葬坑，已发掘三个坑出土陶俑陶马约 2000 件"
     "（估算总数约 8000 件）；③**工艺**——陶俑平均身高约 1.8 米，"
     "千人千面（发髻/胡须/甲片/神态各不相同），原为彩绘（出土后氧化"
     "褪色，保护技术是世界难题）；④**军阵布局**——一号坑步兵方阵/二号"
     "坑混合兵种（骑兵弩兵车兵）/三号坑指挥部——重现秦军编制；⑤**"
     "意义**——1987 年与长城同列首批中国世界遗产，实证秦代雕塑/冶金/"
     "军事制度水平；⑥**陵墓本体**——封土下的地宫（史载水银模拟江河"
     "百川）尚未发掘，技术保护条件成熟前国家不动主陵。",
     ["兵马俑是干什么的", "兵马俑是怎么发现的", "兵马俑千人千面",
      "兵马俑原来是彩色的吗", "兵马俑为什么珍贵", "秦始皇陵地宫"],
     ["问秦代军事制度", "问文物保护技术"],
     "atomic", "",
     "兵马俑=1974临潼打井偶然发现世界第八大奇迹+秦始皇陵陪葬坑已出"
     "土约2000件估算8000件+陶俑平均1.8m千人千面原为彩绘氧化褪色保护"
     "难题+一号坑步兵二号坑混编三号坑指挥部军阵+1987首批世遗+地宫"
     "未发掘水银江河待技术成熟。"),
]

QUESTIONS = [
    ("QB-1321", "小行星和陨石有什么区别？恐龙灭绝和小行星撞击有什么关系？",
     "基础科学", "技术直答",
     ["小行星", "陨石", "撞击", "恐龙"], "通识拓展364"),
    ("QB-1322", "秦始皇陵兵马俑是怎么发现的？它为什么被称为世界第八大奇迹？",
     "历史", "技术直答",
     ["兵马俑", "1974", "发现", "秦"], "通识拓展364"),
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
                               "level:L2", "status:verified", "batch:通识拓展364"],
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
    bank["version"] = "v6.29"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
