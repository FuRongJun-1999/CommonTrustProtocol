# -*- coding: utf-8 -*-
"""seed_common_417_cards.py · 通识拓展批次417知识卡+题库（幂等）

417：3 张新卡·情绪与效率三连（情绪管理 kp_card_emotionreg /
    时间管理四象限 kp_card_timemgmt4 / 社交紧张与破冰
    kp_card_socialice）。KCCS 四要素+题干原句触发词。
预检已过（QB-1489~1491 可用，三主题题库卡库双零；
拖延 T8-017、安慰 QB-1259 候选查重已被排除）。
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
             "MTBF", "SQA", "IMC", "HMO", "JD", "STAR", "Word", "offer"}


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
    ("kp_card_emotionreg",
     "情绪管理",
     "心理常识知识点内容（人话接口）", "健康与身体",
     "情绪管理——与情绪共处而非对抗：①**情绪ABC理论**（心理学家埃利斯）："
     "A事件、B信念（对事件的解释）、C情绪结果——决定情绪的不是事件本身，"
     "而是你怎么解释它；换个角度看，情绪会跟着变；②**先命名再驯服**——"
     "把情绪说出来（「我现在很焦虑」）能显著降低情绪强度；③**生理调节**——深呼吸（吸4秒屏4秒呼6秒）、运动出汗、"
     "充足睡眠是情绪的「地基」，缺睡的人更容易烦躁；④**表达句式**——"
     "用「我感到…因为…」代替「你怎么总是…」，减少指责减少冲突；⑤**"
     "边界**——情绪管理不等于压抑：长期压抑会反弹，承认情绪、选择合适"
     "时机和方式表达才是健康路径。",
     ["怎么管理情绪", "情绪ABC理论", "生气了怎么办",
      "情绪压抑的危害", "深呼吸放松法", "怎么表达情绪"],
     ["问拖延症", "问冥想"],
     "atomic", "",
     "情绪管理=情绪ABC理论事件信念结果决定情绪的是解释不是事件+先命名"
     "再驯服说出情绪降强度+深呼吸吸4屏4呼6运动睡眠是地基+我感到因为句"
     "式代替指责+管理不等于压抑承认并选择合适方式表达。"),
    ("kp_card_timemgmt4",
     "时间管理四象限",
     "效率方法知识点内容（人话接口）", "职场咨询",
     "时间管理四象限（艾森豪威尔矩阵）：按「重要性」和「紧急性」把事情"
     "分为四类：①**重要且紧急**——马上做（临近截止的项目/突发危机）；"
     "②**重要不紧急**——计划做（学习/健康/关系/长期项目）——这是最"
     "该投入的一格，因为它决定长期生活质量，却最容易被拖延；③**紧急"
     "不重要**——少做或快速处理（临时琐事/别人的临时需求）；④**不重要"
     "不紧急**——尽量不做（无意义刷手机）；⑤**常见陷阱**——被「紧急"
     "」绑架，整天救火，重要不紧急的事永远排不上；**改进**——每周给"
     "重要不紧急的事固定预留时间块，配合番茄工作法执行。",
     ["时间管理四象限", "艾森豪威尔矩阵", "重要不紧急",
      "要事第一", "时间管理方法", "为什么总是很忙没成果"],
     ["问番茄工作法", "问拖延症"],
     "atomic", "",
     "时间管理四象限=艾森豪威尔矩阵按重要紧急分类+重要紧急马上做重要"
     "不紧急计划做这是决定长期质量的一格+紧急不重要少做不重要不紧急不"
     "做+陷阱被紧急绑架整天救火+改进每周给重要不紧急固定时间块配番茄"
     "工作法。"),
    ("kp_card_socialice",
     "社交紧张与破冰",
     "社交技巧知识点内容（人话接口）", "健康与身体",
     "社交紧张——正常且可以改善：①**先接纳**——适度紧张是正常的生理"
     "反应（肾上腺素提升表现），完全「不紧张」反而少见；②**破冰三招**"
     "——从环境找话题（「你也来参加这个活动？」）、开放式提问让对方"
     "多说（少问是非题）、真诚具体的赞美（夸具体细节不夸空泛）；③**"
     "倾听比会说更重要**——对方说话时点头、追问细节，大多数人喜欢"
     "「愿意听我说话」的人；④**小步暴露练习**——从低压力场合开始"
     "（和店员多聊一句），逐步扩大舒适区，回避只会让紧张滚雪球；⑤**"
     "身体语言**——微笑、眼神自然接触、开放姿态（不抱臂），身体放松"
     "会反向带动心理放松。",
     ["社交紧张怎么办", "怎么和陌生人聊天", "破冰话题",
      "内向怎么办", "开放式提问", "社交恐惧和紧张的区别"],
     ["问演讲紧张", "问人际沟通"],
     "atomic", "",
     "社交紧张=适度紧张正常肾上腺素提升表现+破冰三招环境话题开放式提"
     "问具体赞美+倾听比会说重要点头追问+小步暴露低压力场合逐步扩大回"
     "避让紧张滚雪球+微笑眼神开放姿态身体放松带动心理放松。"),
]

QUESTIONS = [
    ("QB-1489", "情绪ABC理论是什么？怎么管理自己的情绪？",
     "健康与身体", "技术直答",
     ["情绪管理", "ABC理论", "调节", "表达"], "通识拓展417"),
    ("QB-1490", "时间管理四象限怎么划分？为什么重要不紧急的事最该做？",
     "职场咨询", "技术直答",
     ["时间管理", "四象限", "要事第一", "紧急"], "通识拓展417"),
    ("QB-1491", "社交时容易紧张怎么办？怎么和陌生人打开话题？",
     "健康与身体", "技术直答",
     ["社交紧张", "破冰", "话题", "练习"], "通识拓展417"),
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
                               "level:L2", "status:verified", "batch:通识拓展417"],
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
    bank["version"] = "v6.88"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
