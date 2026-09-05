# -*- coding: utf-8 -*-
"""seed_common_199_cards.py · 通识拓展批次199知识卡+题库（幂等·两卡精批次）

199：生活常识-菠萝为什么「扎嘴」/生活技能-不干胶胶痕怎么去除
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖（taiwan/linzexu 卡
仅「菠萝」「盐水」词提及）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_pineapple",
     "菠萝为什么「扎嘴」",
     "基础科学知识点内容（人话接口）", "化学",
     "吃菠萝「扎嘴/涩/舌头刺痛」=**菠萝蛋白酶在消化你**：①菠萝含**菠萝蛋白**"
     "酶**，会分解口腔黏膜与舌头表面的**蛋白质**——「吃菠萝的同时菠萝也在吃"
     "你」（轻微的蛋白质水解刺激，非过敏的刺麻感）；②**真正的过敏**是另一回"
     "事（少数人菠萝过敏起疹/口腔肿胀，需避免）。**减轻扎嘴**：①**盐水泡**——"
     "盐水抑制酶活性+溶出部分刺激物（传统做法，但效果有限）；②**加热最有效"
     "**——60°C 以上蛋白酶变性失活（菠萝咕咾肉/菠萝饭/烤菠萝不扎嘴）；③选"
     "「金钻凤梨」（甜蜜蜜菠萝）品种——蛋白酶含量低，可直接吃不扎嘴。营养"
     "点：菠萝富含维生素 C 与**菠萝蛋白酶助消化**（餐后吃比空腹吃不刺激）。",
     ["菠萝为什么扎嘴", "吃菠萝舌头刺痛", "菠萝要用盐水泡吗",
      "菠萝蛋白酶", "凤梨和菠萝的区别"],
     ["问辣椒为什么辣（用辣椒卡）", "问芒果过敏"],
     "atomic", "",
     "菠萝扎嘴=菠萝蛋白酶分解口腔黏膜蛋白（「菠萝也吃你」非过敏）；盐水泡效果有限、加热 60°C+ 酶变性最有效（咕咾肉不扎嘴）、低蛋白酶品种凤梨可直接吃；真过敏起疹肿胀需避免；餐后吃不空腹。"),
    ("kp_card_glueremove",
     "不干胶胶痕怎么去除",
     "生活常识知识点内容（人话接口）", "生活常识",
     "标签撕掉后的胶痕去除思路=**让胶「溶」或「软」**（不干胶是有机高分子，"
     "相似相溶）：①**有机溶剂浸润**——风油精/酒精/食用油/护手霜涂在胶痕上"
     "**静置 1-2 分钟软化**，再以布或旧卡片刮除（食用油最安全，塑料面也适"
     "用）；②**加热软化**——吹风机热风吹 30 秒，胶变软即可撕（玻璃/陶瓷适"
     "用；塑料怕热慎用）；③**专用除胶剂**（含溶剂更强力）。**注意**：喷漆家"
     "具/皮革面先用边角试（溶剂可能溶漆）；塑料面忌用刀片硬刮（留划痕）；擦"
     "完用洗洁精去油。汽车贴膜残胶同理：先加热后用除胶剂。",
     ["不干胶怎么去除", "标签胶痕怎么清理", "风油精去胶",
      "玻璃上的贴纸怎么撕干净", "除胶剂"],
     ["问过热液体（物理安全）", "问清洁剂混用"],
     "atomic", "",
     "胶痕去除=相似相溶思路：风油精/酒精/食用油浸润 1-2 分钟软化后刮除（油最安全）+吹风机加热软化（塑料慎热）+专用除胶剂；喷漆/皮革先试勿刀刮；擦完洗洁精去油。"),
]

QUESTIONS = [
    ("QB-826", "吃菠萝为什么会有「扎嘴」的刺痛感？怎么吃菠萝不扎嘴？", "化学", "技术直答",
     ["菠萝蛋白酶", "分解", "蛋白质", "盐水", "加热", "凤梨"], "通识拓展199"),
    ("QB-827", "瓶子上的不干胶标签撕掉后胶痕怎么去除？塑料表面要注意什么？", "生活常识", "技术直答",
     ["风油精", "酒精", "食用油", "软化", "吹风机", "刮"], "通识拓展199"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{6,}", content):
            problems.append((node[0], f"长英文词: {word}"))
    if problems:
        raise SystemExit(f"外文长词检测报警: {problems}")


def ensure_seed() -> dict:
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
                               "level:L2", "status:verified", "batch:通识拓展199"],
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

    bank = json.load(open(BANK, encoding="utf-8"))
    qs = bank["questions"]
    have = {q["id"] for q in qs}
    added = 0
    for qid, question, domain, qtype, keywords, source in QUESTIONS:
        if qid in have:
            continue
        qs.append({"id": qid, "question": question, "domain": domain,
                   "type": qtype, "keywords": keywords, "source": source,
                   "added": "2026-09-05"})
        added += 1
    bank["version"] = "v4.72"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
