# -*- coding: utf-8 -*-
"""seed_common_451_cards.py · 通识拓展批次451知识卡+题库（幂等）

451：2 张新卡（印象派 kp_card_impressionism / 古希腊三大哲学家
    kp_card_greek3，题库卡库双零）+ 1 张存量卡补题
    （美第奇家族与文艺复兴 kp_card_medici，已在库）。
预检已过（QB-1591~1593 可用，三主题题库 0 覆盖）。
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
    ("kp_card_impressionism",
     "印象派",
     "艺术流派知识点内容（人话接口）", "世界文化",
     "印象派——19 世纪下半叶法国的现代艺术开端：①**得名趣事**——1874 年"
     "莫奈的《日出·印象》被批评家嘲讽为「印象主义」，嘲讽反成流派名；"
     "②**艺术主张**——走出画室户外写生，捕捉光与色的瞬间变化，笔触松"
     "散（近看是色块，退后看物象才浮现）；③**代表人物**——"
     "莫奈（《日出·印象》《睡莲》系列）、雷诺阿（人物与光影）、德加"
     "（芭蕾舞女）；之后的「后印象派」三杰：梵高、高更、塞尚——更强调"
     "主观表达，启发了现代艺术；④**意义**——打破学院派陈规，艺术从"
     "「画得像」走向「画得有感受」，现代艺术的大门由此打开。",
     ["印象派怎么得名", "印象派代表画家", "莫奈日出印象",
      "后印象派三杰", "印象派的特点", "现代艺术开端"],
     ["问梵高", "问毕加索"],
     "atomic", "",
     "印象派=1874莫奈日出印象被嘲讽反成流派名+户外写生捕捉光色瞬间笔"
     "触松散近糊远真+莫奈睡莲雷诺阿人物德加舞女+后印象派三杰梵高高更"
     "塞尚重主观表达+打破学院派画得像走向画得有感受现代艺术开端。"),
    ("kp_card_greek3",
     "古希腊三大哲学家",
     "哲学常识知识点内容（人话接口）", "历史与文明",
     "苏格拉底—柏拉图—亚里士多德：西方哲学的师承三连环：①**苏格拉底**"
     "（前469-前399）——「认识你自己」；用问答式「助产术」引导人自己"
     "发现真理；没有留下著作（由弟子柏拉图记录），被雅典法庭判死刑饮"
     "毒芹而亡；②**柏拉图**——苏格拉底弟子，创办学园（西方最早的高等"
     "学府雏形），著《理想国》，主张「理念论」（现实世界是理念世界的"
     "影子）；③**亚里士多德**——柏拉图弟子、亚历山大大帝的老师，百科"
     "全书式学者（逻辑学/物理学/生物学/伦理学/政治学），名言「吾爱吾"
     "师，吾更爱真理」，创立形式逻辑；④**意义**——三代师承奠定西方"
     "哲学与科学传统的根基。",
     ["苏格拉底柏拉图亚里士多德", "古希腊三贤", "认识你自己",
      "理想国", "理念论", "吾爱吾师吾更爱真理"],
     ["问文艺复兴", "问西方哲学"],
     "atomic", "",
     "古希腊三哲=苏格拉底认识你自己问答助产术无著作饮毒芹亡+柏拉图学"
     "园理想国理念论现实是理念影子+亚里士多德柏拉图弟子亚历山大老师百"
     "科全书式形式逻辑吾爱吾师吾更爱真理+三代师承奠定西方哲学科学根基。"),
]

QUESTIONS = [
    ("QB-1591", "印象派是怎么得名的？代表画家有哪些？",
     "世界文化", "技术直答",
     ["印象派", "莫奈", "日出印象", "光色"], "通识拓展451"),
    ("QB-1592", "苏格拉底、柏拉图、亚里士多德是什么关系？各有什么主张？",
     "世界历史", "技术直答",
     ["苏格拉底", "柏拉图", "亚里士多德", "师承"], "通识拓展451"),
    ("QB-1593", "美第奇家族对文艺复兴有什么贡献？",
     "世界历史", "技术直答",
     ["美第奇", "文艺复兴", "赞助", "佛罗伦萨"], "通识拓展451·存量卡补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展451"],
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
    bank["version"] = "v7.22"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
