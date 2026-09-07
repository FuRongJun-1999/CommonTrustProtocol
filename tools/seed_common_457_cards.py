# -*- coding: utf-8 -*-
"""seed_common_457_cards.py · 通识拓展批次457知识卡+题库（幂等）

457：3 张卡补 3 张新角度题（QB-1606~1608）——世界文学名家三连：
    莎士比亚四大悲剧 kp_card_fourtragedies（存量卡补题）/
    安徒生童话 kp_card_andersen（新卡，双零）/
    海明威 kp_card_hemingway（新卡，双零）。
预检已过（QB-1606~1608 可用，三主题精确关键词 0 覆盖）。
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
    ("kp_card_andersen",
     "安徒生童话",
     "世界文学知识点内容（人话接口）", "世界文化",
     "安徒生（1805-1875，丹麦）——「世界童话之王」：①**代表作**——《卖"
     "火柴的小女孩》（除夕夜冻死的悲剧，唤起对穷苦人的同情）、《丑小鸭》"
     "（逆境中成长蜕变，带有自传色彩）、《皇帝的新装》（讽刺虚伪与盲从"
     "——只有孩子说出真话）、《海的女儿》（小美人鱼为爱与灵魂牺牲）；"
     "②**特点**——童话不只是哄孩子的故事，更包裹着对弱者的悲悯、对"
     "虚伪的讽刺与对理想的讴歌；③**影响**——作品被译成 150 多种语言，"
     "丹麦哥本哈根的小美人鱼铜像成为国家象征；4 月 2 日（安徒生生日）"
     "是国际儿童图书日。",
     ["安徒生是哪国人", "卖火柴的小女孩", "丑小鸭的故事",
      "皇帝的新装讽刺什么", "海的女儿", "国际儿童图书日"],
     ["问格林童话", "问儿童文学"],
     "atomic", "",
     "安徒生=丹麦1805到1875世界童话之王+卖火柴的小女孩除夕冻死悲悯穷"
     "苦+丑小鸭逆境蜕变带自传色彩+皇帝的新装讽刺虚伪盲从孩子说真话+海"
     "的女儿为爱与灵魂牺牲+译成150多种语言小美人鱼铜像丹麦象征4月2日"
     "国际儿童图书日。"),
    ("kp_card_hemingway",
     "海明威与《老人与海》",
     "世界文学知识点内容（人话接口）", "世界文化",
     "海明威（1899-1961，美国）——「硬汉文学」代表：①**《老人与海》**——"
     "老渔夫圣地亚哥 84 天没捕到鱼，第 85 天钓到一条比船还大的马林鱼，"
     "搏斗两天两夜，归途中鱼被鲨鱼吃光，拖回的只剩骨架——「人可以被"
     "毁灭，但不能被打败」；凭此获 1953 年普利策奖与 1954 年诺贝尔文学"
     "奖；②**「冰山理论」**——文字只露出八分之一，八分之七藏在水面"
     "之下（留白与潜台词）；③**文风**——电报式简洁（「电文体」），删"
     "一切可有可无的字；④**人生**——亲历两次世界大战，记者出身，"
     "一生冒险（猎狮/斗牛/捕鱼），1961 年病痛中离世。",
     ["老人与海讲什么", "海明威是哪国人", "人可以被毁灭不能被打败",
      "冰山理论", "硬汉文学", "诺贝尔文学奖作家"],
     ["问马克吐温", "问美国文学"],
     "atomic", "",
     "海明威=美国1899到1961硬汉文学代表+老人与海圣地亚哥84天空网大马"
     "林鱼鲨鱼吃光剩骨架人可以被毁灭不能被打败+普利策与诺贝尔奖+冰山"
     "理论文字露八分之七藏水面下+电报式简洁文风+亲历两次大战记者冒险"
     "一生。"),
]

QUESTIONS = [
    ("QB-1606", "莎士比亚的四大悲剧是哪四部？《哈姆雷特》讲了什么故事？",
     "世界文学", "技术直答",
     ["莎士比亚", "四大悲剧", "哈姆雷特", "奥赛罗"], "通识拓展457·存量卡补题"),
    ("QB-1607", "安徒生是哪国的作家？他有哪些著名童话？",
     "世界文学", "技术直答",
     ["安徒生", "童话", "卖火柴", "丑小鸭"], "通识拓展457"),
    ("QB-1608", "《老人与海》讲了什么故事？「冰山理论」是什么？",
     "世界文学", "技术直答",
     ["海明威", "老人与海", "冰山理论", "硬汉"], "通识拓展457"),
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
                               "level:L2", "status:verified", "batch:通识拓展457"],
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
    bank["version"] = "v7.27"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
