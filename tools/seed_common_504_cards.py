# -*- coding: utf-8 -*-
"""seed_common_504_cards.py · 通识拓展批次504知识卡+题库（幂等）

504：2 张新卡 + 1 张存量卡补题·棋牌文学域
    （跳棋 kp_card_checkers / 军棋 kp_card_junqi 新卡——按卡名精确确认双零；
    海明威 kp_card_hemingway 存量补题——诺奖与代表作角度与 QB-1608 不重复）。
预检已过（QB-1744~1746 可用）。
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
    ("kp_card_checkers",
     "跳棋",
     "棋类规则知识点内容（人话接口）", "艺术学堂",
     "跳棋——最经典的多人家庭棋：①**棋盘**——中国跳棋棋盘是六角星形"
     "（六角每个尖角是一个「营」，各 10 格），可 2-6 人同玩，常见 2 人对"
     "角或 6 人满座；②**棋子**——每方 10 枚弹珠（六色各一营）；③**走"
     "法**——每步两种选择：沿相邻位置走一步，或「隔子跳」——越过紧邻"
     "的一枚棋子（不分敌我）跳到其正后方空位，且可连续跳（连跳是快攻关"
     "键）；④**胜负**——把己方全部棋子率先移满对面营地者胜；⑤**常见"
     "家规**——棋子进营后不得再走出、不许久留他人营「堵门」；⑥**国际"
     "跳棋**——与中跳不同：10×10 棋盘双方各 20 枚扁子，走对角、跳吃对"
     "方子，到底线升「王」。",
     ["跳棋怎么玩", "中国跳棋规则", "跳棋几个人玩",
      "隔子跳", "国际跳棋和中国跳棋区别", "跳棋棋盘"],
     ["问五子棋", "问军棋"],
     "atomic", "",
     "跳棋=中国跳棋六角星形棋盘每营10格2到6人弹珠每方10枚+走一步或隔"
     "子跳可连跳不分敌我+率先移满对面营地者胜+家规进营不出堵门犯规+国"
     "际跳棋10乘10各20枚走对角跳吃底线升王。"),
    ("kp_card_junqi",
     "军棋",
     "棋类规则知识点内容（人话接口）", "艺术学堂",
     "军棋（陆战棋）——模拟战场指挥的棋类：①**棋子等级**——从大到小"
     "：司令、军长、师长、旅长、团长、营长、连长、排长、工兵（大吃小"
     "，同级同归于尽）；②**特殊子**——炸弹与任何棋子相碰同归于尽；地"
     "雷不能移动，只有工兵能排雷，其他棋子撞雷同归于尽；军旗放在大本"
     "营不能动；③**司令阵亡军旗亮**——司令被吃时军旗翻开（对方由此"
     "知道旗在哪）；④**行棋**——公路走一步，铁路线可直线滑行任意远"
     "（工兵在铁路上还能转弯走，机动性最强）；⑤**胜负**——吃掉对方"
     "军旗，或对方无棋可走；另有四人暗棋版与「翻翻棋」玩法（靠运气翻"
     "子比大小）。",
     ["军棋怎么玩", "军棋大小顺序", "司令死了军旗亮",
      "工兵排雷", "军棋铁路线", "陆战棋规则"],
     ["问跳棋", "问象棋"],
     "atomic", "",
     "军棋陆战棋=司令军长师长旅长团长营长连长排长工兵大吃小同级同归+"
     "炸弹同归于尽地雷不能动工兵排雷其他撞雷同归+司令阵亡军旗亮+公路"
     "一步铁路滑行任意远工兵铁路转弯+吃军旗或对方无棋可走胜+四人暗棋"
     "翻翻棋。"),
]

QUESTIONS = [
    ("QB-1744", "中国跳棋怎么玩？怎样才算获胜？",
     "棋类规则", "技术直答",
     ["跳棋", "六角星", "隔子跳", "对角营地"], "通识拓展504·新卡"),
    ("QB-1745", "军棋里司令阵亡为什么军旗要亮开？工兵有什么特殊作用？",
     "棋类规则", "技术直答",
     ["军棋", "司令", "军旗", "工兵"], "通识拓展504·新卡"),
    ("QB-1746", "海明威凭借哪部作品获诺贝尔文学奖？他还有哪些代表作？",
     "文学常识", "技术直答",
     ["海明威", "诺贝尔文学奖", "老人与海", "代表作"], "通识拓展504·存量补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展504"],
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
    bank["version"] = "v7.69"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
