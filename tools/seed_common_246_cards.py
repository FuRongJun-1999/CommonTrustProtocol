# -*- coding: utf-8 -*-
"""seed_common_246_cards.py · 通识拓展批次246知识卡+题库（幂等）

246：生物-蝙蝠的回声定位/数学-蜂巢的六边形之谜
KCCS 四要素+题干原句触发词。预检已过（QB-929/930+双id可用）。
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
    ("kp_card_bat_echo",
     "蝙蝠的回声定位",
     "生物通识知识点内容（人话接口）", "基础科学",
     "蝙蝠的回声定位（生物声呐）：①**原理**——喉部发出超声波（频率超 20 千赫，"
     "人耳听不见），声波碰到昆虫/障碍物反弹，耳朵接收回波——**从发声到听到"
     "回波的时间差算距离**，双耳时间差/音强差算方向，回波多普勒频移算目标"
     "速度；②**性能恐怖**——暗房里毫秒级定位并拦截小昆虫，可在密集障碍物"
     "中穿行不碰壁；发声可达每秒 200 次脉冲（临捕获前加速「终末蜂鸣」）；③"
     "**避噪本领**——能从上万只同伴的嘈杂回波中识别自己的（「鸡尾酒会效应」"
     "动物版）；④**仿生应用**——人类雷达与声呐的灵感来源之一，盲人回声定位"
     "训练（弹舌听回声）也是同一原理；⑤**代价**——超高声波发射与听觉系统"
     "耗能大，蝙蝠听力范围特化，多数视力退化（但不是全部——大蝙蝠主要靠"
     "视力与嗅觉）。",
     ["蝙蝠为什么能夜间飞行", "回声定位是什么", "蝙蝠靠什么避开障碍物",
      "超声波是什么", "声呐的原理", "雷达灵感来源"],
     ["问超声医学影像", "问蝙蝠生态保护"],
     "atomic", "",
     "蝙蝠回声定位=喉发超声波(>20kHz人耳不可闻)+回波时间差测距/双耳差定向/"
     "频移测速+毫秒级捕虫+每秒200脉冲终末蜂鸣+嘈杂中识别自己回波+仿生雷达"
     "声呐+盲人弹舌定位同原理。"),
    ("kp_card_honeycomb",
     "蜂巢的六边形之谜",
     "数学通识知识点内容（人话接口）", "数学",
     "蜂巢为什么是六边形：①**问题本质**——用固定周长的材料围出最大面积"
     "（或围出固定面积用材料最省）且能无缝铺满平面；②**淘汰赛**——圆面积"
     "最大但圆与圆拼接有缝隙浪费；正三角形/正方形/正六边形都能无缝铺满"
     "（仅这三种正多边形可密铺），其中**等面积时正六边形周长最短**——六"
     "边形是「材料最省冠军」；③**数学证明**——1999 年数学家黑尔斯证明"
     "「蜂窝猜想」（任何分割平面的方式中，正六边形网格总周长最短）；④"
     "**对比**——正三角形密铺周长约为六边形的 1.2 倍，正方形约 1.05 倍，"
     "蜂蜡消耗差异被千万年进化放大；⑤**人类借鉴**——蜂窝板材料（轻且抗压"
     "）/蜂窝网络基站布局/航天器隔热板，都抄了蜜蜂的作业；⑥**蜂窝内细节**"
     "——巢房底面是三个菱形拼成的尖底，菱形角度固定约 109°/70°，被证明"
     "是最省蜡的尖底设计。",
     ["蜂巢为什么是六边形", "蜜蜂怎么知道建六边形", "蜂窝结构省材料吗",
      "蜂窝猜想", "正六边形密铺", "仿生学蜂巢应用"],
     ["问蜜蜂分工", "问其他昆虫巢穴结构"],
     "atomic", "",
     "蜂巢六边形=等面积正多边形中周长最短(最省蜡)+能无缝密铺的正多边形仅"
     "三角/四边/六边形三种+1999黑尔斯证明蜂窝猜想+巢房三菱形尖底109°/70°"
     "最省蜡+人类抄作业(蜂窝板/基站布局/航天隔热板)。"),
]

QUESTIONS = [
    ("QB-929", "蝙蝠夜间飞行靠什么避开障碍物和捕捉昆虫？什么是回声定位？",
     "基础科学", "技术直答",
     ["超声波", "回波", "时间差", "声呐"], "通识拓展246"),
    ("QB-930", "蜂巢为什么建成六边形？这种结构有什么好处？", "数学", "技术直答",
     ["六边形", "周长", "密铺", "省料"], "通识拓展246"),
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
                               "level:L2", "status:verified", "batch:通识拓展246"],
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
    bank["version"] = "v5.17"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
