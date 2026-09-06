# -*- coding: utf-8 -*-
"""seed_common_262_cards.py · 通识拓展批次262知识卡+题库（幂等）

262：科技-磁悬浮列车原理/工程-跨海大桥怎么建
KCCS 四要素+题干原句触发词。预检已过（QB-977/978+双id可用）。
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
             "AlphaGo", "CFOP"}


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
    ("kp_card_maglev",
     "磁悬浮列车原理",
     "科技通识知识点内容（人话接口）", "科技",
     "磁悬浮列车为什么能「飘」起来跑：①**两条技术路线**——电磁悬浮（EMS，"
     "电磁铁吸起轨道，上海磁浮线用此理，悬浮间隙约 1 厘米）与电动悬浮"
     "（EDS，超导体感应排斥「推」起列车，日本超导磁浮线用此理，间隙约 10 "
     "厘米，速度纪录 603km/h）；②**为什么快**——没有轮轨接触摩擦与机械"
     "磨损，阻力只剩空气阻力，噪音与维护成本更低；③**推进=直线电机**——"
     "把旋转电机的定子「展开」铺在轨道上，磁场波沿线移动像「追着推」列车"
     "（列车自带磁场被推拉前进）；④**中国实践**——上海磁浮示范线（2003 年"
     "通车，最高 430km/h）；国产常导高速磁浮时速 600 公里级样车下线；⑤"
     "**局限**——造价极高（专用轨道全程无接缝精度要求毫米级）、与既有铁路"
     "网不兼容，适合特定高速走廊而非全面铺开。",
     ["磁悬浮列车为什么能悬浮", "磁悬浮原理", "磁悬浮和高铁哪个快",
      "上海磁悬浮多快", "直线电机", "超导磁悬浮"],
     ["问磁悬浮造价对比", "问真空管道列车"],
     "atomic", "",
     "磁悬浮=EMS电磁吸起(上海线间隙1cm)与EDS超导排斥(日603km/h纪录间隙"
     "10cm)两路线+无轮轨摩擦只剩空气阻力+直线电机展开定子追着推+上海"
     "2003年430km/h+国产600km/h样车+造价高轨道不兼容难铺开。"),
    ("kp_card_seabridge",
     "跨海大桥怎么建",
     "工程通识知识点内容（人话接口）", "科技",
     "跨海大桥建造的关键：①**先定桥型**——跨径决定结构：小跨用梁桥，大跨"
     "用斜拉桥（塔+斜索吊梁，数百米跨）与悬索桥（主缆+吊索，千米级跨，"
     "如土耳其恰纳卡莱大桥主跨 2023 米）；②**桥墩怎么在海里立**——钢管桩"
     "群打海床（港珠澳大桥用了上万根）+承台+墩身，深水区用整体式沉井基础；"
     "③**预制拼装**——梁段陆上工厂预制、巨轮运到现场像「搭积木」架设"
     "（港珠澳预制化率极高，海上作业量最小化）；④**抗风抗浪抗腐蚀**——"
     "台风期结构风振校核、大跨桥装阻尼器抗涡振、海洋环境用高性能混凝土+"
     "钢筋防腐涂层保 120 年设计寿命；⑤**世界之最**——港珠澳大桥 55 公里"
     "全球最长跨海通道（含 6.7 公里海底隧道——留出伶仃洋主航道给巨轮，"
     "机场航线限高区变隧道）；⑥**生态补偿**——中华白海豚保护区施工限时"
     "与监测。",
     ["跨海大桥怎么建的", "桥墩在海里怎么打", "悬索桥和斜拉桥区别",
      "港珠澳大桥多长", "为什么有海底隧道", "跨海大桥寿命"],
     ["问隧道盾构技术", "问桥梁检测维护"],
     "atomic", "",
     "跨海桥=桥型按跨径选(斜拉数百米/悬索千米级恰纳卡莱2023m)+海中钢管桩"
     "群基础+预制拼装搭积木减海上作业+抗风浪涡振阻尼器+防腐120年寿命+"
     "港珠澳55km最长含6.7km海底隧道让航道+白海豚生态限时施工。"),
]

QUESTIONS = [
    ("QB-977", "磁悬浮列车为什么能悬浮和高速行驶？原理是什么？", "科技", "技术直答",
     ["悬浮", "电磁", "直线电机", "摩擦"], "通识拓展262"),
    ("QB-978", "跨海大桥的桥墩是怎么在海里建的？为什么有的地方要修海底隧道？",
     "科技", "技术直答",
     ["桥墩", "桩", "隧道", "航道"], "通识拓展262"),
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
                               "level:L2", "status:verified", "batch:通识拓展262"],
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
    bank["version"] = "v5.33"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
