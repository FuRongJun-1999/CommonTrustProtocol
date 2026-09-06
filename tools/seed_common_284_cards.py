# -*- coding: utf-8 -*-
"""seed_common_284_cards.py · 通识拓展批次284知识卡+题库（幂等）

284：食品科学-泡菜腌制原理/食品科学-味精的真相（发酵食品新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1076/1077+双id可用）。
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
             "BCS"}


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
    ("kp_card_pickle",
     "泡菜腌制的科学",
     "食品科学知识点内容（人话接口）", "生活常识",
     "泡菜为什么酸脆且能存放：①**乳酸菌主导**——蔬菜在盐水中，乳酸菌把糖"
     "发酵成乳酸（酸味来源），酸度升高抑制腐败菌——「以酸抑菌」的天然"
     "防腐；②**盐的角色**——高盐初期抑制杂菌给乳酸菌争取时间+渗出蔬菜"
     "水分（脱水变脆韧）——盐太少杂菌抢跑变腐，太多乳酸菌也停工；③**"
     "无氧环境**——乳酸菌厌氧，坛沿水密封隔绝氧气（霉菌需氧），泡菜坛"
     "设计就是天然厌氧发酵罐；④**亚硝酸盐曲线**——腌制初期 2-10 天亚硝"
     "酸盐浓度攀升至峰值（杂菌把硝酸盐转成亚硝酸盐），20-30 天后乳酸菌"
     "主导降到安全低值——**腌制不足一个月的「急泡菜」反而最危险**；⑤"
     "**脆度**——嗜酸乳酸菌分解果胶变软是过头的标志，加少许白酒抑杂菌"
     "保脆；⑥韩国泡菜（韩式辣白菜发酵）与四川泡菜（老盐水）菌群路线"
     "不同但同属乳酸发酵。",
     ["泡菜为什么是酸的", "泡菜腌制的原理", "泡菜多久能吃",
      "亚硝酸盐什么时候最高", "泡菜为什么能存放", "四川泡菜和韩国泡菜"],
     ["问发酵菌种培养", "问梅子酒酿制"],
     "atomic", "",
     "泡菜=乳酸菌产酸以酸抑菌+盐抑杂菌脱水保脆+坛沿水密封厌氧+亚硝酸盐"
     "2-10天峰值20-30天安全(急泡菜最危险)+过头产酶变软+韩川两路乳酸发酵。"),
    ("kp_card_msg",
     "味精的真相",
     "食品科学知识点内容（人话接口）", "生活常识",
     "味精没有传说中那么可怕：①**本质**——味精=谷氨酸钠，谷氨酸是人体"
     "必需氨基酸之一广泛存在于天然食物（番茄/蘑菇/奶酪的「鲜味」就是它）；"
     "②**工艺**——现代味精由粮食（玉米/大米）微生物发酵生产，与酱油酿造"
     "同路线，并非化学合成；③**「致癌」辟谣**——常规食用量下谷氨酸钠"
     "在体内正常代谢，未发现致癌证据，「中餐馆综合征」多项研究未证实与"
     "味精有因果关系；④**适量原则**——真正的「钠摄入超标」问题：味精"
     "含钠，与盐叠加计算——放了味精就少放点盐；⑤**使用技巧**——出锅前"
     "放（长时间高温部分转化为焦谷氨酸钠，虽无害但鲜味减弱）、酸性菜"
     "（糖醋）效果差、凉拌菜先化开；⑥**鸡精≠更健康**——鸡精=味精+盐+"
     "核苷酸增鲜剂+鸡肉粉香精，核心鲜味还是味精，钠含量不低。",
     ["味精致癌是真的吗", "味精是什么做的", "味精什么时候放",
      "鸡精和味精哪个好", "谷氨酸钠", "中餐馆综合征"],
     ["问天然鲜味物质", "问低钠饮食"],
     "atomic", "",
     "味精=谷氨酸钠(天然鲜味氨基酸粮食发酵生产)+常规量无致癌证据中餐馆"
     "综合征未证实因果+真问题是叠加钠超标放味精少放盐+出锅前放酸性菜差"
     "+鸡精=味精+盐+增鲜剂非更健康。"),
]

QUESTIONS = [
    ("QB-1076", "泡菜为什么是酸的？腌制多久吃才安全？", "生活常识", "技术直答",
     ["乳酸菌", "发酵", "亚硝酸盐", "20"], "通识拓展284"),
    ("QB-1077", "味精致癌是真的吗？味精是什么做的？", "生活常识", "技术直答",
     ["谷氨酸钠", "发酵", "辟谣", "钠"], "通识拓展284"),
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
                               "level:L2", "status:verified", "batch:通识拓展284"],
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
    bank["version"] = "v5.55"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
