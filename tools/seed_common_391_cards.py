# -*- coding: utf-8 -*-
"""seed_common_391_cards.py · 通识拓展批次391知识卡+题库（幂等）

391：1 张存量卡补题（人的一生有两副牙齿 kp_card_teeth，刷牙防蛀角度）
    + 2 张新卡（折纸 kp_card_origami / 剪指甲 kp_card_nailcut）。
KCCS 四要素+题干原句触发词。预检已过（QB-1411~1413 可用，
折纸/剪指甲/刷牙题库 0 覆盖，卡库无同名卡）。
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
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO", "SVM"}


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
    ("kp_card_origami",
     "折纸",
     "手工常识知识点内容（人话接口）", "生活常识",
     "折纸——不裁不剪、只靠折叠把一张纸变成造型的艺术：①**源流**——"
     "纸在中国发明后出现折叠用纸的雏形；折纸在日本发展成成熟的国民艺"
     "术，「千纸鹤」是最著名的形象——折叠千只纸鹤祈愿康复与和平（源于"
     "广岛少女佐佐木祯子的真实故事）；②**现代折纸早已数学化**——折痕"
     "遵循严格的几何公理，复杂造型（昆虫/龙）靠「设计图」预先计算；③**"
     "工程应用**——卫星太阳能板的展开结构、汽车安全气囊的收拢算法、"
     "血管支架，都借鉴了折纸的折叠展开原理；④**教育价值**——锻炼空间"
     "想象与手部精细动作，是最便宜的几何启蒙课。",
     ["折纸的起源", "千纸鹤的含义", "折纸有什么用",
      "折纸与数学", "折纸工程应用", "怎么学折纸"],
     ["问剪纸", "问手工"],
     "atomic", "",
     "折纸=不裁不剪只靠折叠+纸源于中国日本发展成国民艺术+千纸鹤祈愿"
     "康复和平源于广岛少女佐佐木祯子+现代折纸几何公理数学化设计图预"
     "算+太阳能板安全气囊血管支架借鉴折叠原理+空间想象手部精细动作"
     "几何启蒙。"),
    ("kp_card_nailcut",
     "剪指甲",
     "生活卫生知识点内容（人话接口）", "健康与身体",
     "剪指甲——最日常的卫生习惯：①**指甲生长速度**——手指甲每月约长"
     "3 毫米（比脚趾甲快），大约两三周剪一次合适；②**正确剪法**——先"
     "温水泡软（或洗完澡后剪），平着剪、两边留出约 1 毫米白边，两侧不"
     "要剪得太深太圆——剪成「深圆弧」容易长进肉里引发嵌甲和甲沟炎"
     "（脚趾甲尤其常见）；③**工具**——用专用指甲钳，不要用普通剪刀或"
     "用嘴咬（口水和伤口增加感染风险）；④**卫生**——指甲刀不与他人共"
     "用（灰指甲等真菌会通过指甲刀传染），剪完洗手；⑤**婴幼儿**——趁"
     "熟睡时剪，用婴儿专用圆头剪，防抓伤脸。",
     ["指甲多久剪一次", "指甲怎么剪才正确", "甲沟炎怎么预防",
      "嵌甲是什么", "指甲刀能共用吗", "婴儿剪指甲"],
     ["问灰指甲", "问手足护理"],
     "atomic", "",
     "剪指甲=手指甲每月长约3毫米两三周一次+温水泡软平剪留1毫米白边"
     "两侧不剪深圆防嵌甲甲沟炎+专用指甲钳不用嘴咬+指甲刀不共用防真菌"
     "传染剪完洗手+婴儿睡后用圆头剪。"),
]

QUESTIONS = [
    ("QB-1411", "人一生有几副牙齿？怎么刷牙才能预防蛀牙？",
     "健康与身体", "技术直答",
     ["牙齿", "乳牙", "恒牙", "刷牙"], "通识拓展391·存量卡补题"),
    ("QB-1412", "折纸有什么用处？千纸鹤有什么含义？",
     "生活常识", "技术直答",
     ["折纸", "千纸鹤", "数学", "应用"], "通识拓展391"),
    ("QB-1413", "指甲多久剪一次？怎么剪才能避免甲沟炎？",
     "健康与身体", "技术直答",
     ["剪指甲", "甲沟炎", "嵌甲", "指甲钳"], "通识拓展391"),
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
                               "level:L2", "status:verified", "batch:通识拓展391"],
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
    bank["version"] = "v6.61"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
