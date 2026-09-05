# -*- coding: utf-8 -*-
"""seed_common_240_cards.py · 通识拓展批次240（混合批次·幂等）

240：①新卡 kp_card_fiber_optic 光纤通信原理 + QB-905
     ②新卡 kp_card_qin_unify 秦始皇统一度量衡 + QB-906
     ③存量卡补题 诸子散文 + QB-907
     ④存量卡补题 约束与自由度 + QB-908
预检已过（QB-905~908+新卡id可用）。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

WHITELIST = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
             "effect", "OR6A2", "ghrelin", "DOMS", "DHT", "frisson"}


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
    ("kp_card_fiber_optic",
     "光纤通信的原理",
     "科技通识知识点内容（人话接口）", "科技",
     "光纤通信原理：①**核心=光的全反射**——光纤由纤芯（折射率高）和包层"
     "（折射率低）构成，光从纤芯射向包层界面时入射角大于临界角就全部反射回"
     "纤芯，像光在管子里不断弹墙前进，损耗极小，传数百公里也无需太多"
     "太多；②**为什么用光**——光的频率远高于无线电波，可携带的信息带宽大"
     "几个数量级，一根头发丝粗的光纤理论上可同时传数十万人通话；③**信号"
     "转换**——电信号→激光二极管转成光脉冲→光纤传输→接收端光电二极管转回"
     "电信号；④**优势**——抗电磁干扰（光不走电流，雷电/高压线旁边照样稳）"
     "+保密性强（光被包裹在纤芯里不外泄，难窃听）+重量轻损耗低；⑤**中继**"
     "——跨洋海底光缆靠掺铒光纤放大器直接在光域放大信号。",
     ["光纤通信是什么原理", "光为什么能在光纤里传播", "光纤为什么快",
      "全反射是什么", "海底光缆怎么工作", "光纤抗干扰吗"],
     ["问光纤制造工艺", "问无线通信对比"],
     "atomic", "",
     "光纤=纤芯全反射弹墙前进(纤芯折射率>包层)+光频高带宽大(一根丝数十万"
     "路通话)+电→光→电转换+抗电磁干扰/保密/轻+海底光缆掺铒放大。"),
    ("kp_card_qin_unify",
     "秦始皇统一度量衡",
     "人文通识知识点内容（人话接口）", "历史",
     "秦始皇统一度量衡：①**背景**——战国七雄各搞一套：长度/容量/重量单位"
     "不一（齐国以釜、秦国以斛），钱币形状各异（布币/刀币/圜钱），文字异形"
     "（同一个字七国七种写法），跨国贸易要反复换算；②**统一内容**——前 221"
     " 年灭六国后，以秦制为准：度量衡（度=长度/量=容积/衡=重量）+圆形方孔"
     "「半两」钱通行全国+小篆为标准文字（书同文）+车轨间距统一（车同轨）；"
     "③**意义**——全国市场结算成本骤降，政令文书无碍通行，是中央集权国家"
     "治理的技术底座；后世两千多年「圆形方孔钱」形制沿用至清末，郡县制+"
     "统一文字让中国「分久必合」有了文化粘合剂；④**配套**——修驰道直道"
     "（高速公路网）统一车距，商业与军事调度效率倍增。",
     ["秦始皇统一度量衡是什么意思", "书同文车同轨是谁",
      "为什么统一度量衡很重要", "半两钱是什么", "秦始皇统一了什么"],
     ["问秦朝官制细节", "问各国货币形制对比"],
     "atomic", "",
     "秦统一度量衡=前221年以秦制准（度量衡+圆形方孔半两钱+小篆书同文+车"
     "同轨+驰道）→跨贸结算/政令通行成本骤降=中央集权技术底座+钱形制沿用"
     "两千年+书同文=文化粘合剂。"),
]

QUESTIONS = [
    ("QB-905", "光纤通信的原理是什么？光为什么能在光纤里传播？", "科技", "技术直答",
     ["全反射", "纤芯", "包层", "折射率"], "通识拓展240"),
    ("QB-906", "秦始皇统一度量衡具体统一了什么？有什么历史意义？", "历史", "技术直答",
     ["度量衡", "半两钱", "书同文", "车同轨"], "通识拓展240"),
    ("QB-907", "先秦诸子散文有哪些代表作品？各有什么风格特点？", "文学", "学科直答",
     ["论语", "孟子", "庄子", "语录体", "寓言"], "通识拓展240·存量卡补题"),
    ("QB-908", "什么是约束与自由度？自由度如何计算？", "物理", "学科直答",
     ["约束", "自由度", "独立坐标"], "通识拓展240·存量卡补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展240"],
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
    bank["version"] = "v5.11"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
