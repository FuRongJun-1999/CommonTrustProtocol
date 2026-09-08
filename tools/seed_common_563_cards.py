# -*- coding: utf-8 -*-
"""seed_common_563_cards.py · 通识拓展批次563知识卡+题库（幂等）

563：2 张新卡·时间外贸域（十二时辰 kp_card_shichen /
    市舶司与古代外贸 kp_card_shibosi——id 与语义等价卡名双重确认双零；
    茶马互市 kp_card_teahorse2 已有卡查重跳过）。
预检已过（QB-1921~1923 可用）。
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
    ("kp_card_shichen",
     "十二时辰",
     "传统文化知识点内容（人话接口）", "传统文化",
     "十二时辰——古人的时间刻度：①**划分**——一昼夜十二个时辰，每时"
     "辰两小时，以地支命名：子（23-1 点）丑（1-3）寅（3-5）卯（5-7）辰"
     "（7-9）巳（9-11）午（11-13）未（13-15）申（15-17）酉（17-19）戌"
     "（19-21）亥（21-23）；②**生活用语**——「点卯」：官署卯时查点到"
     "岗（上班打卡的老祖宗）；「半夜三更」：一夜分五更，三更约子时；"
     "「午时三刻」：演义中问斩的时辰（午时阳气最盛）；③**对应动物**"
     "——十二时辰与十二生肖一一对应（子鼠、丑牛……）；④**功用**——"
     "作息、值守、药理（子午觉）皆按此运行，是刻漏、更鼓计时的语言。",
     ["十二时辰", "子时", "点卯", "三更半夜",
      "午时三刻", "时辰对照表"],
     ["问天干地支", "问十二生肖"],
     "atomic", "",
     "十二时辰=一昼夜十二时辰每时辰两小时地支命名子23-1到亥21-23+点卯"
     "官署卯时点到上班打卡老祖宗+半夜三更一夜五更三更约子时+午时三刻阳"
     "气最盛问斩演义+与十二生肖一一对应子鼠丑牛+子午觉刻漏更鼓计时语言"
     "。"),
    ("kp_card_shibosi",
     "市舶司与古代外贸",
     "经济史知识点内容（人话接口）", "历史与文明",
     "市舶司与古代外贸——古代的「海关」：①**设置**——唐代广州已设市"
     "舶使；宋开宝四年（971 年）首设市舶司于广州，后扩至泉州、明州（宁"
     "波）、杭州等；②**职能**——发放公凭（贸易许可证）、抽解（按比例"
     "征收实物税）、博买（官府优先收购番货）、接待管理蕃商；③**泉州**"
     "——宋元时期被誉为「东方第一大港」（刺桐港），马可·波罗与伊本·"
     "白图泰都有记载；④**商品**——出口丝绸瓷器茶叶，进口香料珠宝药材"
     "（「香药」贸易）；⑤**衰落**——明清海禁与朝贡贸易收缩，古代外贸"
     "由盛转管制。",
     ["市舶司", "古代海关", "泉州港", "刺桐港",
      "海上贸易", "抽解"],
     ["问郑和下西洋", "问丝绸之路"],
     "atomic", "",
     "市舶司=唐市舶使宋971首设市舶司广州后泉州明州杭州+发公凭贸易许可"
     "抽解实物税博买官府收购管理蕃商+泉州刺桐港东方第一大港马可波罗伊"
     "本白图泰记载+出口丝绸瓷器茶叶进口香料珠宝+明清海禁朝贡收缩由盛转"
     "管制。"),
]

QUESTIONS = [
    ("QB-1921", "十二时辰怎么划分？「点卯」是什么意思？",
     "传统文化", "技术直答",
     ["十二时辰", "子时", "点卯", "地支"], "通识拓展563·新卡"),
    ("QB-1922", "「半夜三更」的三更是几点？为什么问斩在「午时三刻」？",
     "传统文化", "技术直答",
     ["三更", "午时三刻", "子时", "更点"], "通识拓展563·新卡"),
    ("QB-1923", "市舶司是什么机构？为什么说泉州是东方第一大港？",
     "历史常识", "技术直答",
     ["市舶司", "泉州", "海外贸易", "海关"], "通识拓展563·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展563"],
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
    bank["version"] = "v8.28"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
