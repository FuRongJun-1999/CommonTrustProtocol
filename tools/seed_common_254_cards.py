# -*- coding: utf-8 -*-
"""seed_common_254_cards.py · 通识拓展批次254知识卡+题库（幂等）

254：食品科学-巧克力的成分与融点/食品-白酒的酿造原理
KCCS 四要素+题干原句触发词。预检已过（QB-953/954+双id可用）。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

WHITELIST = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
             "effect", "OR6A2", "ghrelin", "DOMS", "DHT", "frisson"}


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
    ("kp_card_chocolate",
     "巧克力的成分与融点",
     "食品科学知识点内容（人话接口）", "生活常识",
     "巧克力「只融在口」的科学：①**融点魔法**——可可脂融点约 34-36°C，恰好"
     "略低于体温——含在嘴里刚好化开，拿在手里却保持固态，这是天然油脂里"
     "罕见的多晶型（V 型结晶）给的礼物；②**保存翻车**——温度反复变化会让"
     "可可脂迁移到 V 型以外的结晶（VI 型），表面浮起一层白霜（脂霜），不影响"
     "安全但口感粗糙；③**成分分级**——黑巧克力=可可固形物+可可脂（70% 以上"
     "可可含量风味更浓苦）；牛奶巧克力加乳粉；**白巧克力不含可可固形物**"
     "（只有可可脂+糖+乳），严格说不算「真」巧克力；④**代可可脂警示**——"
     "用氢化植物油替代可可脂，可能含反式脂肪酸，融点不对口感受差（蜡感）；"
     "⑤**狗不能吃巧克力**——可可含可可碱，狗代谢极慢，累积中毒（呕吐心律"
     "失常乃至死亡），黑巧克力浓度越高越危险。",
     ["巧克力为什么一含就化", "巧克力融点", "巧克力表面白霜",
      "白巧克力是巧克力吗", "代可可脂是什么", "狗为什么不能吃巧克力"],
     ["问可可豆发酵工艺", "问巧克力历史"],
     "atomic", "",
     "巧克力=可可脂融点34-36°C略低于体温只融在口(V型结晶)+温度反复出脂霜"
     "不影响安全+白巧克力无可可固形物+代可可脂或含反式脂+可可碱狗无法代谢"
     "中毒勿喂。"),
    ("kp_card_baijiu",
     "白酒的酿造原理",
     "食品化学知识点内容（人话接口）", "生活常识",
     "中国白酒酿造原理：①**两条菌路线**——粮食淀粉先「糖化」（霉菌把淀粉"
     "切成葡萄糖）再「酒化」（酵母把糖发酵成酒精）；西方酿酒分两步用两种"
     "曲/麦芽，中国白酒的独门是**酒曲一步兼做糖化+发酵剂**；②**固态发酵**"
     "——白酒用高粱等粮食固态发酵（西方啤酒葡萄酒液态发酵），配糟醅调节，"
     "窖池微生物群落参与生香；③**蒸馏定高度**——发酵完的酒醅蒸馏取酒，"
     "酒精度可达 50-60 度以上（啤酒葡萄酒一般不到 15 度无需蒸馏）；④**香型**"
     "——窖池/工艺/微生物决定香型：酱香（茅台，高温大曲多轮次）、浓香"
     "（窖泥老窖微生物）、清香（地缸发酵干净）；⑤**「勾兑」本义=调酒工艺**"
     "——不同批次/年份/轮次基酒按比例调配出稳定风味，是正常工序（劣质酒"
     "争议在食用酒精+香精勾兑）；⑥高度酒为何能存——酒精度高抑菌，酯类"
     "物质缓慢熟化「越陈越香」有前提（纯粮固态酒密封存）。",
     ["白酒怎么酿的", "酒曲是什么", "白酒为什么度数高",
      "酱香浓香清香区别", "勾兑是什么意思", "酒为什么越陈越香"],
     ["问品酒感官评价", "问酿酒设备"],
     "atomic", "",
     "白酒=淀粉糖化(霉菌)→酒化(酵母)双路线酒曲一步兼做+固态发酵窖池微生物"
     "生香+蒸馏取高度酒50-60度+香型由窖池工艺定(酱/浓/清)+勾兑本义基酒调配"
     "工艺+高度抑菌酯化熟化越陈越香有前提。"),
]

QUESTIONS = [
    ("QB-953", "巧克力为什么一含就化？狗为什么不能吃巧克力？", "生活常识", "技术直答",
     ["可可脂", "融点", "体温", "可可碱"], "通识拓展254"),
    ("QB-954", "白酒是怎么酿出来的？酒曲起什么作用？勾兑是什么意思？",
     "生活常识", "技术直答",
     ["酒曲", "糖化", "发酵", "蒸馏", "勾兑"], "通识拓展254"),
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
                               "level:L2", "status:verified", "batch:通识拓展254"],
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
    bank["version"] = "v5.25"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
