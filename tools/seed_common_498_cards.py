# -*- coding: utf-8 -*-
"""seed_common_498_cards.py · 通识拓展批次498知识卡+题库（幂等）

498：2 张新卡·音乐石刻域轮换（五声音阶 kp_card_wushengyinxian /
    大足石刻 kp_card_dazushike），五声音阶配双题。
预检已过（QB-1726~1728 可用，两主题题库卡库零独立卡；
    都江堰已有 2 卡 3 题按查重跳过）。
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
             "MTBF", "SQA", "IMC", "HMO", "JD", "STAR", "Word", "offer",
             "XMind", "HDR", "Robotaxi"}


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
    ("kp_card_wushengyinxian",
     "五声音阶",
     "音乐常识知识点内容（人话接口）", "艺术学堂",
     "五声音阶——中国传统音乐的调式基础：①**五个音**——宫、商、角、"
     "徵、羽（按音高从低到高），大致对应简谱的 do、re、mi、sol、la——"
     "没有 fa 和 si；②**由来**——春秋战国《管子》已载「三分损益法」"
     "生成五音，《吕氏春秋》有完整记载，比十二平均律早两千多年；③**"
     "色彩**——五声调式旋律流畅古朴，是民歌（茉莉花）、古琴曲（高山"
     "流水）、戏曲唱腔的底层语汇；④**衍生**——加入变宫、变徵成七声"
     "（如《荆轲刺秦》筑声「为变徵之声」）；⑤**验证法**——用只有黑键"
     "的钢琴黑键弹出的是五声音阶感旋律（如《沧海一声笑》）。",
     ["五声音阶是哪五个音", "宫商角徵羽", "中国传统调式",
      "三分损益法", "为什么中国歌没有4和7", "民族五声调式"],
     ["问十二平均律", "问古琴"],
     "atomic", "",
     "五声音阶=宫商角徵羽对应do re mi sol la没有fa si+管子三分损益法"
     "吕氏春秋完整记载早两千多年+旋律流畅古朴茉莉花高山流水底层语汇+"
     "加变宫变徵成七声变徵之声+黑键弹五声感沧海一声笑。"),
    ("kp_card_dazushike",
     "大足石刻",
     "考古常识知识点内容（人话接口）", "历史与文明",
     "大足石刻——重庆大足的唐宋摩崖造像群：①**范围**——以宝顶山、北"
     "山、南山、石门山、石篆山「五山」为代表，造像 5 万余尊；②**时代"
     "特色**——晚唐至南宋开凿，把佛教造像「中国化、生活化」：父母恩重"
     "经变相刻的就是育儿日常，牧牛图借驯牛喻修行；③**镇山之宝**——宝"
     "顶山千手观音：实刻手臂 830 只（不是传说中的千只），金碧辉煌，"
     "2008-2015 年历时 8 年修复；④**艺术地位**——与云冈、龙门一脉相"
     "承又自成一格，是中国晚期石窟艺术的巅峰；⑤**地位**——1999 年列"
     "入世界文化遗产。",
     ["大足石刻在哪里", "千手观音有几只手", "大足石刻是哪个朝代",
      "宝顶山北山", "父母恩重经变相", "重庆石刻"],
     ["问四大石窟", "问乐山大佛"],
     "atomic", "",
     "大足石刻=重庆大足宝顶山北山等五山代表造像5万余尊+晚唐至南宋开"
     "凿佛教造像中国化生活化父母恩重经变相牧牛图+宝顶山千手观音实刻"
     "830只手2008到2015历时8年修复+中国晚期石窟艺术巅峰+1999年世界文"
     "化遗产。"),
]

QUESTIONS = [
    ("QB-1726", "中国传统五声音阶是哪五个音？对应简谱里的什么？",
     "音乐常识", "技术直答",
     ["五声音阶", "宫商角徵羽", "调式", "传统音乐"], "通识拓展498·新卡"),
    ("QB-1727", "大足石刻在哪里？千手观音有什么特别之处？",
     "历史常识", "技术直答",
     ["大足石刻", "千手观音", "宝顶山", "重庆"], "通识拓展498·新卡"),
    ("QB-1728", "「宫商角徵羽」是什么？出自什么年代？",
     "音乐常识", "技术直答",
     ["宫商角徵羽", "五声音阶", "三分损益", "先秦"], "通识拓展498·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展498"],
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
    bank["version"] = "v7.63"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
