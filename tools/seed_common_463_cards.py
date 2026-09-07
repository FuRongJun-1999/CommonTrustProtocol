# -*- coding: utf-8 -*-
"""seed_common_463_cards.py · 通识拓展批次463知识卡+题库（幂等）

463：2 张新卡（缝扣子 kp_card_sewbutton / 皮鞋保养 kp_card_shoecare）
    + 1 张存量卡补题（铁生锈与防锈 kp_card_rust，已在库）。
生活技能三连。预检已过（QB-1624~1626 可用，
缝扣子/皮鞋保养/铁锈防锈角度题库 0 覆盖）。
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
    ("kp_card_sewbutton",
     "缝扣子",
     "生活技能知识点内容（人话接口）", "生活常识",
     "缝扣子——最实用的手针基本功：①**准备**——针、线（线长约臂展，"
     "太长易打结）、扣子；线头穿针后末端打结；②**四眼扣缝法**——从布"
     "反面入针→对角穿扣子一孔→从另一孔穿回布面，重复 4-6 次；为留出"
     "「线脚」，可在扣子与布料间垫一根牙签再缝；③**收尾打结**——在"
     "布面与扣子之间的线上绕圈打结，剪短线头；④**技巧**——针脚均匀"
     "松紧适度；扣子松了早缝，掉了找回来还能用（缝回原位对齐旧针孔）；"
     "⑤**延伸**——学会平针缝（最基础直线针法）还能缝补开线、改裤"
     "脚，是独立生活的必备技能。",
     ["怎么缝扣子", "四眼扣怎么缝", "缝扣子打结",
      "平针缝", "扣子掉了怎么缝", "手针基本功"],
     ["问缝纫", "问衣物修补"],
     "atomic", "",
     "缝扣子=针线长约臂展末端打结+四眼扣对角穿4到6次扣子下垫牙签留线"
     "脚+收尾绕圈打结剪短线头+针脚均匀松紧适度松了早缝对齐旧针孔+平针"
     "缝可缝补开线改裤脚独立生活技能。"),
    ("kp_card_shoecare",
     "皮鞋保养",
     "生活技能知识点内容（人话接口）", "生活常识",
     "皮鞋保养——穿得久的关键在养护：①**日常护理**——穿完用软布擦去"
     "灰尘污渍，定期上鞋油（同色或无色）：少量均匀打圈涂抹，晾 5 分钟"
     "后用软布或鞋刷抛光；②**防水防潮**——雨天淋湿后塞报纸吸水、自然"
     "阴干，切勿暴晒或烘烤（皮质会变硬开裂）；不穿时用鞋撑（或塞纸团）"
     "定型防皱；③**轮换穿**——同一双皮鞋连续穿会让皮质疲劳，两双"
     "轮换能大幅延长寿命；④**皮质区分**——光面皮用鞋油保养，磨砂/"
     "翻毛皮用专用刷与喷剂，不能上油；⑤**存放**——阴凉干燥通风处，"
     "避免与尖锐物挤压。",
     ["皮鞋怎么保养", "皮鞋上油方法", "皮鞋淋湿了怎么办",
      "鞋撑有什么用", "磨砂皮怎么护理", "皮鞋发霉处理"],
     ["问皮包保养", "问衣物护理"],
     "atomic", "",
     "皮鞋保养=穿完软布除尘定期同色鞋油打圈涂抹5分钟抛光+淋湿塞报纸"
     "阴干勿暴晒烘烤皮质开裂+鞋撑定型防皱两双轮换防皮质疲劳+光面鞋油"
     "磨砂专用刷喷剂不能上油+阴凉干燥通风存放。"),
]

QUESTIONS = [
    ("QB-1624", "怎么缝扣子才牢固？四眼扣的缝法是什么？",
     "生活常识", "技术直答",
     ["缝扣子", "针线", "打结", "针脚"], "通识拓展463"),
    ("QB-1625", "皮鞋怎么保养？皮鞋淋湿后应该怎么处理？",
     "生活常识", "技术直答",
     ["皮鞋", "保养", "鞋油", "阴干"], "通识拓展463"),
    ("QB-1626", "铁为什么会生锈？防止铁制品生锈有哪些方法？",
     "化学基础", "技术直答",
     ["铁锈", "生锈", "氧气", "防锈"], "通识拓展463·存量卡补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展463"],
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
    bank["version"] = "v7.33"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
