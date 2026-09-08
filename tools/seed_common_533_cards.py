# -*- coding: utf-8 -*-
"""seed_common_533_cards.py · 通识拓展批次533知识卡+题库（幂等）

533：2 张新卡·礼俗文化域（年龄雅称 kp_card_nianling——总括角度，
    花甲单题 QB-738 已覆盖不冲突 / 避讳文化 kp_card_bihui 双零新卡）。
预检已过（QB-1831~1833 可用）。
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
    ("kp_card_nianling",
     "年龄雅称",
     "传统文化知识点内容（人话接口）", "传统文化",
     "年龄雅称——古人给每段年岁的诗意名字：①**幼年**——襁褓（未满周"
     "岁）、垂髫与总角（童年，头发不束）、豆蔻（女子十三四岁，杜牧「豆"
     "蔻梢头二月初」）、及笄（女子十五，可以盘发插簪）、弱冠（男子二十"
     "，行冠礼）；②**中年**——而立（三十）、不惑（四十）、知天命（五"
     "十），出自《论语》「三十而立，四十而不惑，五十而知天命」；③**"
     "老年**——耳顺/花甲（六十，干支纪年六十年一轮回）、古稀（七十，"
     "杜甫「人生七十古来稀」）、耄耋（八九十岁）、期颐（百岁，「颐养」"
     "之年）；④**用处**——读古文辨年纪、贺寿择词（寿比南山不老松）"
     "，都靠这套雅称体系。",
     ["年龄雅称", "而立之年是多少岁", "不惑", "弱冠",
      "豆蔻年华", "耄耋", "期颐"],
     ["问生肖", "问干支纪年"],
     "atomic", "",
     "年龄雅称=襁褓周岁垂髫总角童年+豆蔻女十三四及笄女十五弱冠男二十+"
     "而立三十不惑四十知天命五十论语三十而立+花甲六十干支轮回古稀七十"
     "杜甫诗耄耋八九十期颐百岁+贺寿读古文辨年齿。"),
    ("kp_card_bihui",
     "避讳文化",
     "传统文化知识点内容（人话接口）", "传统文化",
     "避讳文化——不能直呼的名字：①**什么是避讳**——古人不能直呼帝王"
     "与尊长的名字，写文章遇之要改字、缺笔或空格；②**国讳**——避皇帝"
     "名讳：嫦娥本名「姮娥」，为避汉文帝刘恒讳改「嫦娥」；「观世音」简"
     "称「观音」一说与避唐太宗李世民讳有关；③**家讳**——避父祖名："
     "司马迁父名「谈」，《史记》全书避「谈」字；诗人李贺因父名「晋肃"
     "」遭人非议不得考进士，韩愈为此写《讳辩》鸣不平；④**民间典故**——"
     "宋州官田登讳「灯」，元宵放灯改称「放火三日」，遂有「只许州官放"
     "火，不许百姓点灯」；⑤**影响**——避讳给古书古地名留下许多「改"
     "名痕迹」，也是考证文献年代的重要线索。",
     ["避讳是什么", "国讳", "家讳", "嫦娥名字的由来",
      "只许州官放火", "李贺讳辩"],
     ["问汉字六书", "问古代礼仪"],
     "atomic", "",
     "避讳文化=不直呼帝王尊长名讳改字缺笔空格+国讳姮娥避刘恒改嫦娥观音"
     "简称一说避李世民+家讳司马迁避父谈字李贺父晋肃不得考进士韩愈讳辩"
     "+田登讳灯只许州官放火不许百姓点灯+改名痕迹考证文献年代线索。"),
]

QUESTIONS = [
    ("QB-1831", "「而立」「不惑」「知天命」分别指多少岁？",
     "传统文化", "技术直答",
     ["而立", "不惑", "知天命", "年龄"], "通识拓展533·新卡"),
    ("QB-1832", "「弱冠」「及笄」「豆蔻」分别指什么年纪的男女？",
     "传统文化", "技术直答",
     ["弱冠", "及笄", "豆蔻", "年纪"], "通识拓展533·新卡"),
    ("QB-1833", "古人的「避讳」是什么？嫦娥的名字和避讳有什么关系？",
     "传统文化", "技术直答",
     ["避讳", "嫦娥", "姮娥", "刘恒"], "通识拓展533·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展533"],
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
    bank["version"] = "v7.98"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
