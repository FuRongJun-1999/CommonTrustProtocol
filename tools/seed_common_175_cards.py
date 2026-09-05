# -*- coding: utf-8 -*-
"""seed_common_175_cards.py · 通识拓展批次175知识卡+题库（幂等·两卡精批次）

175：生活常识-打鼾与睡眠呼吸暂停/生活常识-衣服为什么会起球
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_snoring",
     "打鼾与睡眠呼吸暂停",
     "生活常识知识点内容（人话接口）", "生活常识",
     "打鼾=睡眠时上呼吸道**狭窄**，气流通过使软腭/悬雍垂（小舌头）等软组织**振"
     "动**发声。加重因素：仰卧（舌根后坠堵住气道——侧睡可缓解）、肥胖（颈部脂"
     "肪挤压气道）、饮酒（酒精松弛肌肉）、鼻塞、疲劳。**危险信号——睡眠呼吸暂"
     "停综合征（OSA）**：鼾声**忽高忽低有停顿**（憋气 10 秒以上）+**憋醒/喘"
     "醒**+白天嗜睡（开车犯困）/晨起头痛口干/注意力差、夜尿多——长期缺氧增加"
     "高血压/心律失常/卒中风险，**不是小事**：需医院**睡眠监测**确诊，治疗=减"
     "重+侧睡+戒酒+口腔矫治器，中重度用 **CPAP 呼吸机**（睡眠时持续正压「撑"
     "开」气道）。单纯均匀轻鼾且无白天症状多为良性。儿童打鼾（腺样体肥大）影"
     "响发育面容（腺样体面容），应及早就诊耳鼻喉科。",
     ["打鼾是什么原因", "睡眠呼吸暂停综合征", "打呼噜需要治疗吗",
      "OSA是什么病", "呼吸机CPAP", "儿童打鼾"],
     ["问睡眠卫生（用睡眠卡）", "问悬雍垂腭咽成形手术"],
     "atomic", "",
     "打鼾=上气道狭窄气流振动软组织：加重=仰卧/肥胖/饮酒/鼻塞；危险信号=鼾声停顿憋气+憋醒+白天嗜睡=OSA 需睡眠监测（长期缺氧伤心血管）；治疗=减重侧睡戒酒+中重度 CPAP 呼吸机；儿童打鼾查腺样体。"),
    ("kp_card_pilling",
     "衣服为什么会起球",
     "生活常识知识点内容（人话接口）", "生活常识",
     "起球=织物表面的**短纤维被摩擦纠缠**成小结（毛球）挂在布面：①**为什么起"
     "**——面料里的**短纤维**（尤其是混入的化纤如涤纶/腈纶）经摩擦被拉出布"
     "面缠成球；化纤强度高**球扯不断就挂在上面**越积越多——所以涤纶混纺最易"
     "「起球不掉」；纯棉羊毛也会起球但棉球脆易脱落（羊毛球还可被面料自磨掉）"
     "——**起球≠质量差**，是纤维特性；②**减少起球**：翻面装入洗衣袋洗、选"
     "柔和洗涤模式、与粗糙衣物（牛仔/带拉链）分开洗、少搓揉；③**已起球处理**"
     "：电动剃毛器/毛球修剪器最有效，别用手硬揪（连根拉出纤维破洞）。④选购"
     "参考：贴身穿想少起球选**长绒棉/精梳棉**（长纤维不易缠），化纤混纺比例"
     "高的（如 65% 涤）更容易球挂。",
     ["衣服起球怎么办", "为什么衣服会起球", "起球是质量问题吗",
      "毛球修剪器", "什么面料不起球"],
     ["问衣物洗涤标识（用洗涤标识卡）", "问面料知识"],
     "atomic", "",
     "起球=短纤维摩擦缠结成球：化纤混纺球强韧挂得住最显眼、棉球脆易掉——起球≠劣质是纤维特性；预防=翻面装袋柔洗/分洗；已起用修剪器勿硬揪；贴身选长绒棉精梳棉少起球。"),
]

QUESTIONS = [
    ("QB-776", "打鼾在什么情况下是「睡眠呼吸暂停综合征」的危险信号？应该怎么治疗？", "生活常识", "技术直答",
     ["停顿", "憋气", "憋醒", "嗜睡", "睡眠监测", "CPAP", "呼吸机"], "通识拓展175"),
    ("QB-777", "衣服为什么会起球？化纤混纺的衣服为什么起球更明显？", "生活常识", "技术直答",
     ["短纤维", "摩擦", "缠结", "涤纶", "修剪器"], "通识拓展175"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    whitelist = {"Havilland", "Maillard", "reaction", "CPAP", "OSA"}
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{6,}", content):
            if word not in whitelist:
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
                               "level:L2", "status:verified", "batch:通识拓展175"],
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
    bank["version"] = "v4.48"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
