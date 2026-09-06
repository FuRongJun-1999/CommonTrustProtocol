# -*- coding: utf-8 -*-
"""seed_common_328_cards.py · 通识拓展批次328知识卡+题库（幂等）

328：建筑-布达拉宫/建筑-苏州园林（世界遗产建筑延续）
KCCS 四要素+题干原句触发词。预检已过（QB-1223/1224+双id可用）。
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
    ("kp_card_potala",
     "布达拉宫",
     "建筑历史知识点内容（人话接口）", "历史",
     "布达拉宫——雪域高原的宫堡：①**缘起**——公元 7 世纪松赞干布为迎娶"
     "文成公主始建，17 世纪五世达赖喇嘛重建扩为今日规模；②**结构**——"
     "依红山而建，海拔约 3700 米，主楼 13 层高 115 米；分白宫（达赖喇嘛"
     "起居与政务）与红宫（佛殿与历代达赖灵塔殿）两部分——白宫白宫红宫"
     "红，是藏式宫堡式建筑的巅峰；③**建造智慧**——墙体收分（上窄下宽"
     "斜收增大稳定性）、地基深入岩层、石木结构（墙厚达数米）——高原"
     "地震带上屹立 300 余年；④**珍藏**——大量壁画/唐卡/经卷/灵塔"
     "（五世达赖灵塔用黄金约 3721 公斤珠宝万颗）；⑤**地位**——1961 年"
     "首批全国重点文保，1994 年列入世界遗产；⑥**参观限制**——每日限流"
     "限时（保护古建筑与壁画），旺季需提前预约。",
     ["布达拉宫在哪里", "布达拉宫是谁建的", "白宫和红宫",
      "布达拉宫多少米", "布达拉宫世界遗产", "布达拉宫灵塔"],
     ["问文成公主入藏", "问藏式建筑"],
     "atomic", "",
     "布达拉宫=7世纪松赞干布迎文成公主始建17世纪五世达赖重建+红山3700m"
     "13层115m+白宫起居政务红宫佛殿灵塔+墙收分石木结构抗高原震+灵塔"
     "黄金3721kg+1994世遗+限流预约保护。"),
    ("kp_card_suzhougarden",
     "苏州园林",
     "建筑艺术知识点内容（人话接口）", "历史",
     "苏州园林——咫尺之内再造乾坤：①**代表**——拙政园/留园/网师园/"
     "沧浪亭等，「江南园林甲天下，苏州园林甲江南」，1997 年列入世界遗产；"
     "②**造园哲学**——「虽由人作，宛自天开」：人工造景却模仿自然山水，"
     "反对对称规整（与西方几何园林对照）；③**空间手法**——借景（把园外"
     "塔影山色「借」入园中）/框景（门洞窗洞如画框）/移步换景（走一步"
     "换一幅画面），小园做大做大做深；④**元素组合**——叠石（太湖石"
     "「瘦皱漏透」）、理水、花木、建筑（亭台楼榭）四位一体，文人书法"
     "匾额楹联点题（文化意蕴）；⑤**功能**——古代士大夫退休归隐的"
     "「城市山林」——不出城郭而享山水之趣；⑥**匠心**——网师园仅 8 亩"
     "却层次丰富（小中见大典范）。",
     ["苏州园林有什么特点", "拙政园", "借景是什么",
      "虽由人作宛自天开", "太湖石瘦皱漏透", "苏州园林世界遗产"],
     ["问皇家园林对比", "问园林花窗"],
     "atomic", "",
     "苏州园林=拙政园留园网师园沧浪亭1997世遗+虽由人作宛自天开反对称"
     "+借景框景移步换景小中做大+叠石理水花木建筑四位一体匾额点题+"
     "士大夫城市山林归隐+网师园8亩层次典范。"),
]

QUESTIONS = [
    ("QB-1223", "布达拉宫在哪里？白宫和红宫分别是什么用途？", "历史", "技术直答",
     ["西藏", "红山", "白宫", "红宫"], "通识拓展328"),
    ("QB-1224", "苏州园林有什么特点？「借景」是什么手法？", "历史", "技术直答",
     ["苏州园林", "借景", "自然", "移步换景"], "通识拓展328"),
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
                               "level:L2", "status:verified", "batch:通识拓展328"],
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
    bank["version"] = "v5.98"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
