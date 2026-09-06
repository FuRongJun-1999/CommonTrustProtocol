# -*- coding: utf-8 -*-
"""seed_common_346_cards.py · 通识拓展批次346知识卡+题库（幂等）

346：非遗-木版年画/工艺-青花瓷（非遗手工艺新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1277/1278+双id可用）。
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
             "Dijkstra", "Bellman", "Floyd", "logV"}


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
    ("kp_card_nianhua2",
     "木版年画",
     "非遗艺术知识点内容（人话接口）", "文化",
     "木版年画——刻在木板上的年味：①**工艺**——画稿→雕版（梨木/杜木"
     "刻版）→套色印刷（一版一色，多至五六色套印）——一张年画需数块版"
     "反复套印；②**四大产地**——天津杨柳青（细腻半印半绘）、苏州桃花"
     "坞、河南朱仙镇（古朴夸张）、山东潍坊杨家埠（粗犷鲜艳）；③**题材"
     "**——门神（秦琼尉迟恭）/灶王/娃娃胖（连年有余胖娃娃抱鱼）/戏曲"
     "故事——承载祈福禳灾的年俗期待；④**寓意体系**——谐音（蝙蝠=福/"
     "鸡=吉/莲=连）、象征（石榴多子/桃长寿）与年画结合成「图必有意，意"
     "必吉祥」；⑤**节令**——腊月上市贴年画是旧时过年重要仪式，与春联"
     "窗花共同构成年俗视觉系统；⑥**当代**——国家级非遗，杨柳青与潍坊"
     "年画进校园传承。",
     ["木版年画是什么", "杨柳青年画", "年画的产地",
      "年画题材有什么", "门神年画", "套色印刷"],
     ["问潍坊风筝", "问民间美术"],
     "atomic", "",
     "年画=画稿雕版梨木刻版一版一色多色套印+四大产地杨柳青细腻桃花坞"
     "朱仙镇古朴杨家埠粗犷+题材门神灶王胖娃娃戏曲+谐音象征图必有意意"
     "必吉祥+腊月贴年画年俗仪式+国家级非遗进校园。"),
    ("kp_card_blueporc2",
     "青花瓷",
     "工艺通识知识点内容（人话接口）", "文化",
     "青花瓷为什么是「中国名片」：①**工艺**——以钴料在瓷胎上绘图案，"
     "罩透明釉高温（约1300°C）一次烧成——白地蓝花，钴料呈色稳定鲜艳；"
     "②**成熟**——元代景德镇成熟（元青花大器雄浑，鬼谷子下山大罐拍卖"
     "2.3 亿元），明清鼎盛（永乐宣德青花用进口「苏麻离青」发色浓艳带"
     "铁锈斑）；③**海上传奇**——青花瓷是大航海时代中国出口大宗，「"
     "大航海时代中国出口大宗，「瓷器」与国名同源享誉世界，荷兰代尔夫"
     "特蓝陶即仿"
     "青花；④**审美**——蓝白对比素雅宁静，图案融合中式山水花鸟与"
     "伊斯兰几何纹（外销瓷适应中东市场——文明互鉴的物证）；⑤**"
     "鉴别入门**——看釉面光泽/青料发色/胎骨与款识（官窑年款规范）。",
     ["青花瓷是怎么做的", "青花瓷为什么是蓝白色的",
      "元青花", "苏麻离青", "外销瓷", "青花瓷鉴别"],
     ["问五大名窑", "问瓷器发展史"],
     "atomic", "",
     "青花瓷=钴料绘胎罩透明釉1300°C一次烧成白地蓝花+元代景德镇成熟"
     "大宗，「瓷器」与国名同源享誉世界，荷兰代尔夫特蓝陶即仿"
     "代尔夫特仿烧+融合中式与伊斯兰纹文明互鉴+鉴别看釉青料胎款。"),
]

QUESTIONS = [
    ("QB-1277", "木版年画是怎么制作的？四大产地在哪里？", "文化", "技术直答",
     ["雕版", "套色", "杨柳青", "朱仙镇"], "通识拓展346"),
    ("QB-1278", "青花瓷是怎么烧制的？为什么被称为中国的名片？", "文化", "技术直答",
     ["钴料", "青花", "景德镇", "外销"], "通识拓展346"),
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
                               "level:L2", "status:verified", "batch:通识拓展346"],
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
    bank["version"] = "v6.12"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
