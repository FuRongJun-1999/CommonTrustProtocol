# -*- coding: utf-8 -*-
"""seed_common_362_cards.py · 通识拓展批次362知识卡+题库（幂等）

362：科技-直升机为什么能垂直起降/科技-无人机（航空器新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1317/1318+双id可用）。
注：热气球QB-449已有，本批取旋翼飞行角度避让。
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
    ("kp_card_helicopter",
     "直升机为什么能垂直起降",
     "科技通识知识点内容（人话接口）", "科技",
     "直升机的飞行原理：①**升力来源=旋翼**——顶部大旋翼高速旋转切割"
     "空气产生升力（机翼旋转起来就不需要跑道滑跑加速）——可垂直起降和"
     "悬停；②**怎么前进**——旋翼周期性变距（前倾姿势）让升力向前倾斜"
     "分解出前进推力；③**尾桨的用途**——抵消机身反扭力（没有尾桨机身"
     "会反向打转），并可控制机头方向；④**操纵**——总距杆控制升力升降"
     "+周期变距杆控制前后左右+脚蹬控制尾桨转向——手脚并用；⑤**应用"
     "场景**——医疗救援（垂直起降不依赖机场）/消防灭火/电力巡线/山区"
     "运输/农林喷洒；⑥**特点**——灵活但速度（一般 250-300 km/h）与"
     "航程不如固定翼，振动大维护成本高。",
     ["直升机为什么能垂直起降", "直升机的原理", "尾桨有什么用",
      "直升机怎么前进", "直升机和飞机的区别", "直升机悬停"],
     ["问武装直升机", "问旋翼机对比"],
     "atomic", "",
     "直升机=顶部旋翼旋转切割空气产生升力可垂直起降悬停+周期变距前倾"
     "前进+尾桨抵消反扭力控方向+总距杆周期杆脚蹬手脚并用+救援消防巡线"
     "山区运输+灵活但速度航程不如固定翼振动大维护贵。"),
    ("kp_card_uav",
     "无人机",
     "科技通识知识点内容（人话接口）", "科技",
     "无人机（无人驾驶飞行器）：①**类型**——多旋翼（四轴最常见，悬停"
     "稳操作简单）/固定翼（航时长速度快，测绘巡检）/直升机式（载重大）；"
     "②**原理**——多旋翼靠不同电机转速差实现升降/偏航/前后左右倾斜"
     "（飞控芯片+陀螺仪+加速度计实时平衡，每秒校正数百次）；③**应用**"
     "——航拍影视/农业植保喷洒/电力巡线/测绘/物流快递（偏远地区试点）"
     "/应急救援搜救；④**法规**——实名登记+禁飞区（机场净空区/军事"
     "管理区/重点目标）/高度限制（微型机有豁免条款）；"
     "⑤**反无人机**——机场等重点区域有电子围栏+无线电干扰+捕获网"
     "技术；⑥**技术趋势**——自主避障/跟拍/AI 识别目标/编队飞行（"
     "灯光秀是集群控制展示）。",
     ["无人机是什么", "无人机怎么飞", "无人机有什么用途",
      "无人机禁飞区", "无人机航拍", "无人机编队"],
     ["问无人机法规细则", "问反无人机技术"],
     "atomic", "",
     "无人机=多旋翼(四轴悬停稳)/固定翼(航时长)/直升机式+电机转速差"
     "升降偏航倾斜+飞控陀螺仪加速度计每秒数百次校正+航拍植保巡线测绘"
     "物流救援+实名登记禁飞区真高120米+电子围栏反无人机+自主避障AI"
     "编队趋势。"),
]

QUESTIONS = [
    ("QB-1317", "直升机为什么能垂直起降和悬停？尾桨有什么用？", "科技", "技术直答",
     ["旋翼", "升力", "尾桨", "悬停"], "通识拓展362"),
    ("QB-1318", "无人机是怎么飞起来的？它有哪些应用场景？", "科技", "技术直答",
     ["多旋翼", "飞控", "航拍", "植保"], "通识拓展362"),
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
                               "level:L2", "status:verified", "batch:通识拓展362"],
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
    bank["version"] = "v6.27"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
