# -*- coding: utf-8 -*-
"""seed_common_250_cards.py · 通识拓展批次250知识卡+题库（幂等）

250：物理-飞机为什么逆风起飞/交通-红绿灯的配色科学
KCCS 四要素+题干原句触发词。预检已过（QB-941/942+双id可用）。
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
    ("kp_card_takeoff",
     "飞机为什么逆风起飞",
     "物理通识知识点内容（人话接口）", "基础科学",
     "飞机逆风起飞降落的原理：①**升力来源**——机翼上表面弯曲下表面平，"
     "流过上面的空气路程长流速快压强小，下面的流速慢压强大——压差把飞机"
     "托起来（升力与**空速**的平方成正比）；②**关键概念：空速 vs 地速**——"
     "升力只看飞机与空气的相对速度（空速），不看对地速度；③**逆风起飞**"
     "——迎风跑，风迎面吹来直接「送」空速：地速 140km/h+逆风 30km/h=空速 "
     "170km/h，更短滑跑距离就能达到起飞所需升力——跑道更短、更省油、轮胎"
     "刹车损耗更小；④**逆风降落同理**——接地时的地速更小，滑行距离短刹车"
     "更安全，且逆风侧风分量把飞机「按」在跑道上；⑤**顺风的坏处**——起飞"
     "滑跑距离拉长、降落接地速度大易冲出跑道，所以跑道方向按当地常年风向"
     "设计，飞机尽量「顶风」起降。",
     ["飞机为什么逆风起飞", "逆风起飞还是顺风起飞", "飞机升力怎么产生",
      "空速和地速", "飞机降落为什么也逆风", "伯努利原理飞机"],
     ["问舰载机甲板风", "问风洞实验"],
     "atomic", "",
     "逆风起降=升力∝空速平方(机翼上下压差·伯努利)+逆风送空速→滑跑更短"
     "省油+降落接地地速小刹车安全+顺风拉长滑跑易冲出跑道+跑道按常年风向"
     "设计。"),
    ("kp_card_trafficlight",
     "红绿灯的配色科学",
     "交通通识知识点内容（人话接口）", "生活常识",
     "红绿灯为什么是红黄绿：①**红灯=红光**——红色在可见光中**波长最长"
     "（约 620-750 纳米）**，散射弱穿透强，雨雾天最远就能看见——警示「停」"
     "必须选视认距离最长的颜色；②**绿灯**——与红色对比鲜明，且绿色在人类"
     "视觉中代表安全通行（二战前日本曾用蓝灯，后调整光谱兼容色觉障碍者）；"
     "③**黄灯**——波长居中，且是红绿之间**过渡警示**：国际惯例黄灯时长约 "
     "3 秒，给「来不及停」的车清空路口的时间（猛刹车追尾 vs 闯灯的两难缓冲）；"
     "④**色盲兼容设计**——红绿色盲人群庞大（男性约 8%），所以灯的**位置"
     "固定编码**（红灯永远在最上/左），色盲也能靠位置判断；⑤**历史**——"
     "红绿灯源于 19 世纪英国铁路信号系统（红=停源自危险信号的红色火药桶"
     "传统），1868 年伦敦装上世界第一盏道路信号灯。",
     ["红绿灯为什么是红黄绿", "红灯为什么代表停", "黄灯是干什么用的",
      "黄灯有几秒", "红绿色盲怎么看红绿灯", "红绿灯的由来"],
     ["问智能交通信号配时", "问铁路信号系统"],
     "atomic", "",
     "红黄绿=红光波长最长散射弱穿透强视认距离最远(停)+绿与红对比鲜明+"
     "黄灯3秒过渡缓冲清空路口+位置固定编码兼容红绿色盲(男8%)+源于19世纪"
     "英国铁路信号1868伦敦首盏。"),
]

QUESTIONS = [
    ("QB-941", "飞机为什么逆风起飞？顺风起飞有什么坏处？", "基础科学", "技术直答",
     ["升力", "空速", "逆风", "滑跑"], "通识拓展250"),
    ("QB-942", "红绿灯为什么选红黄绿三种颜色？黄灯有什么作用？", "生活常识", "技术直答",
     ["波长", "穿透", "黄灯", "3秒"], "通识拓展250"),
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
                               "level:L2", "status:verified", "batch:通识拓展250"],
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
    bank["version"] = "v5.21"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
