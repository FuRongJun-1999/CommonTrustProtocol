# -*- coding: utf-8 -*-
"""seed_common_556_cards.py · 通识拓展批次556知识卡+题库（幂等）

556：2 张新卡·名著名场面域（水浒经典桥段 kp_card_shuihu_dian /
    西游经典桥段 kp_card_xiyou_dian——id 与语义等价卡名双重确认双零，
    武松/林冲/白骨精等考点全零题）。
预检已过（QB-1900~1902 可用）。
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
    ("kp_card_shuihu_dian",
     "水浒经典桥段",
     "古典文学知识点内容（人话接口）", "艺术学堂",
     "水浒经典桥段——逼上梁山的好汉群像：①**武松打虎**——景阳冈下十"
     "八碗酒壮行，哨棒折断赤手空拳打死吊睛白额虎；②**鲁智深**——拳打"
     "镇关西三拳定恶霸，倒拔垂杨柳震泼皮，禅杖大开大合；③**林冲**——"
     "八十万禁军教头遭陷害，风雪山神庙手刃仇敌，雪夜上梁山；④**智取生"
     "辰纲**——晁盖吴用等在黄泥冈以蒙汗药巧夺不义之财；⑤**聚义**——"
     "一百单八将聚义忠义堂，「替天行道」大旗与招安悲剧结局。",
     ["武松打虎", "鲁智深倒拔垂杨柳", "林冲风雪山神庙",
      "智取生辰纲", "梁山好汉", "替天行道"],
     ["问水浒传", "问西游记"],
     "atomic", "",
     "水浒桥段=武松景阳冈十八碗酒赤手打虎+鲁智深拳打镇关西倒拔垂杨柳+"
     "林冲八十万禁军教头风雪山神庙雪夜上梁山+智取生辰纲黄泥冈蒙汗药+"
     "一百单八将忠义堂替天行道招安悲剧。"),
    ("kp_card_xiyou_dian",
     "西游经典桥段",
     "古典文学知识点内容（人话接口）", "艺术学堂",
     "西游经典桥段——取经路上的九九八十一难：①**大闹天宫**——孙悟空"
     "偷蟠桃盗金丹，炼成火眼金睛，大战二郎神后被压五行山下五百年；②**"
     "三打白骨精**——白骨精三变村姑老翁，唐僧肉眼不辨怒逐悟空，冤情与"
     "忠诚的经典冲突；③**真假美猴王**——六耳猕猴与悟空难辨，谛听不敢"
     "言，如来佛祖辨明真相；④**三借芭蕉扇**——火焰山八百里火焰，悟空"
     "与铁扇公主、牛魔王斗智斗勇；⑤**寓意**——八十一难隐喻修行磨砺，"
     "「敢问路在何方，路在脚下」。",
     ["大闹天宫", "三打白骨精", "真假美猴王",
      "三借芭蕉扇", "火焰山", "八十一难"],
     ["问西游记", "问水浒传"],
     "atomic", "",
     "西游桥段=大闹天宫偷蟠桃火眼金睛压五行山五百年+三打白骨精三变唐"
     "僧怒逐冤情忠诚冲突+真假美猴王六耳猕猴如来辨明+三借芭蕉扇火焰山铁"
     "扇公主牛魔王+八十一难修行磨砺路在脚下。"),
]

QUESTIONS = [
    ("QB-1900", "「武松打虎」和「倒拔垂杨柳」分别是谁的故事？",
     "文学常识", "技术直答",
     ["武松", "鲁智深", "景阳冈", "垂杨柳"], "通识拓展556·新卡"),
    ("QB-1901", "「风雪山神庙」讲的是谁？林冲为什么上梁山？",
     "文学常识", "技术直答",
     ["林冲", "风雪山神庙", "上梁山", "逼上梁山"], "通识拓展556·新卡"),
    ("QB-1902", "「三打白骨精」讲了什么？唐僧为什么赶走孙悟空？",
     "文学常识", "技术直答",
     ["三打白骨精", "白骨精", "唐僧", "孙悟空"], "通识拓展556·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展556"],
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
    bank["version"] = "v8.21"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
