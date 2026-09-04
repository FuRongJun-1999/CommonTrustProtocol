# -*- coding: utf-8 -*-
"""seed_common_24_cards.py · 通识拓展批次24知识卡+题库（幂等）

24：化学-空气成分/历史-科举制度/生物学-鱼的呼吸/数学-三角形内角和
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_nitrogen",
     "空气的成分",
     "基础科学知识点内容（人话接口）", "化学",
     "空气是混合物，按体积分数：氮气约 78%（含量最多）、氧气约 21%（支持呼吸"
     "与燃烧）、稀有气体（氩氦氖等）约 0.94%、二氧化碳约 0.04%，还有水蒸气等"
     "杂质。含量最多的气体是氮气而非氧气——氮气化学性质稳定，可用作保护气"
     "（食品充氮保鲜/焊接保护）；氧气支持燃烧但本身不可燃；二氧化碳不支持燃"
     "烧、不能供给呼吸，固态干冰用于人工降雨和舞台烟雾。",
     ["空气里含量最多的气体是什么", "空气中氧气占多少", "氮气有什么用途",
      "空气是混合物还是纯净物", "干冰是什么", "二氧化碳支持燃烧吗"],
     ["问稀有气体用途细节", "问空气污染指标"],
     "atomic", "",
     "空气体积分数：氮78%>氧21%>稀有气体0.94%>CO₂0.04%；氮气稳定做保护气；干冰=固态CO₂。"),
    ("kp_card_keju",
     "科举制度",
     "人文通识知识点内容（人话接口）", "历史",
     "科举是中国古代通过分科考试选拔官员的制度：隋炀帝时正式设立进士科（科举"
     "制创立的标志），唐朝完善（武则天首创殿试与武举），明朝鼎盛并发展为「八股"
     "取士」，1905 年清末废除，历时约 1300 年。等级序列（明清）：童试（秀才）→"
     "乡试（举人，第一名解元）→会试（贡士，第一名会元）→殿试（进士，第一名称"
     "「状元」）。意义：打破门第垄断、以才学选官，是现代文官考试制度的先声。",
     ["古代通过考试选拔人才的制度叫什么", "科举制是哪个朝代创立的",
      "状元是什么考试的 第一名", "殿试乡试会试的顺序", "科举制什么时候废除",
      "八股取士是哪个朝代"],
     ["问西方文官制度借鉴", "问具体科场舞弊案"],
     "atomic", "",
     "科举：隋创立(进士科)→唐完善(殿试/武举)→明八股→1905废；明清四级=童试秀才/乡试举人/会试贡士/殿试进士(状元)。"),
    ("kp_card_gill",
     "鱼的呼吸器官",
     "基础科学知识点内容（人话接口）", "生物学",
     "鱼靠鳃呼吸：水从口流入、经过鳃丝流出，鳃丝里密布毛细血管，水中的溶解氧"
     "扩散进入血液、血液中的二氧化碳排出到水中——鱼「喝水」其实是在「呼吸」。"
     "鱼离开水会很快死亡：鳃丝彼此分开、表面积大，在空气中会干燥粘连，无法再"
     "进行气体交换。鱼鳔不是呼吸器官——它主要调节鱼的浮沉（控制密度）。鲸、海"
     "豚是哺乳动物用肺呼吸，必须浮上水面换气，不属于鱼类。",
     ["鱼靠什么器官呼吸", "鱼的鳃是怎么工作的", "鱼离开水为什么会死",
      "鱼鳔的作用是什么", "鲸鱼是鱼吗", "鱼为什么会吐泡泡"],
     ["问两栖动物呼吸", "问鱼侧线感知"],
     "atomic", "",
     "鱼用鳃呼吸：水流经鳃丝(密布毛细血管)换气；离水=鳃丝干燥粘连而死；鱼鳔=调节浮沉非呼吸；鲸豚用肺是哺乳类。"),
    ("kp_card_triangle",
     "三角形内角和与稳定性",
     "基础科学知识点内容（人话接口）", "数学",
     "三角形三个内角的和等于 180°（任意三角形都成立）——已知两个角就能求第三"
     "个角，如两角为 60° 和 70°，则第三角=180−60−70=50°。三角形外角和恒为 "
     "360°。三角形的另一重要性质是稳定性：三边长度确定，形状就唯一确定——这"
     "就是桥梁、屋顶、自行车架用三角形结构的原因；四边形则不具有稳定性（可变"
     "形，如活动衣架），但加上一根斜杆构成两个三角形后就被固定。",
     ["三角形三个内角和是多少", "已知两角求第三角", "三角形外角和是多少",
      "为什么桥梁用三角形结构", "三角形为什么具有稳定性", "四边形不稳定怎么固定"],
     ["问勾股定理", "问相似三角形判定"],
     "atomic", "",
     "三角形内角和=180°(外角和360°)；稳定性=三边定形唯一→桥梁/屋架用三角结构；四边形+斜杆变三角固定。"),
]

QUESTIONS = [
    ("QB-229", "空气里含量最多的气体是什么", "化学", "技术直答",
     ["氮气", "78%"], "通识拓展24"),
    ("QB-230", "古代通过考试选拔人才的制度叫什么", "历史", "技术直答",
     ["科举"], "通识拓展24"),
    ("QB-231", "鱼靠什么器官呼吸", "生物学", "技术直答",
     ["鳃"], "通识拓展24"),
    ("QB-232", "三角形三个内角和是多少", "数学", "技术直答",
     ["180", "180度"], "通识拓展24"),
]


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
                               "level:L2", "status:verified", "batch:通识拓展24"],
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
                   "added": "2026-09-04"})
        added += 1
    bank["version"] = "v1.16"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
