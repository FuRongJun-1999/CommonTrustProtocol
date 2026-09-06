# -*- coding: utf-8 -*-
"""seed_common_298_cards.py · 通识拓展批次298知识卡+题库（幂等）

298：科学史-日心说革命/科学史-进化论（科学史新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1125/1126+双id可用）。
注：牛顿三定律已有 QB-097/912/1007，本批避让取科学史视角。
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
    ("kp_card_copernicus",
     "日心说革命",
     "科学史知识点内容（人话接口）", "历史",
     "从地心到日心：①**地心说**——托勒密体系（本轮/均轮修补），符合直觉与"
     "教会宇宙观，统治西方近 1400 年；②**哥白尼**——1543 年临终出版"
     "《天体运行论》提出日心说（地球只是绕日行星之一），「哥白尼革命」"
     "拉开近代科学序幕——把人从宇宙中心拉下；③**接力**——第谷精确观测"
     "数据→开普勒三定律（椭圆轨道颠覆正圆信仰）→伽利略望远镜实证（木星"
     "卫星证明并非万物绕地球/金星相位证明绕日），因支持日心说受宗教裁判；"
     "④**牛顿收口**——万有引力定律统一解释天体与地面运动，日心说获得"
     "力学根基；⑤**哲学意义**——天界与地界的界限被打破（同一套物理规律"
     "统治宇宙），实验+数学+观测的方法论范式确立；⑥**布鲁诺**——因宣扬"
     "宇宙无限等思想被烧死，科学自由史上的标志性悲剧。",
     ["日心说是谁提出的", "哥白尼革命", "伽利略为什么受审",
      "开普勒三定律", "日心说怎么被证实的", "布鲁诺为什么被烧死"],
     ["问第谷观测", "问宗教与科学史"],
     "atomic", "",
     "日心说=托勒密地心统治1400年→哥白尼1543天体运行论临终出版→第谷"
     "数据开普勒椭圆定律伽利略望远镜实证(木卫金星相位)受审→牛顿万有引力"
     "收口+天界地界同一套规律+实验数学观测范式确立+布鲁诺悲剧。"),
    ("kp_card_evolution",
     "进化论",
     "科学史知识点内容（人话接口）", "基础科学",
     "达尔文进化论核心：①**环球考察**——贝格尔号五年航行（加拉帕戈斯"
     "群岛地雀喙形差异的启发），1859 年出版《物种起源》；②**两大机制**——"
     "变异（个体差异普遍存在）+自然选择（适者生存：适应环境的个体留下"
     "更多后代，有利性状逐代累积）；③**共同祖先**——所有生命彼此相关，"
     "人与黑猩猩有共同祖先而非「人是猴子变的」；④**进化没有方向**——"
     "不是「越来越高级」，只是适应当下环境（细菌比人类更「成功」——存在"
     "时间与生物量）；⑤**证据链**——化石过渡类型（始祖鸟）/比较解剖学"
     "（同源器官：人臂与鲸鳍同构）/分子生物学（DNA 序列相似度与亲缘一致"
     "——最强现代证据）/定向选择实证（抗生素耐药菌演化）；⑥**常见误读**"
     "——「社会达尔文主义」把自然规律错误搬到人类社会伦理，达尔文本人"
     "并未主张；拉马克「用进废退」获得性遗传在多数情形被否定（表观遗传学"
     "是有限的修正而非推翻）。",
     ["进化论是谁提出的", "自然选择是什么意思", "人是猴子变的吗",
      "进化有方向吗", "抗生素耐药和进化论", "用进废退对吗"],
     ["问遗传算法", "问人类演化史"],
     "atomic", "",
     "进化论=达尔文贝格尔号五年加拉帕戈斯地雀启发1859物种起源+变异+自然"
     "选择适者生存逐代累积+共同祖先(人非猴变)+进化无方向只适应环境+证据"
     "化石同源器官DNA相似度耐药菌实证+社会达尔文主义误读+用进废退多数"
     "被否定。"),
]

QUESTIONS = [
    ("QB-1125", "日心说是谁提出的？伽利略为什么受到教会审判？", "历史", "技术直答",
     ["哥白尼", "日心说", "伽利略", "望远镜"], "通识拓展298"),
    ("QB-1126", "进化论的核心机制是什么？人是猴子变的吗？", "基础科学", "技术直答",
     ["达尔文", "自然选择", "共同祖先", "变异"], "通识拓展298"),
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
                               "level:L2", "status:verified", "batch:通识拓展298"],
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
    bank["version"] = "v5.69"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
