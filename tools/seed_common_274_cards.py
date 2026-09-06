# -*- coding: utf-8 -*-
"""seed_common_274_cards.py · 通识拓展批次274知识卡+题库（幂等）

274：机械-齿轮传动的原理/物理-拔河比的是力气吗
KCCS 四要素+题干原句触发词。预检已过（QB-1042/1043+双id可用）。
注：自行车物理已有 QB-409，本批避让。
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
             "FADH2", "Vmax", "Km"}


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
    ("kp_card_gear2",
     "齿轮传动的原理",
     "机械通识知识点内容（人话接口）", "科技",
     "齿轮怎么传递力与速度：①**啮合传动**——两齿轮的齿依次互相咬合推动，"
     "传递动力不打滑（比皮带传动精确可靠）；②**转速与齿数成反比**——大轮"
     "带小轮：大轮转一圈小轮多转几圈（转速加快但力量变小）；小轮带大轮："
     "转速降低但扭矩放大（扭矩与齿数成正比）——**省力就不省速，省速就不"
     "省力**（功率守恒的体现）；③**变速自行车原理**——脚踏链轮换大小档："
     "爬坡换小链轮带大飞轮（扭矩大蹬着轻），平路冲刺换大带小（速度高）；"
     "④**转向**——外啮合两轮转向相反，要同向需中间加惰轮；⑤**应用**——"
     "钟表（齿轮系精确分频走针）、汽车变速箱、机械手表机芯、工厂减速机；"
     "⑥**渐开线齿形**——现代齿轮齿廓多为渐开线，保证传动平稳且对中心距"
     "误差不敏感（工业标准化的智慧）。",
     ["齿轮是怎么传动的", "大齿轮带小齿轮转速怎么变", "变速自行车原理",
      "为什么齿轮省力就不省速", "惰轮是什么", "渐开线齿轮"],
     ["问齿轮加工工艺", "问谐波减速器"],
     "atomic", "",
     "齿轮=啮合不打滑+转速与齿数成反比扭矩与齿数成正比(功率守恒省力不"
     "省速)+变速车大小档换扭矩速度+外啮合反向惰轮同向+钟表变速箱应用+"
     "渐开线齿廓平稳抗中心距误差。"),
    ("kp_card_tugwar",
     "拔河比的是力气吗",
     "物理通识知识点内容（人话接口）", "基础科学",
     "拔河的力学真相：①**核心是摩擦力不是拉力**——两队之间绳子拉力处处"
     "相等（牛顿第三定律+轻绳），决定胜负的是**鞋底与地面的摩擦力**谁能"
     "扛住更大的拉力——拔河其实是「蹬地能力」比赛；②**体重的作用**——"
     "体重大→对地面正压力大→最大静摩擦力大，所以拔河比赛按体重分级/多"
     "上重选手；③**姿势**——身体后倾重心低（把体重「坐」进绳子方向）、"
     "蹬地发力而不是单纯用胳膊拉、全队节奏统一同时发力；④**鞋子**——"
     "鞋底纹路深摩擦系数大的鞋占便宜（专用拔河鞋）；⑤**误区**——「肌肉"
     "大力士队输给平均体重队」不稀奇：技术+摩擦+体重配置 > 局部肌肉力量；"
     "⑥**安全**——勿突然松手（对方集体后仰摔倒风险）、绳子绕手防勒伤。",
     ["拔河获胜靠什么", "拔河比的是力气还是摩擦力", "拔河为什么按体重分",
      "拔河有什么技巧", "拔河身体姿势", "拔河牛顿第三定律"],
     ["问拔河比赛规则", "问摩擦系数测量"],
     "atomic", "",
     "拔河=绳子拉力处处相等胜负在鞋地摩擦力(蹬地能力)+体重正压力大静摩擦"
     "大故按体重分级+后倾低重心蹬地发力队节奏统一+深纹鞋占便宜+技术摩擦"
     "体重配置>肌肉+防松手回弹。"),
]

QUESTIONS = [
    ("QB-1042", "齿轮传动时大轮带小轮转速怎么变？为什么省力就不省速？",
     "科技", "技术直答",
     ["齿数", "转速", "扭矩", "变速"], "通识拓展274"),
    ("QB-1043", "拔河比的是力气还是摩擦力？为什么按体重分组？", "基础科学", "技术直答",
     ["摩擦力", "体重", "蹬地", "拉力"], "通识拓展274"),
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
                               "level:L2", "status:verified", "batch:通识拓展274"],
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
    bank["version"] = "v5.45"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
