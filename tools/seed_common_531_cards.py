# -*- coding: utf-8 -*-
"""seed_common_531_cards.py · 通识拓展批次531知识卡+题库（幂等）

531：2 张新卡·制度经济域（科举功名阶梯 kp_card_keju_path /
    古代货币 kp_card_gubai——id 与语义等价卡名双重确认无独立卡；
    会试相关 QB-897/1516 为科举概述题，功名阶梯角度不重复；
    度量衡 QB-906 已有题跳过）。
预检已过（QB-1825~1827 可用）。
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
    ("kp_card_keju_path",
     "科举功名阶梯",
     "制度史知识点内容（人话接口）", "历史与文明",
     "科举功名阶梯——明清读书人的登云梯：①**童生**——未过入门考试的"
     "读书人都叫童生（白首尚是童生不稀奇）；②**秀才**——通过县试、"
     "府试、院试成为生员（俗称秀才），见了县官不跪、免徭役；③**举人**"
     "——秀才参加三年一次的省级乡试（秋闱），中者为举人（第一名「解元"
     "」），有做官资格——《儒林外史》范进考的就是举人；④**贡士与进士"
     "**——举人进京会试（春闱）中者为贡士（第一名「会元」），贡士再"
     "经皇帝主持的殿试录取为进士，一甲三名：状元、榜眼、探花；⑤**连中"
     "三元**——乡试、会试、殿试均得第一（解元+会元+状元），历史上屈"
     "指可数；⑥**八股文**——明清考试文体，从四书五经出题，格式死板"
     "，末年成思想枷锁。",
     ["秀才举人状元哪个大", "连中三元", "解元", "范进中举是中什么",
      "殿试", "八股文"],
     ["问科举制度", "问清代科场案"],
     "atomic", "",
     "科举阶梯=童生过县府院试成秀才生员免徭役+乡试秋闱中举人第一名解"
     "元有官资格范进中举+会试春闱中贡士第一名会元+殿试天子门生进士一"
     "甲状元榜眼探花+连中三元乡会殿皆第一屈指可数+八股文四书五经出题"
     "明清思想枷锁。"),
    ("kp_card_gubai",
     "古代货币",
     "经济史知识点内容（人话接口）", "历史与文明",
     "古代货币演变——从贝壳到纸币：①**贝币**——最早用海贝作货币，汉"
     "字里凡与钱财有关的字多带「贝」旁：财、货、贸、购、贫、贱、贵"
     "；②**金属铸币**——春秋战国布币、刀币、圜钱林立；秦统一后行「半"
     "两」钱，方孔圆钱「外圆内方」定型两千年；③**五铢与通宝**——汉"
     "五铢钱通行七百余年；唐武德四年铸「开元通宝」，开「通宝」钱制"
     "（注意：它铸于唐初高祖时，与玄宗「开元」年号无关）；④**交子**——"
     "北宋四川（益州）商业发达催生世界最早的纸币，1023 年由官方发行"
     "，比欧洲纸币早约七百年；⑤**明清**——白银与铜钱并行，晚清引入"
     "机制银元。",
     ["古代用什么钱", "贝币", "开元通宝", "交子",
      "世界上最早的纸币", "方孔圆钱"],
     ["问漕运与盐政", "问四大发明"],
     "atomic", "",
     "古代货币=海贝为币财货贸购贫贱贵贝旁字+战国布币刀币圜钱+秦半两方"
     "孔圆钱外圆内方定型+汉五铢七百年+唐开元通宝武德四年铸与开元年号无"
     "关+北宋交子1023四川官方发行世界最早纸币早欧洲七百年+明清银钱并行"
     "晚清银元。"),
]

QUESTIONS = [
    ("QB-1825", "科举功名从低到高怎么排？秀才和举人谁大？",
     "历史常识", "技术直答",
     ["科举", "秀才", "举人", "进士"], "通识拓展531·新卡"),
    ("QB-1826", "「连中三元」是哪三元？历史上有多罕见？",
     "历史常识", "技术直答",
     ["连中三元", "解元", "会元", "状元"], "通识拓展531·新卡"),
    ("QB-1827", "世界上最早的纸币是什么？出现在哪个朝代？",
     "历史常识", "技术直答",
     ["交子", "北宋", "纸币", "四川"], "通识拓展531·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展531"],
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
    bank["version"] = "v7.96"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
