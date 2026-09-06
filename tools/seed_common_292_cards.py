# -*- coding: utf-8 -*-
"""seed_common_292_cards.py · 通识拓展批次292知识卡+题库（幂等）

292：科技-量子通信（墨子号）/历史-九章算术与刘徽
KCCS 四要素+题干原句触发词。预检已过（QB-1104/1105+双id可用）。
注：祖冲之已有 QB-220 避让。
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
             "BCS"}


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
    ("kp_card_quantumcomm",
     "量子通信（墨子号）",
     "科技通识知识点内容（人话接口）", "科技",
     "量子通信为什么「无法窃听」：①**量子密钥分发（QKD）**——用单光子的"
     "偏振/相位态传密钥，量子力学「测量即扰动」——窃听者一旦偷看光子状态"
     "必然留下痕迹，通信双方立即可察觉（窃听可发现而非不可窃听）；②**不可"
     "克隆定理**——未知量子态无法被完美复制，窃听者无法「抄一份再转发」；"
     "③**墨子号**——2016 年发射的世界首颗量子科学实验卫星（命名致敬《墨"
     "经》光学记载），完成星地量子密钥分发/千公里级纠缠分发/量子隐形传态"
     "三项实验；④**京沪干线**——2017 年开通的世界首条量子保密通信骨干网"
     "（2000+ 公里，金融政务专线）；⑤**局限**——QKD 只分发密钥（加密"
     "本体仍是经典算法）、需要专用光纤或卫星链路、距离受衰减限制（可信"
     "中继扩展）；⑥**量子隐形传态**——传的是量子态信息不是物质本身，"
     "「瞬移人」是科幻误读。",
     ["量子通信为什么安全", "墨子号卫星", "量子密钥分发",
      "量子通信能不能超光速", "京沪干线", "量子隐形传态"],
     ["问量子计算", "问后量子密码"],
     "atomic", "",
     "量子通信=QKD单光子态传密钥+测量即扰动窃听必留痕+不可克隆定理+"
     "墨子号2016世界首颗量子卫星(星地密钥/千公里纠缠/隐形传态)+京沪"
     "干线2000km保密网+只发密钥需专线+隐形传态传态非传物。"),
    ("kp_card_jiuzhang",
     "九章算术与刘徽",
     "人文通识知识点内容（人话接口）", "历史",
     "《九章算术》——中国古代数学经典：①**成书**——汉代定型（先秦积累"
     "+汉人整理），246 个应用问题分九章（方田/粟米/衰分/少广/商功/均输/"
     "盈不足/方程/勾股）；②**特点**——算法实用导向（田亩计算/比例换算/"
     "工程土方/税收摊派），「方程术」是世界最早的线性方程组消元法（比欧洲"
     "早一千多年），「正负术」最早引入负数运算；③**刘徽（魏晋）**——"
     "作《九章算术注》：割圆术（圆内接正多边形逼近圆，「割之弥细，所失"
     "弥少」——极限思想雏形）算得 π≈3.1416，还提出出入相补原理；④**"
     "祖冲之父子**——继刘徽之后把 π 精确到 3.1415926-3.1415927 之间"
     "（领先世界约 900 年）；⑤**地位**——与《几何原本》并称两大数学"
     "传统源头：算法化/机械化 vs 公理化/演绎化。",
     ["九章算术是什么书", "九章算术包括哪九章", "刘徽割圆术",
      "中国最早引入负数的书", "线性方程组最早", "九章算术的地位"],
     ["问周髀算经", "问中国古代数学成就"],
     "atomic", "",
     "九章算术=汉定型246问九章(方田粟米衰分少广商功均输盈不足方程勾股)"
     "+方程术最早线性消元正负术最早负数+刘徽注割圆术π≈3.1416极限雏形"
     "+祖冲之π精确到7位领先900年+与几何原本并称两大数学传统。"),
]

QUESTIONS = [
    ("QB-1104", "量子通信为什么安全？墨子号卫星做了什么？", "科技", "技术直答",
     ["量子", "密钥", "窃听", "墨子号"], "通识拓展292"),
    ("QB-1105", "《九章算术》是本什么书？刘徽的割圆术是什么思想？", "历史", "技术直答",
     ["九章算术", "刘徽", "割圆", "方程"], "通识拓展292"),
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
                               "level:L2", "status:verified", "batch:通识拓展292"],
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
    bank["version"] = "v5.63"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
