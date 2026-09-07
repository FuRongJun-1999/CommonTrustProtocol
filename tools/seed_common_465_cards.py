# -*- coding: utf-8 -*-
"""seed_common_465_cards.py · 通识拓展批次465知识卡+题库（幂等）

465：3 张新卡·传统美德三连（诚信守诺 kp_card_honesty /
    感恩与知足 kp_card_gratitude / 勤俭节约 kp_card_diligence）。
预检已过（QB-1630~1632 可用，三主题题库 0 覆盖、卡库无同名卡）。
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
    ("kp_card_honesty",
     "诚信守诺",
     "传统美德知识点内容（人话接口）", "传统文化",
     "诚信——立身立业之本：①**内涵**——诚实（不说假话）+守信（说到"
     "做到）；②**典故**——商鞅「立木为信」（搬木头就赏金，取信于民"
     "推行变法）、季布「一诺千金」（答应的事比千金还贵重）、曾子杀猪"
     "（不哄骗孩子，言出必行）；③**反例警示**——烽火戏诸侯：周幽王"
     "失信于诸侯，最终亡国；④**现代价值**——个人征信体系：失信影响"
     "贷款、出行与就业，诚信从美德变成「信用资产」；⑤**怎么做**——"
     "不轻易承诺、承诺了就尽力兑现、做不到及时说明并补救。",
     ["诚信是什么意思", "立木为信的典故", "一诺千金是谁",
      "曾子杀猪的故事", "烽火戏诸侯", "诚信的重要性"],
     ["问宽容美德", "问勤俭节约"],
     "atomic", "",
     "诚信=诚实不说假话守信说到做到+商鞅立木为信取信于民推行变法+季布"
     "一诺千金+曾子杀猪言出必行不哄孩子+烽火戏诸侯失信亡国反例+现代个"
     "人征信失信影响贷款出行就业+不轻诺诺必践做不到及时补救。"),
    ("kp_card_gratitude",
     "感恩与知足",
     "传统美德知识点内容（人话接口）", "传统文化",
     "感恩与知足——幸福感的两大来源：①**感恩之心**——「滴水之恩，当"
     "涌泉相报」；乌鸦反哺、羔羊跪乳的典故教人回报养育之恩；②**感恩的"
     "心理学**——研究表明常写感恩日记的人幸福感更高、抑郁更少——感"
     "恩把注意力从「缺什么」转向「有什么」；③**知足常乐**——老子「知"
     "足者富」：知足不是不上进，而是不被无止境的欲望绑架；④**表达**"
     "——及时说谢谢、用行动回报（陪伴/帮忙）、把善意传递给第三人"
     "（「把爱传下去」）；⑤**家庭实践**——饭前感念食物来之不易、"
     "记住他人帮助的具体细节并当面致谢。",
     ["感恩的意义", "滴水之恩涌泉相报", "知足常乐什么意思",
      "感恩对孩子的好处", "怎么培养感恩", "乌鸦反哺"],
     ["问孝道", "问美德教育"],
     "atomic", "",
     "感恩知足=滴水之恩涌泉相报乌鸦反哺羔羊跪乳回报养育+心理学感恩日"
     "记幸福感更高抑郁更少注意力从缺什么转有什么+老子知足者富不被欲望"
     "绑架非不上进+及时道谢行动回报善意传递+家庭饭前感恩记细节当面致"
     "谢。"),
    ("kp_card_diligence",
     "勤俭节约",
     "传统美德知识点内容（人话接口）", "传统文化",
     "勤俭——持家立业的传统智慧：①**古训**——「静以修身，俭以养德」"
     "（诸葛亮《诫子书》）；「历览前贤国与家，成由勤俭破由奢」（李商"
     "隐）；②**勤**——一勤天下无难事：勤奋补拙、日积月累（「不积跬"
     "步无以至千里」）；③**俭**——俭不是抠门，而是物尽其用、不浪费："
     "珍惜粮食（谁知盘中餐粒粒皆辛苦）、理性消费不冲动囤积；④**现代"
     "场景**——「光盘行动」反对餐饮浪费、旧物改造利用、按需购物；⑤**"
     "平衡**——节俭不等于降低必要的生活与健康投入（该看的病要看、该"
     "用的学习工具要买），省该省的，花该花的。",
     ["勤俭节约的意义", "俭以养德", "光盘行动",
      "怎么教育孩子节俭", "理性消费", "成由勤俭破由奢"],
     ["问理财入门", "问传统美德"],
     "atomic", "",
     "勤俭节约=静以修身俭以养德诫子书成由勤俭破由奢李商隐+勤一勤天下"
     "无难事不积跬步无以至千里+俭非抠门物尽其用不浪费粒粒皆辛苦+现代"
     "光盘行动旧物改造按需购物+平衡节俭不减必要健康学习投入省该省花"
     "该花。"),
]

QUESTIONS = [
    ("QB-1630", "「立木为信」和「一诺千金」讲的是什么？为什么诚信很重要？",
     "传统文化", "技术直答",
     ["诚信", "立木为信", "一诺千金", "守信"], "通识拓展465"),
    ("QB-1631", "为什么说感恩和知足能带来幸福感？",
     "传统文化", "技术直答",
     ["感恩", "知足", "幸福感", "滴水之恩"], "通识拓展465"),
    ("QB-1632", "「成由勤俭破由奢」是什么意思？日常生活中怎么做到节约？",
     "传统文化", "技术直答",
     ["勤俭", "节约", "光盘行动", "理性消费"], "通识拓展465"),
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
                               "level:L2", "status:verified", "batch:通识拓展465"],
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
    bank["version"] = "v7.35"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
