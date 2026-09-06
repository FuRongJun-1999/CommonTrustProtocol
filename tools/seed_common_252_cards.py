# -*- coding: utf-8 -*-
"""seed_common_252_cards.py · 通识拓展批次252知识卡+题库（幂等）

252：科技-石英表的原理/人文-算盘与珠算
KCCS 四要素+题干原句触发词。预检已过（QB-947/948+双id可用）。
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
    ("kp_card_quartzwatch",
     "石英表的原理",
     "科技通识知识点内容（人话接口）", "科技",
     "石英表为什么走时准：①**核心=石英晶体压电效应**——给石英晶片通电，"
     "它会以非常稳定的频率振荡（32768 赫兹）——压电效应：电让它振动，振动"
     "又反过来产生电；②**32768 的来头**——32768=2 的 15 次方，芯片用二进制"
     "逐级除 2 分频（分 15 次刚好得到 1 赫兹=每秒一次），驱动步进马达走针；"
     "③**为什么比机械表准**——石英振荡频率稳定度远超游丝摆轮（机械表受"
     "温度/重力/上弦状态影响，日差约 ±30 秒；石英表月差仅 ±15 秒左右）；④"
     "**历史意义**——1969 年日本精工推出世界第一只石英表，引发「石英危机」"
     "重创瑞士机械表业，机械表后来转向奢侈品路线求生；⑤**趣味**——石英"
     "钟表常见「跳秒」走针，正是每秒一次脉冲驱动的痕迹。",
     ["石英表为什么准", "石英表原理", "压电效应是什么",
      "石英表和机械表哪个准", "32768赫兹", "石英危机"],
     ["问原子钟原理", "问机械表机芯工艺"],
     "atomic", "",
     "石英表=石英晶片压电效应32768Hz(2^15)稳定振荡+二进制15次分频到1Hz"
     "驱动步进马达+月差±15秒远准于机械表日差±30秒+1969精工首只石英表"
     "引发石英危机逼瑞士表转奢侈品线。"),
    ("kp_card_abacus2",
     "算盘与珠算",
     "人文通识知识点内容（人话接口）", "历史",
     "算盘——古代计算器：①**结构**——矩形木框穿档，档上串珠：中国算盘"
     "「上 2 珠下 5 珠」（上珠每珠代表 5，下珠每珠代表 1），靠手指拨珠运算；"
     "②**为什么上 2 下 5**——一档可表 0-15，不单为十进制：旧制「一斤十六"
     "两」（十六进制斤两换算）直接在同档完成，这是中国算盘的独门设计；③"
     "**运算靠口诀**——加减「三下五除二」乘除「九九归除」口诀化，熟练者"
     "看数字直接拨珠不假思索；④**性能惊人**——1980 年代计算器普及前，"
     "珠算熟手加减运算速度可与早期电动计算器打平（1946 年里德vs 盟军计算"
     "员项斯身的著名对决常被引为算盘高光）；⑤**文化地位**——珠算 2013 年"
     "入选联合国非遗；「三下五除二」「打小算盘」等成语皆源于珠算；⑥日本"
     "日本算盘上 1 下 4 为十进制纯化版，俄国算珠横置算盘形异理同。",
     ["算盘怎么用", "算盘为什么上2下5", "珠算是什么", "算盘是谁发明的",
      "一斤十六两和算盘", "珠算非遗"],
     ["问算盘教学", "问计算器发展史"],
     "atomic", "",
     "算盘=框档串珠(中国式上2下5一档可表0-15)适应旧制一斤十六两十六进制"
     "+口诀化运算(三下五除二)+加减速度曾比肩电动计算器+珠算2013年联合国"
     "非遗+日式上1下4纯十进制变体。"),
]

QUESTIONS = [
    ("QB-947", "石英表为什么比机械表走时准？它的原理是什么？", "科技", "技术直答",
     ["石英", "压电", "32768", "振荡"], "通识拓展252"),
    ("QB-948", "算盘为什么设计成上2珠下5珠？珠算有什么特点？", "历史", "技术直答",
     ["算盘", "十六两", "口诀", "非遗"], "通识拓展252"),
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
                               "level:L2", "status:verified", "batch:通识拓展252"],
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
    bank["version"] = "v5.23"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
