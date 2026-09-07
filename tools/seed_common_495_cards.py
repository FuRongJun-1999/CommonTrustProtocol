# -*- coding: utf-8 -*-
"""seed_common_495_cards.py · 通识拓展批次495知识卡+题库（幂等）

495：2 张新卡 + 1 张存量卡补题——石窟双绝 + 园林
    （龙门石窟 kp_card_longmen / 云冈石窟 kp_card_yungang 新卡，
    苏州园林 kp_card_suzhougarden 存量补题）。
预检已过（QB-1717~1719 可用，龙门/云冈卡库无独立卡、题库零覆盖）。
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
    ("kp_card_longmen",
     "龙门石窟",
     "考古常识知识点内容（人话接口）", "历史与文明",
     "龙门石窟——河南洛阳的石刻艺术宝库：①**位置**——伊水两岸的龙门"
     "山与香山之间，古称「伊阙」，两山对峙如门阙；②**开凿**——始于"
     "北魏孝文帝迁都洛阳（约 493 年）前后，营造延续 400 余年至唐代，"
     "现存窟龛 2300 余个、造像近 11 万尊；③**镇窟之宝**——奉先寺卢"
     "舍那大佛：通高 17.14 米，面容丰腴安详，相传以武则天形象为参照，"
     "是唐代雕塑艺术的巅峰；④**北魏名窟**——古阳洞（开凿最早）、宾阳"
     "中洞；⑤**地位**——2000 年列入世界文化遗产，与莫高窟、云冈石窟"
     "、麦积山石窟并称中国四大石窟。",
     ["龙门石窟在哪里", "卢舍那大佛", "龙门石窟是哪个朝代",
      "奉先寺", "四大石窟", "伊阙"],
     ["问云冈石窟", "问乐山大佛"],
     "atomic", "",
     "龙门石窟=河南洛阳伊水两岸龙门山香山古称伊阙+北魏孝文帝迁都洛阳"
     "约493年始凿延续400余年窟龛2300余造像近11万尊+奉先寺卢舍那大佛17."
     "14米相传以武则天为参照唐代雕塑巅峰+古阳洞宾阳中洞北魏名窟+2000"
     "年世界遗产四大石窟之一。"),
    ("kp_card_yungang",
     "云冈石窟",
     "考古常识知识点内容（人话接口）", "历史与文明",
     "云冈石窟——山西大同的北魏皇家石窟：①**位置**——大同城西武周山"
     "南麓，北魏都城平城（今大同）近郊；②**开凿**——北魏文成帝和平"
     "初年（5 世纪中叶）由高僧昙曜主持开凿「昙曜五窟」（第 16-20 窟"
     "），是皇家工程的开端；③**标志**——第 20 窟露天大佛（释迦坐像"
     "高 13.7 米），双肩齐挺、深目高鼻，气势雄浑，是云冈的形象代表"
     "；④**风格**——早期造像融合西域与中原风格（可见犍陀罗艺术影响"
     "），晚期逐渐汉化「秀骨清像」；⑤**地位**——现存主要洞窟 45 个"
     "，造像 5.9 万余尊，2001 年列入世界文化遗产。",
     ["云冈石窟在哪里", "昙曜五窟", "云冈石窟是哪个朝代",
      "第20窟大佛", "大同石窟", "犍陀罗风格"],
     ["问龙门石窟", "问莫高窟"],
     "atomic", "",
     "云冈石窟=山西大同武周山南麓北魏平城近郊+北魏和平初年昙曜主持开"
     "凿昙曜五窟第16到20窟皇家工程开端+第20窟露天大佛13.7米深目高鼻"
     "气势雄浑形象代表+早期融合西域中原风格可见犍陀罗影响晚期秀骨清像"
     "汉化+45个主要洞窟5.9万余尊2001年世界遗产。"),
]

QUESTIONS = [
    ("QB-1717", "龙门石窟在哪里？卢舍那大佛有什么特点？",
     "历史常识", "技术直答",
     ["龙门石窟", "卢舍那", "洛阳", "奉先寺"], "通识拓展495·新卡"),
    ("QB-1718", "云冈石窟是哪个朝代开凿的？昙曜五窟是什么？",
     "历史常识", "技术直答",
     ["云冈石窟", "北魏", "昙曜", "大同"], "通识拓展495·新卡"),
    ("QB-1719", "苏州园林有哪些代表？造园手法上有什么讲究？",
     "传统文化", "技术直答",
     ["拙政园", "借景", "苏州园林", "世界遗产"], "通识拓展495·存量卡补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展495"],
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
    bank["version"] = "v7.60"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
