# -*- coding: utf-8 -*-
"""seed_common_371_cards.py · 通识拓展批次371知识卡+题库（幂等）

371：天文-引力波/天文-暗物质与暗能量（现代宇宙学新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1335/1336+双id可用）。
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
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO"}


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
    ("kp_card_gravitywave",
     "引力波",
     "天文通识知识点内容（人话接口）", "基础科学",
     "引力波——时空的涟漪：①**是什么**——爱因斯坦广义相对论预言：大质量"
     "天体加速运动（如双黑洞绕转合并）会扰动时空，以光速向外传播涟漪"
     "——时空本身在「震荡」；②**首次探测**——2015 年 9 月美国 LIGO"
     "（激光干涉引力波天文台）直接探测到双黑洞合并产生的引力波（13 亿年"
     "前发出），2017 年诺贝尔物理学奖；③**探测原理**——两条 4 公里长的"
     "垂直激光干涉臂，引力波经过时空间拉伸压缩（变化小于质子直径万分之一"
     "），干涉条纹变化即信号；④**多信使天文学**——2017 年双中子星合并"
     "事件首次同时探测到引力波+电磁对应体（伽马暴），开启「听到又看到」"
     "新时代；⑤**意义**——验证广义相对论、开辟不依赖电磁波的新观测窗口"
     "（可「听」到黑洞合并等不发光事件）。",
     ["引力波是什么", "引力波怎么探测", "LIGO是什么",
      "引力波诺贝尔奖", "双黑洞合并", "时空涟漪"],
     ["问韦布望远镜", "问脉冲星"],
     "atomic", "",
     "引力波=爱因斯坦广义相对论预言时空涟漪+大质量天体加速运动产生以光速"
     "传播+2015年LIGO首次直接探测双黑洞合并13亿年前发出2017诺奖+两条"
     "4公里激光干涉臂变化小于质子直径万分之一+2017双中子星合并引力波加"
     "电磁对应体开启多信使天文学+验证广义相对论开辟新观测窗口。"),
    ("kp_card_darkenergy",
     "暗物质与暗能量",
     "天文通识知识点内容（人话接口）", "基础科学",
     "宇宙的「隐形主角」：①**暗物质**——不发光不吸光但有引力：星系旋转"
     "速度太快（外侧星体本该被甩出去）+引力透镜效应，证明存在大量看不见"
     "的物质——约占宇宙总质能 27%；②**暗能量**——宇宙加速膨胀背后的"
     "「神秘斥力」（1998 年观测超新星发现膨胀在加速），约占 68%——我们"
     "熟悉的普通物质（恒星行星你我）只占约 5%；③**为什么重要**——"
     "「看不见的 95%」决定宇宙的过去与命运（继续膨胀还是收缩）；④**"
     "探测难题**——暗物质不与光作用只留引力痕迹（地下实验室/粒子对撞"
     "机/空间望远镜三路围剿数十年未直接捕获）；⑤**候选理论**——暗物质"
     "粒子（弱相互作用大质量粒子/轴子），暗能量可能是宇宙学常数（爱因斯坦的宇宙学常数"
     "「最大错误」或成先见之明）。",
     ["暗物质是什么", "暗能量是什么", "宇宙由什么组成",
      "暗物质怎么探测", "宇宙加速膨胀", "普通物质占比"],
     ["问中微子", "问宇宙终极命运"],
     "atomic", "",
     "暗物质暗能量=暗物质不发光有引力(星系旋转太快引力透镜证明)占27%"
     "+暗能量宇宙加速膨胀神秘斥力占68%+普通物质仅5%+看不见的95%决定"
     "宇宙命运+地下实验室对撞机空间望远镜三路围剿数十年未直接捕获+"
     "候选弱相互作用大质量粒子轴子暗能量或为宇宙学常数爱因斯坦最大错误或成先见。"),
]

QUESTIONS = [
    ("QB-1335", "引力波是什么？人类是哪一年首次直接探测到引力波的？",
     "基础科学", "技术直答",
     ["引力波", "LIGO", "时空", "2015"], "通识拓展371"),
    ("QB-1336", "暗物质和暗能量分别是什么？宇宙中普通物质占多少？", "基础科学", "技术直答",
     ["暗物质", "暗能量", "27%", "68%"], "通识拓展371"),
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
                               "level:L2", "status:verified", "batch:通识拓展371"],
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
    bank["version"] = "v6.36"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
