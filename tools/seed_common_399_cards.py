# -*- coding: utf-8 -*-
"""seed_common_399_cards.py · 通识拓展批次399知识卡+题库（幂等）

399：1 张存量卡补题（家庭电路与安全电压 kp_card_220v，三孔插座角度，
    已在库）+ 2 张新卡（家庭养花 kp_card_gardening / 搬家 kp_card_moving）。
KCCS 四要素+题干原句触发词。预检已过（QB-1435~1437 可用；
耳机打结已有 QB-864/991 排除）。
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
             "MTBF", "SQA", "IMC"}


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
    ("kp_card_gardening",
     "家庭养花入门",
     "生活技能知识点内容（人话接口）", "生活常识",
     "家庭养花——新手也能养活的指南：①**浇水黄金原则**——「见干见湿」："
     "盆土干了再浇、浇就浇透（盆底出水），比定时定量更科学；大多数花"
     "死于浇水太勤——积水烂根是盆栽头号杀手；②**光照分类**——喜阳"
     "植物（月季/茉莉/多肉）放南向窗台，耐阴植物（绿萝/吊兰/虎皮兰）"
     "室内散光即可，绿萝是新手的「练手神器」；③**土壤与施肥**——疏"
     "松透气的营养土，施肥记住「薄肥勤施」（浓肥烧根）；④**黄叶诊断**"
     "——叶黄发软多为水大，叶黄干瘦多为缺水或缺光，先查浇水再看光照；"
     "⑤**上手推荐**——绿萝、吊兰、虎皮兰、多肉，耐旱皮实好恢复。",
     ["家庭养花怎么入门", "花多久浇一次水", "见干见湿是什么",
      "绿萝怎么养", "花叶子发黄怎么办", "新手养什么花"],
     ["问多肉植物", "问园艺工具"],
     "atomic", "",
     "家庭养花=见干见湿干透浇透比定时科学+积水烂根盆栽头号杀手+喜阳"
     "南窗耐阴散光绿萝吊兰虎皮兰练手+疏松营养土薄肥勤施浓肥烧根+黄叶"
     "软是水大干瘦缺水缺光+新手推荐绿萝吊兰虎皮兰多肉。"),
    ("kp_card_moving",
     "搬家全流程",
     "生活技能知识点内容（人话接口）", "生活常识",
     "搬家——一次有序的「项目迁移」：①**搬家前一周**——断舍离减负"
     "（一年没用的东西直接处理）、宽带迁移/地址变更（银行、快递默认"
     "地址）提前办理；②**打包技巧**——分房间分箱并在箱外编号标记"
     "（内容+目标房间）、重物装小箱轻物装大箱、易碎品用衣物毛巾包裹"
     "缓冲、每箱写清单方便核对；③**搬家当天**——贵重物品（证件/首饰"
     "/现金）自己随身带，旧居最后检查水电气是否关闭并拍照留证（读表"
     "数）；④**到新居**——先验水电燃气再让工人卸大件，家具布局想好"
     "再拆包，避免二次搬运；⑤**收拾顺序**——先铺床和卫生间用品（当"
     "晚就要用），厨房和书房可以慢慢来。",
     ["搬家注意事项", "搬家怎么打包", "搬家公司怎么选",
      "搬家先搬什么", "搬家清单", "断舍离"],
     ["问租房", "问收纳"],
     "atomic", "",
     "搬家=提前一周断舍离宽带地址变更+分房间编号标记重物小箱轻物大箱"
     "易碎品衣物缓冲写清单+贵重随身旧居关水电气拍照读表+新居先验水电"
     "再卸大件想好布局再拆包+先铺床和卫生间慢慢收拾其他。"),
]

QUESTIONS = [
    ("QB-1435", "家庭养花浇水有什么原则？花叶子发黄怎么判断原因？",
     "生活常识", "技术直答",
     ["养花", "浇水", "见干见湿", "黄叶"], "通识拓展399"),
    ("QB-1436", "三孔插座的第三个孔是什么？人体的安全电压是多少？",
     "生活常识", "技术直答",
     ["插座", "地线", "安全电压", "火线"], "通识拓展399·存量卡补题"),
    ("QB-1437", "搬家前要做什么准备？打包有什么技巧？",
     "生活常识", "技术直答",
     ["搬家", "打包", "清单", "断舍离"], "通识拓展399"),
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
                               "level:L2", "status:verified", "batch:通识拓展399"],
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
    bank["version"] = "v6.69"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
