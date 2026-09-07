# -*- coding: utf-8 -*-
"""seed_common_402_cards.py · 通识拓展批次402知识卡+题库（幂等）

402：2 张新卡（焯水与勾芡 kp_card_blanch / 吃火锅的门道 kp_card_hotpot）
    + 1 张存量卡补题（熬夜后的补救 kp_card_stayuprecover，已在库）。
KCCS 四要素+题干原句触发词。预检已过（QB-1444~1446 可用，
焯水/勾芡/火锅题库 0 覆盖，卡库无同名卡；熬夜已有 2 题泛考
但「熬夜后怎么补救」精确角度 0 覆盖，卡触发词原句匹配）。
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
             "MTBF", "SQA", "IMC", "HMO"}


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
    ("kp_card_blanch",
     "焯水与勾芡",
     "烹饪技法知识点内容（人话接口）", "生活常识",
     "两个最常用的中式烹饪前/后处理技法：①**焯水**——把食材放进沸水"
     "或冷水锅短时间煮：肉类**冷水下锅**（随水温升高血沫渗出，去腥去"
     "血水），绿叶蔬菜**沸水下锅**（快速烫熟保持翠绿脆嫩，可加几滴油"
     "和盐保色）；焯水还能去除草酸（菠菜）和农残、缩短后续烹饪时间；"
     "②**勾芡**——淀粉加水调匀，在菜肴出锅前淋入并搅匀：淀粉糊化后"
     "把汤汁变稠，「挂味」在食材表面（芡汁包裹=入口更有味）；③**芡的"
     "厚薄**——厚芡用于爆炒快菜（汁紧裹），薄芡用于汤羹（微稠顺滑）；"
     "④**小技巧**——勾芡后再淋明油会更亮；汤汁太多先大火收汁再勾芡，"
     "别靠淀粉硬堆。",
     ["焯水的作用", "肉类焯水冷水还是热水", "勾芡用什么淀粉",
      "勾芡的作用", "薄芡厚芡", "菠菜为什么要焯水"],
     ["问刀工", "问调味"],
     "atomic", "",
     "焯水勾芡=肉类冷水下锅去血沫蔬菜沸水保色加油盐+焯去草酸农残缩短"
     "烹饪+勾芡淀粉糊化挂味出锅前淋+厚芡爆炒薄芡汤羹+勾芡后淋明油更"
     "亮先收汁再勾芡。"),
    ("kp_card_hotpot",
     "吃火锅的门道",
     "饮食常识知识点内容（人话接口）", "生活常识",
     "火锅——围炉共食的中国式聚餐：①**涮煮时间**——毛肚「七上八下」"
     "十几秒脆嫩，薄切牛羊肉变色即熟；但肉片必须完全变色熟透再吃（防"
     "寄生虫），海鲜要煮够时间；②**生熟分开**——夹生肉的筷子和餐具"
     "与入口的分开（防细菌交叉污染）；③**汤底的坑**——久煮汤嘌呤高"
     "（痛风/高尿酸慎喝老汤），锅底高油高盐，涮前喝点清汤、少喝最后"
     "的浓汤；④**烫食风险**——食物出锅晾一晾再吃，长期吃超过 65℃"
     "的烫食会损伤食管黏膜（国际癌症机构列为 2A 类致癌因素）；⑤**"
     "搭配**——荤素均衡、先菜后肉更舒服，餐后酸奶水果护胃。",
     ["火锅怎么吃健康", "毛肚涮多久", "火锅汤能喝吗",
      "吃火锅注意什么", "生熟分开", "烫食危害"],
     ["问烧烤健康", "问痛风饮食"],
     "atomic", "",
     "火锅=毛肚七上八下肉片变色熟透防寄生虫+生熟筷子分开防交叉污染+"
     "久煮汤嘌呤高高油高盐少喝浓汤+超65度烫食损伤食管2A致癌晾一晾+"
     "荤素均衡先菜后肉餐后酸奶。"),
]

QUESTIONS = [
    ("QB-1444", "焯水有什么作用？肉类和蔬菜焯水有什么区别？",
     "生活常识", "技术直答",
     ["焯水", "去腥", "冷水", "沸水"], "通识拓展402"),
    ("QB-1445", "熬夜后怎么补救？第二天怎么快速恢复状态？",
     "健康与身体", "技术直答",
     ["熬夜", "补觉", "恢复", "生物钟"], "通识拓展402·存量卡补题"),
    ("QB-1446", "吃火锅要注意什么？火锅汤底能喝吗？",
     "生活常识", "技术直答",
     ["火锅", "涮煮", "嘌呤", "烫食"], "通识拓展402"),
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
                               "level:L2", "status:verified", "batch:通识拓展402"],
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
    bank["version"] = "v6.72"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
