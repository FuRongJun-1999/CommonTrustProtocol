# -*- coding: utf-8 -*-
"""seed_common_290_cards.py · 通识拓展批次290知识卡+题库（幂等）

290：运动-潜水的耳压平衡/运动-减压病与安全上浮（潜水运动新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1097/1098+双id可用）。
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
    ("kp_card_diving",
     "潜水的耳压平衡",
     "运动科学知识点内容（人话接口）", "生活常识",
     "潜水为什么耳朵疼：①**原理**——下潜每 10 米增加一个大气压，中耳是"
     "封闭气腔，外界水压压鼓膜向内——压差大则剧痛甚至鼓膜破裂；②**平衡"
     "技术（下潜全程主动做）**——捏鼻鼓气（瓦尔萨尔瓦动作，轻缓勿猛）/"
     "吞咽打哈欠（主动开放咽鼓管）——稍有痛感应上浮少许重做，**强忍下潜"
     "最危险**；③**感冒鼻塞勿潜水**——咽鼓管堵塞平衡不了耳压，且鼻窦"
     "同样受压（上浮时反向阻塞剧痛更烈）；④**面镜挤压**——"
     "下潜面镜内也成负压，用鼻子向面镜呼气平衡；⑤**耳压失衡的伤**——"
     "鼓膜充血/破裂（进水眩晕）/气压伤，恢复前勿再下水。",
     ["潜水为什么耳朵疼", "耳压平衡怎么做", "捏鼻鼓气",
      "感冒能潜水吗", "潜水耳痛怎么办", "咽鼓管"],
     ["问自由潜训练", "问潜水证照体系"],
     "atomic", "",
     "耳压=每10米增一大气压中耳封闭气腔受压+捏鼻鼓气吞咽开放咽鼓管全程"
     "主动做+痛感上浮重做强忍最危险+感冒鼻塞勿潜(咽鼓管堵+反向阻塞)+"
     "面镜鼻呼气平衡+破裂眩晕就医。"),
    ("kp_card_bends",
     "减压病与安全上浮",
     "运动科学知识点内容（人话接口）", "生活常识",
     "潜水减压病为什么可怕：①**成因**——高压下氮气大量溶入血液组织"
     "（亨利定律），上浮过快时氮气来不及排出直接在体内「汽化」成气泡——"
     "堵在关节剧痛（业内俗称「弯折症」）堵在肺脑脊髓则瘫痪致命；②"
     "**安全上浮**——控制上升速度（约 9-18 米/分钟）+在安全停留点（5 米"
     "停 3 分钟）让氮气缓缓排出——电脑表/潜导盯深度时间；③**禁忌**——"
     "潜水后 12-18 小时内勿乘飞机/上高原（环境再降压=二次减压病风险）；"
     "④**治疗**——高压氧舱再加压复溶气泡+逐段减压（越早越好）；⑤**氮醉"
     "**——30 米以下氮气的麻醉效应（像醉酒判断力下降），深潜危险之一；"
     "⑥**预防三件套**——按计划深度时间潜水/留余量（残压 50 bar 上浮）/"
     "结伴制（潜伴互检）。",
     ["什么是减压病", "潜水为什么不能快速上浮",
      "潜水后多久能坐飞机", "氮醉是什么", "安全停留", "减压病怎么治疗"],
     ["问饱和潜水", "问潜水医学"],
     "atomic", "",
     "减压病=高压溶氮上浮过快体内汽化成气泡(关节痛/肺脑栓塞致命)+上浮"
     "9-18米每分+5米停3分钟安全停留+潜水后12-18小时勿乘机高原+高压氧舱"
     "再加压治疗+氮醉30米下麻醉+残压50bar结伴制。"),
]

QUESTIONS = [
    ("QB-1097", "潜水时耳朵疼怎么办？耳压平衡的正确做法是什么？", "生活常识", "技术直答",
     ["耳压", "咽鼓管", "捏鼻鼓气", "上浮"], "通识拓展290"),
    ("QB-1098", "什么是减压病？为什么潜水后不能马上坐飞机？", "生活常识", "技术直答",
     ["减压病", "氮气", "上浮", "飞机"], "通识拓展290"),
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
                               "level:L2", "status:verified", "batch:通识拓展290"],
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
    bank["version"] = "v5.61"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
