# -*- coding: utf-8 -*-
"""seed_common_336_cards.py · 通识拓展批次336知识卡+题库（幂等）

336：人体-出汗调节体温/人体-白发的成因
KCCS 四要素+题干原句触发词。预检已过（QB-1247/1248+双新id可用）。
注：kp_card_whitehair 已被占用，改用 kp_card_whitehair2。
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
             "Dijkstra", "Bellman", "Floyd", "logV"}


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
    ("kp_card_sweatcool",
     "出汗与体温调节",
     "人体生理知识点内容（人话接口）", "生活常识",
     "出汗是身体的「空调」：①**原理**——汗腺分泌汗液到皮肤表面，汗液"
     "蒸发吸热带走热量——每蒸发 1 毫升汗约带走 0.58 千卡热量（蒸发散热"
     "是高温环境唯一有效散热途径）；②**为什么湿热天更难受**——空气湿度"
     "大时汗液蒸发不出去（只在身上流），散热效率骤降——「蒸桑拿」感觉；"
     "③**出汗≠排毒**——汗 99% 是水+少量盐与尿素，主要功能是散热，"
     "「排毒」由肝肾负责（出汗多反而要补水补盐）；④**运动出汗与静态"
     "出汗**——运动产热出汗 + 紧张手心出汗（精神性发汗，掌心腋窝为主）；"
     "⑤**异常信号**——夜间盗汗（可能是结核/甲功问题）、半边身出汗、"
     "突然大汗伴胸闷（心梗信号之一）需就医；⑥**补水**——大量出汗补"
     "水同时补电解质（只喝纯水可能「低钠」头晕）。",
     ["出汗的作用", "出汗是排毒吗", "为什么天热会出汗",
      "湿热天出汗更难受", "夜间盗汗", "大量出汗后喝什么"],
     ["问多汗症", "问汗腺分布"],
     "atomic", "",
     "出汗=汗腺分泌汗液蒸发吸热散热(高温唯一有效途径1ml≈0.58千卡)+"
     "湿度大蒸发受阻难受+汗99%水非排毒肝肾司职+紧张精神性手心腋窝汗+"
     "夜间盗汗/半边汗/大汗胸闷就医+大量出汗补电解质。"),
    ("kp_card_whitehair2",
     "白发的成因",
     "人体生理知识点内容（人话接口）", "生活常识",
     "头发为什么会变白：①**原理**——毛囊中的黑色素细胞停止产生黑色素，"
     "新长出的发干无色即白发（不是头发「变」白，是新长的就白）；②**年龄"
     "规律**——通常 30-40 岁起逐渐出现（亚洲人约 40 岁过半数有白发），"
     "与遗传关系最大（父母早白发者大概率也早）；③**加速因素**——长期"
     "压力大（可能通过氧化应激影响毛囊）、B 族维生素缺乏/贫血/甲状腺"
     "疾病、吸烟（研究显示与早白发相关）；④**少年白**——遗传为主，"
     "排除疾病与营养问题后无需过度治疗；⑤**拔一根长三根是无稽之谈**——"
     "毛囊独立工作，拔发不刺激周围变白（但拔发伤毛囊易毛囊炎，不建议）；"
     "⑥**逆转难**——除疾病性白发（治疗后可能恢复）外，自然白发目前无"
     "可靠逆转手段，染发是遮盖方案（选正规产品）。",
     ["白头发是怎么来的", "少年白头发", "白发能变黑吗",
      "拔白头发好不好", "白头发和遗传", "压力大长白发"],
     ["问染发安全", "问黑色素细胞"],
     "atomic", "",
     "白发=毛囊黑色素细胞停止产黑素新发即白(非变白)+30-40岁起遗传关系"
     "最大+压力氧化/B族缺乏/贫血/甲功/吸烟加速+少年白遗传为主无需过度"
     "治+拔一根长三根无稽毛囊独立但拔发伤毛囊+自然白发无可靠逆转染发"
     "遮盖选正规。"),
]

QUESTIONS = [
    ("QB-1247", "人为什么会出汗？出汗能排毒吗？", "生活常识", "技术直答",
     ["散热", "蒸发", "水", "电解质"], "通识拓展336"),
    ("QB-1248", "白头发是怎么长出来的？能变黑吗？", "生活常识", "技术直答",
     ["黑色素", "毛囊", "遗传", "白发"], "通识拓展336"),
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
                               "level:L2", "status:verified", "batch:通识拓展336"],
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
                   "added": "2026-09-06"})
        added += 1
    bank["version"] = "v6.05"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
