# -*- coding: utf-8 -*-
"""seed_common_435_cards.py · 通识拓展批次435知识卡+题库（幂等）

435：2 张新卡（亚马逊雨林 kp_card_amazon / 东非大裂谷 kp_card_rift，
    题库卡库双零）+ 1 张存量卡补题（海水为什么是咸的 kp_card_seawater
    死海浮力角度，已在库）。
世界地理三连。预检已过（QB-1543~1545 可用，死海角度题库 0 覆盖）。
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
    ("kp_card_amazon",
     "亚马逊雨林",
     "世界地理知识点内容（人话接口）", "自然常识",
     "亚马逊雨林——「地球之肺」与物种宝库：①**规模**——世界最大的热带"
     "雨林（约 500 万平方公里，横跨南美九国），亚马逊河是世界流量最大"
     "的河流（约占全球入海淡水的五分之一）；②**为什么重要**——固碳释"
     "氧调节全球气候；物种密度全球第一（数百万种昆虫、数千种鸟类和鱼"
     "类，很多物种尚未被科学描述）；③**威胁**——砍伐与烧荒（雨林土壤"
     "薄，毁林开垦后很难恢复，存在雨林变稀树草原的不可逆风险）；④**"
     "保护**——巴西等国的卫星监测与保护区体系、国际碳中和合作（保护"
     "雨林已成为全球气候议题）；⑤**人文**——雨林中生活着众多原住民"
     "部落，他们是雨林知识的活图书馆。",
     ["亚马逊雨林在哪", "地球之肺是什么", "亚马逊河",
      "雨林为什么重要", "雨林砍伐的危害", "生物多样性"],
     ["问非洲草原", "问气候变化"],
     "atomic", "",
     "亚马逊雨林=世界最大热带雨林约500万平方公里横跨南美九国+亚马逊河"
     "流量全球第一约占五分之一+固碳释氧调节气候物种密度全球第一数百万"
     "种+砍伐烧荒土壤薄难恢复雨林变草原不可逆风险+卫星监测保护区国际"
     "碳中和合作+原住民部落雨林知识活图书馆。"),
    ("kp_card_rift",
     "东非大裂谷",
     "世界地理知识点内容（人话接口）", "自然常识",
     "东非大裂谷——「地球最大的伤疤」：①**规模**——世界最长的裂谷带，"
     "全长约 6000 公里，从红海沿岸延伸到莫桑比克；②**怎么形成**——非"
     "洲板块内部的地幔上涌拉伸地壳，岩层断裂下陷形成巨大谷地（不是被"
     "河水冲出来的）；③**裂谷景观**——串珠状的裂谷湖群（坦噶尼喀湖是"
     "世界第二深的湖）、活火山（维龙加火山群）；④**人类摇篮**——东非"
     "大裂谷出土了大量古人类化石（「露西」、图尔卡纳男孩等），是人类"
     "起源研究的核心地区；⑤**未来**——板块仍在张裂（每年几毫米），"
     "亿万年之后这里可能裂开成新的海洋。",
     ["东非大裂谷是怎么形成的", "东非大裂谷有多长",
      "地球伤疤", "坦噶尼喀湖", "人类摇篮", "露西化石"],
     ["问板块运动", "问火山"],
     "atomic", "",
     "东非大裂谷=世界最长裂谷带约6000公里红海到莫桑比克地球伤疤+非洲"
     "板块内部地幔上涌拉伸地壳断裂下陷形成非河流冲刷+坦噶尼喀湖世界第"
     "二深维龙加火山+露西图尔卡纳男孩古人类化石人类摇篮+板块张裂每年"
     "数毫米亿年后或成新海洋。"),
]

QUESTIONS = [
    ("QB-1543", "亚马逊雨林为什么被称为「地球之肺」？它面临什么威胁？",
     "自然常识", "技术直答",
     ["亚马逊", "雨林", "地球之肺", "砍伐"], "通识拓展435"),
    ("QB-1544", "东非大裂谷是怎么形成的？它有哪些世界之最？",
     "自然常识", "技术直答",
     ["东非大裂谷", "板块", "裂谷", "人类摇篮"], "通识拓展435"),
    ("QB-1545", "死海为什么淹不死人？死海真的是海吗？",
     "自然常识", "技术直答",
     ["死海", "浮力", "盐度", "咸水湖"], "通识拓展435·存量卡补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展435"],
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
    bank["version"] = "v7.06"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
