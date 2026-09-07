# -*- coding: utf-8 -*-
"""seed_common_497_cards.py · 通识拓展批次497知识卡+题库（幂等）

497：2 张新卡 + 1 张存量卡补题·理科艺术域轮换
    （伯努利原理 kp_card_bernoulli / 十二平均律 kp_card_12tet 新卡，
    共振→受迫振动卡 kp_6461893227 存量补题）。
预检已过（QB-1723~1725 可用，伯努利/十二平均律题库卡库双零）。
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
    ("kp_card_bernoulli",
     "伯努利原理",
     "物理常识知识点内容（人话接口）", "科学世界",
     "伯努利原理——流体力学最常用的结论：①**核心**——在稳定流动的流"
     "体（液体或气体）中，流速越大的位置压强越小，流速越小的地方压强"
     "越大；②**提出**——瑞士科学家丹尼尔·伯努利在 1738 年《流体动力"
     "学》中给出；③**飞机升力**——机翼上凸下平，上方气流路程长流速快"
     "压强小、下方流速慢压强大，压强差把飞机托起来；④**生活实例**——"
     "向两张纸中间吹气纸反而合拢、站台安全线（列车高速通过时身侧气流"
     "快压强小，会被「推」向列车）、喷雾器与化油器原理；⑤**口算实验**"
     "——对着硬币上方吹气，硬币会跳起。",
     ["什么是伯努利原理", "飞机为什么能飞起来", "流速大压强小",
      "站台安全线的原因", "两张纸吹气实验", "机翼升力"],
     ["问帕斯卡定律", "问阿基米德原理"],
     "atomic", "",
     "伯努利原理=稳定流动流体流速越大压强越小+丹尼尔·伯努利1738年流体"
     "动力学提出+机翼上凸下平上快下慢压强差产生升力+吹气纸合拢站台安"
     "全线喷雾器生活实例+硬币上方吹气会跳起。"),
    ("kp_card_12tet",
     "十二平均律",
     "音乐常识知识点内容（人话接口）", "艺术学堂",
     "十二平均律——现代音乐律制的基础：①**是什么**——把一个八度均分"
     "为 12 个半音，相邻半音频率比相等（都是 2 的 12 次方根，约 1."
     "059），转调方便；②**中国首创**——明代朱载堉（1536-1611）在《律"
     "学新说》中最早给出十二平均律的精确算法（新法密率），比欧洲早数"
     "十年；③**西方推广**——巴赫为推广该律制创作《平均律钢琴曲集》"
     "（48 首前奏曲与赋格），被誉为音乐的「旧约圣经」；④**键盘对应**"
     "——钢琴一个八度 7 个白键 + 5 个黑键共 12 个音就是十二平均律；"
     "⑤**意义**——解决了纯律/三分损益法转调跑音的问题，让任意转调成"
     "为可能，是现代乐器定音的世界标准。",
     ["什么是十二平均律", "十二平均律是谁发明的", "朱载堉",
      "平均律钢琴曲集", "钢琴为什么有黑白键", "半音是什么"],
     ["问五声音阶", "问纯律"],
     "atomic", "",
     "十二平均律=一个八度均分12个半音频率比2的12次方根约1.059转调方"
     "便+明代朱载堉律学新说最早精确计算早欧洲数十年+巴赫平均律钢琴曲"
     "集48首推广旧约圣经+钢琴八度7白5黑12音+解决转调跑音现代定音标准"
     "。"),
]

QUESTIONS = [
    ("QB-1723", "什么是伯努利原理？飞机为什么能飞起来？",
     "科学常识", "技术直答",
     ["伯努利", "流速", "压强", "机翼升力"], "通识拓展497·新卡"),
    ("QB-1724", "什么是十二平均律？它是谁最早精确计算的？",
     "音乐常识", "技术直答",
     ["十二平均律", "朱载堉", "半音", "八度"], "通识拓展497·新卡"),
    ("QB-1725", "什么是共振现象？生活中有哪些共振的例子？",
     "科学常识", "技术直答",
     ["共振", "受迫振动", "固有频率", "振幅最大"], "通识拓展497·存量卡补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展497"],
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
    bank["version"] = "v7.62"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
