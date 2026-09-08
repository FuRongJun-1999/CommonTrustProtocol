# -*- coding: utf-8 -*-
"""seed_common_518_cards.py · 通识拓展批次518知识卡+题库（幂等）

518：2 张新卡·古代制度域（古代驿站 kp_card_yizhan /
    常平仓与荒政 kp_card_cangzheng——id 与语义等价卡名双重确认双零）。
预检已过（QB-1786~1788 可用）。
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
    ("kp_card_yizhan",
     "古代驿站",
     "制度史知识点内容（人话接口）", "历史与文明",
     "古代驿站——帝国信息与交通的血脉：①**制度**——「邮」为步递、「"
     "驿」为马传，秦统一后修驰道、直道，驿站体系贯通全国；唐代约每三十"
     "里设一驿，全国驿站一千六百有余；②**速度**——普通文书日行三百"
     "里，紧急军情可至日行五百里，「八百里加急」是极限夸张说法——一"
     "路换马不换人、腰系铜铃逢站即换；③**名场面**——杜牧「一骑红尘妃"
     "子笑」：杨贵妃的荔枝靠驿马接力从南方飞递长安；④**元代站赤**——"
     "蒙古语音译，驿站网络横跨欧亚，设「站户」专供马匹夫役；⑤**结局**"
     "——明末裁撤驿站节省开支，大批驿卒失业，李自成即失业驿卒出身，"
     "投身起义终成亡明之人——一个制度的裁撤改写历史。",
     ["古代驿站是干什么的", "八百里加急", "一骑红尘妃子笑",
      "驿站多少里一个", "李自成是驿卒吗", "站赤"],
     ["问漕运与盐政", "问丝绸之路"],
     "atomic", "",
     "驿站=邮步传驿马传秦驰道贯通唐代三十里一驿全国一千六百余+普通日"
     "三百里紧急五百里八百里加急极限换马不换人+一骑红尘妃子笑荔枝飞递"
     "+元代站赤横跨欧亚站户供役+明末裁驿驿卒李自成失业起义亡明。"),
    ("kp_card_cangzheng",
     "常平仓与荒政",
     "制度史知识点内容（人话接口）", "历史与文明",
     "常平仓与荒政——古人的粮食安全智慧：①**常平仓**——汉宣帝时耿寿"
     "昌首创：丰年谷贱由官府加价收购（籴），荒年谷贵减价出售（粜），平"
     "抑粮价、备荒赈济，历代沿设；②**义仓与社仓**——隋代长孙平奏设义"
     "仓（民间捐粮州县储备），南宋朱熹在乡里推广社仓（乡民互助、春借"
     "秋还）；③**荒政**——灾年的救济制度：开仓赈济、蠲免赋税、施粥"
     "，以及高明的「以工代赈」——宋代范仲淹荒年兴修工程雇饥民，既救"
     "急又建设，不养懒汉；④**管理难题**——储粮霉烂、官吏贪墨、豪强"
     "侵占常使善政打折，「常平」常不平；⑤**启示**——丰歉调节+民间互"
     "助+以工代赈构成古代社会保障三层结构。",
     ["常平仓是什么", "耿寿昌", "义仓和社仓", "以工代赈",
      "古代怎么救灾", "朱熹社仓"],
     ["问漕运与盐政", "问二十四节气"],
     "atomic", "",
     "常平仓荒政=汉宣帝耿寿昌创常平丰年籴荒年粜平抑粮价+隋长孙平义仓"
     "民间捐粮+南宋朱熹社仓春借秋还乡民互助+荒政开仓蠲免施粥+以工代"
     "赈范仲淹荒年兴工雇饥民救急又建设+霉烂贪墨常使善政打折。"),
]

QUESTIONS = [
    ("QB-1786", "古代驿站是做什么用的？「八百里加急」是怎么实现的？",
     "历史常识", "技术直答",
     ["驿站", "八百里加急", "驿马", "换马"], "通识拓展518·新卡"),
    ("QB-1787", "常平仓是怎么运作的？谁首创的？",
     "历史常识", "技术直答",
     ["常平仓", "耿寿昌", "籴", "粜"], "通识拓展518·新卡"),
    ("QB-1788", "什么是「以工代赈」？历史上谁用过这个办法救灾？",
     "历史常识", "技术直答",
     ["以工代赈", "范仲淹", "荒政", "赈灾"], "通识拓展518·存量补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展518"],
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
    bank["version"] = "v7.83"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
