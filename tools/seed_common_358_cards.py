# -*- coding: utf-8 -*-
"""seed_common_358_cards.py · 通识拓展批次358知识卡+题库（幂等）

358：文化-汉服/文化-旗袍（传统服饰新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1309/1310+双id可用）。
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
    ("kp_card_hanfu2",
     "汉服",
     "服饰文化知识点内容（人话接口）", "文化",
     "汉服——汉族传统服饰体系：①**形制**——交领右衽（左襟压右襟，"
     "「右衽」是华夏与「左衽」夷狄的文化区分）、系带隐扣、上衣下裳/"
     "衣裳连属（深袍）两大体系；②**主要款式**——曲裾深衣（汉）/襦裙"
     "（齐胸/齐腰，唐宋）/袄裙（明）/直裾/圆领袍；③**文化内涵**——"
     "「上衣下裳」象征天地秩序，宽袍大袖体现含蓄庄重；④**消亡与复兴**"
     "——清初剃发易服中断三百余年，21 世纪汉服运动复兴（都市日常化/"
     "节日化穿着渐成风潮）；⑤**与和服韩服关系**——和服源自吴服、韩服"
     "受明制服饰影响，同属东亚服饰文化圈；⑥**形制考据**——汉服圈重视"
     "「形制正确」（有出土文物/壁画佐证），山正（正版山寨）之争是热点"
     "话题。",
     ["汉服是什么", "汉服的形制", "交领右衽", "汉服运动",
      "齐胸襦裙", "汉服和和服的区别"],
     ["问汉服节", "问明制汉服"],
     "atomic", "",
     "汉服=汉族传统服饰交领右衽系带隐扣+上衣下裳与深袍两大体系+曲裾"
     "襦裙袄裙圆领袍款式+清初剃发易服中断三百年+21世纪汉服运动复兴"
     "+和服韩服同属东亚服饰文化圈+形制考据山正之争。"),
    ("kp_card_qipao2",
     "旗袍",
     "服饰文化知识点内容（人话接口）", "文化",
     "旗袍——东方美的现代演绎：①**演变**——清代旗人袍服（宽平直）→"
     "民国 1920 年代上海改良（收腰显曲线/短袖/开衩）——中西合璧的产物"
     "；②**工艺要素**——立领/盘扣（手工布纽扣）/开衩/滚边/面料（织锦"
     "缎/丝绒/印花绸）；③**黄金时代**——1930 年代上海（月份牌画/"
     "阮玲玉等影星带动），社交场合与女学生制服皆见；④**文化符号**——"
     "宋美龄外交着装/王家卫《花样年华》23 套旗袍演绎含蓄暧昧——旗袍"
     "成为东方女性美学代表；⑤**现代**——婚礼礼服/礼仪迎宾/改良日常"
     "款，2011 年旗袍手工制作技艺列入国家级非遗；⑥**穿搭配**——"
     "盘发+珍珠+高跟鞋经典，根据身材选版型（宽松改良款包容度更高）。",
     ["旗袍的来历", "旗袍的演变", "盘扣是什么", "旗袍的款式",
      "花样年华旗袍", "旗袍怎么搭配"],
     ["问龙凤褂", "问旗袍与和服对比"],
     "atomic", "",
     "旗袍=清代旗人袍服→1920年代上海改良收腰显曲线中西合璧+立领盘扣"
     "开衩滚边织锦缎+1930上海黄金时代月份牌影星+宋美龄外交花样年华"
     "+手工技艺国家级非遗+婚礼礼仪改良日常款。"),
]

QUESTIONS = [
    ("QB-1309", "汉服的形制有什么讲究？什么是交领右衽？", "文化", "技术直答",
     ["交领", "右衽", "襦裙", "形制"], "通识拓展358"),
    ("QB-1310", "旗袍是怎么演变而来的？它有什么工艺特色？", "文化", "技术直答",
     ["旗袍", "改良", "盘扣", "立领"], "通识拓展358"),
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
                               "level:L2", "status:verified", "batch:通识拓展358"],
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
    bank["version"] = "v6.24"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
