# -*- coding: utf-8 -*-
"""seed_common_503_cards.py · 通识拓展批次503知识卡+题库（幂等）

503：2 张新卡 + 1 张存量域补题·棋牌文学域
    （五子棋 kp_card_gomoku / 扑克牌与斗地主 kp_card_poker 新卡——
    按卡名精确确认双零；《红楼梦》金陵十二钗角度补题与 QB-1290 不重复）。
预检已过（QB-1741~1743 可用）。
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
    ("kp_card_gomoku",
     "五子棋",
     "棋类规则知识点内容（人话接口）", "艺术学堂",
     "五子棋——规则最简的棋类之一：①**棋盘与行棋**——标准棋盘 15×15"
     " 共 225 个交叉点，黑白两色棋子，黑先白后，落子无悔；②**胜负**——"
     "先在横、竖、斜任意方向连成五子者胜（自由规则）；③**职业禁手**——"
     "连珠规则为平衡黑棋先手优势，规定黑棋「三三禁」「四四禁」「长连"
     "禁」（六子及以上），黑棋走出禁手判负；白棋无禁手，长连也算胜"
     "；④**入门价值**——规则一分钟学会、变化却极深，是最好的逻辑启蒙"
     "棋；⑤**段位体系**——业余从 25 级到 1 级再到段位，职业有初段到"
     "九段。",
     ["五子棋怎么下", "五子棋规则", "五子棋禁手是什么",
      "三三禁手", "连珠", "五子棋先手"],
     ["问围棋", "问国际象棋"],
     "atomic", "",
     "五子棋=15乘15盘225交叉点黑先白后落子无悔+横竖斜连五即胜+连珠职"
     "业规则黑棋三三四四长连禁手判负白棋无禁手+规则一分钟学会逻辑启蒙"
     "最佳+业余级位段位职业初段到九段。"),
    ("kp_card_poker",
     "扑克牌与斗地主",
     "棋牌规则知识点内容（人话接口）", "艺术学堂",
     "扑克牌与斗地主——最常见的家庭牌局：①**一副牌**——54 张：黑桃"
     "红桃梅花方块四种花色各 13 张（A-K，A 在多数玩法中既当 1 又当最大"
     "），加大王小王；②**斗地主配置**——三人玩，每人 17 张，翻 3 张底"
     "牌，抢到地主的人共 20 张，地主一对二对抗两农民；③**牌大小**——"
     "3 最小、2 次于王大于 A，小王大于 2、大王最大；④**牌型**——单张"
     "、对子、三张、三带一/二、顺子（五张起连续，不含 2 和王）、连对、"
     "四带二、炸弹（四同张，压一切非炸）、王炸（双王，最大）；⑤**胜负"
     "**——地主或任一农民先出完手牌即该方获胜；「春天」指地主赢而农民"
     "一张未出，计分翻倍。",
     ["斗地主怎么玩", "一副扑克多少张", "斗地主牌大小顺序",
      "王炸是什么", "顺子能带2吗", "斗地主规则"],
     ["问德州扑克", "问象棋"],
     "atomic", "",
     "扑克斗地主=54张四花色各13张加大小王A当1也当最大+三人各17张底牌"
     "3张地主20张一对二+3最小2大于A王最大+牌型单对三带顺子不含2王连对"
     "四带二炸弹王炸最大+先出完方胜春天翻倍。"),
]

QUESTIONS = [
    ("QB-1741", "五子棋的基本规则是什么？黑棋有哪些禁手？",
     "棋类规则", "技术直答",
     ["五子棋", "禁手", "连珠", "黑先"], "通识拓展503·新卡"),
    ("QB-1742", "一副扑克牌有多少张？斗地主的牌大小顺序是什么？",
     "棋类规则", "技术直答",
     ["扑克牌", "斗地主", "王炸", "顺子"], "通识拓展503·新卡"),
    ("QB-1743", "《红楼梦》的金陵十二钗指什么？贾宝玉和林黛玉是什么关系？",
     "文学常识", "技术直答",
     ["金陵十二钗", "贾宝玉", "林黛玉", "大观园"], "通识拓展503·存量补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展503"],
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
    bank["version"] = "v7.68"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
