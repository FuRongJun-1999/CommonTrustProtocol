# -*- coding: utf-8 -*-
"""seed_common_360_cards.py · 通识拓展批次360知识卡+题库（幂等）

360：古生物-猛犸象/古生物-冰河期动物（史前动物新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1313/1314+双id可用）。
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
    ("kp_card_mammoth2",
     "猛犸象",
     "古生物知识点内容（人话接口）", "历史",
     "猛犸象——冰河时代的巨兽：①**外形**——体型比现代大象大（草原猛犸"
     "肩高可达 4 米），披浓密长毛御寒（长毛象之名），弯曲巨大象牙可达 4-5 "
     "米（铲雪找食/争斗武器）；②**生存年代**——距今约 500 万年至 4000 "
     "年前灭绝（西伯利亚弗兰格尔岛残存种群存活至约 4000 年前——金字塔"
     "建成时还有猛犸象）；③**食物**——草与灌木，臼齿宽平适于研磨粗硬"
     "草料（一生换 6 次臼齿）；④**为什么灭绝**——冰河期结束气候变暖"
     "栖息地缩小+人类狩猎双因素；⑤**冷冻化石**——西伯利亚冻土发现保留"
     "软组织/血液甚至毛发的完整个体（DNA 研究与「复活」讨论的对象）；⑥"
     "**人类关系**——原始人猎捕猛犸（骨屋/象牙雕刻品），是史前艺术重要"
     "题材。",
     ["猛犸象是什么", "猛犸象为什么灭绝", "猛犸象和大象的区别",
      "猛犸象化石", "长毛象", "猛犸象能复活吗"],
     ["问冰河时期动物", "问大象演化"],
     "atomic", "",
     "猛犸象=冰河巨兽比现代象大披浓密长毛(长毛象)+弯曲巨牙4-5米铲雪"
     "争斗+约4000年前才灭绝(弗兰格尔岛残存至金字塔时代)+灭绝=气候变暖"
     "栖息地缩小+人类狩猎+西伯利亚冻土完整化石DNA研究复活讨论+史前"
     "艺术题材。"),
    ("kp_card_iceageanimal",
     "冰河期动物",
     "古生物知识点内容（人话接口）", "基础科学",
     "冰河期的动物们：①**冰河期**——地球历史上多次被大面积冰盖覆盖的"
     "寒冷时期（末次冰盛期约 2 万年前），海平面比现在低 100 多米（白令"
     "陆桥使人类步入美洲）；②**明星动物**——猛犸象/披毛犀（长毛防寒）"
     "/大角鹿（角展 3 米+）/剑齿虎（匕首状犬齿）/洞熊洞狮/大地懒（南美"
     "巨兽）；③**巨型动物的生存策略**——大体型保温+长毛脂肪御寒+迁徙"
     "追食物；④**大灭绝**——冰期末气候剧变+人类狩猎扩张，巨型动物"
     "全球性灭绝（澳洲/美洲最惨烈）；⑤**幸存者**——"
     "驯鹿/麝牛/北极狐等适应寒冷的物种延续至今；⑥**研究价值**——冻土"
     "化石+冰芯+洞穴壁画三重证据还原冰河生态。",
     ["冰河时期有哪些动物", "猛犸象披毛犀", "剑齿虎",
      "冰河期巨兽为什么灭绝", "大地懒", "冰河时代动物"],
     ["问灭绝与人类关系", "问其他史前生物"],
     "atomic", "",
     "冰河期动物=末次冰盛期2万年前海平面低100多米白令陆桥+明星猛犸象"
     "披毛犀大角鹿剑齿虎洞熊大地懒+大体型长毛脂肪御寒迁徙策略+冰期末"
     "气候剧变与人类狩猎全球巨兽灭绝+驯鹿麝牛北极狐幸存+冻土化石冰芯"
     "洞穴壁画三重证据。"),
]

QUESTIONS = [
    ("QB-1313", "猛犸象长什么样？它们为什么灭绝了？", "历史", "技术直答",
     ["猛犸象", "长毛", "灭绝", "气候"], "通识拓展360"),
    ("QB-1314", "冰河时期有哪些著名动物？它们的灭绝和人类有关系吗？", "历史", "技术直答",
     ["冰河期", "猛犸象", "剑齿虎", "灭绝"], "通识拓展360"),
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
                               "level:L2", "status:verified", "batch:通识拓展360"],
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
    bank["version"] = "v6.25"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
