# -*- coding: utf-8 -*-
"""seed_common_248_cards.py · 通识拓展批次248知识卡+题库（幂等）

248：科技-GPS导航定位原理/生活-拉链的结构原理
KCCS 四要素+题干原句触发词。预检已过（QB-935/936+双id可用）。
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
    ("kp_card_gps",
     "GPS导航定位原理",
     "科技通识知识点内容（人话接口）", "科技",
     "GPS（全球定位系统）工作原理：①**星座构成**——约 24 颗以上工作卫星在"
     "约 2 万公里高空 6 个轨道面运行，保证全球任意地点任意时刻可见 4 颗以上；"
     "②**定位本质=测距交会**——手机接收卫星信号，用「信号传播时间×光速」"
     "算出与每颗卫星的距离，三颗卫星的三个球面相交出位置点；③**为什么是 "
     "4 颗**——接收器时钟远不如卫星原子钟精准，第 4 颗卫星用来解算时钟"
     "误差（时间差 1 微秒=定位差 300 米）；④**原子钟**——星载铯/铷原子钟"
     "精度达数十亿年差 1 秒，相对论效应（卫星时钟因高速+弱引力每天快约 38 "
     "微秒）必须修正，否则定位每天漂移约 10 公里；⑤**民用精度**——约 3-10 "
     "米，差分增强（地基/星基增强站播发误差修正）可达厘米级（测绘/无人驾驶"
     "用）；⑥中国北斗/欧洲伽利略/俄罗斯格洛纳斯同原理，多系统联合可见卫星"
     "更多精度更高。",
     ["GPS是怎么定位的", "导航卫星工作原理", "为什么至少要4颗卫星",
      "GPS精度是多少", "北斗和GPS一样吗", "相对论对GPS的影响"],
     ["问军用加密信号", "问室内定位技术"],
     "atomic", "",
     "GPS=24+卫星2万km六轨道保任意点见4颗+测距交会(时间×光速三球面相交)"
     "+第4颗解算接收器钟差(1微秒=300米)+星载原子钟+相对论修正日快38微秒"
     "否则漂10km+民用3-10米差分厘米级+北斗伽利略同原理。"),
    ("kp_card_zipper",
     "拉链的结构原理",
     "生活通识知识点内容（人话接口）", "生活常识",
     "拉链咬合的巧思：①**核心=凸凹齿交错咬合**——两条链带上各有一排带"
     "凸嘴/凹嘴的小齿，拉头把一侧齿的凸嘴压进另一侧齿的凹嘴，像无数微型"
     "卡扣连续扣紧；②**拉头双导槽**——拉头前窄后宽：入口端斜面把两排齿"
     "「挤」到一起咬合（Y 字形导槽），反向端则把咬合齿逐渐「掰」开——一"
     "个拉头兼任「装配工」和「拆卸工」；③**自锁**——咬合后的齿受拉力时"
     "力沿齿的斜面分解为压紧分力，拉力越大咬得越紧（斜面楔紧原理），垂直"
     "方向的小拉力不会让它自己脱开；④**历史**——1893 年贾德森申请「滑动"
     "锁紧装置」专利，1913 年桑巴克改进出可靠咬合齿，一战起用于军装/钱袋；"
     "⑤**常见故障**——滑牙多因齿被线头卡住或拉头导槽被撑变形（用钳子轻夹"
     "拉头两侧可恢复咬合力）。",
     ["拉链是什么原理", "拉链为什么拉上不会自己开", "拉链齿怎么咬合的",
      "拉链发明", "拉链滑牙怎么办", "拉头结构"],
     ["问工业拉链标准", "问防水拉链工艺"],
     "atomic", "",
     "拉链=凸凹齿交错咬合微型卡扣+拉头双导槽(入口挤合Y形槽/反向掰开一物"
     "两用)+斜面楔紧自锁(拉力越大咬越紧)+1893专利1913改进+滑牙=夹拉头"
     "恢复咬合。"),
]

QUESTIONS = [
    ("QB-935", "GPS是怎么定位的？为什么至少需要4颗卫星？", "科技", "技术直答",
     ["测距", "卫星", "4颗", "时钟"], "通识拓展248"),
    ("QB-936", "拉链是什么原理？为什么拉上后不会自己打开？", "生活常识", "技术直答",
     ["咬合", "拉头", "斜面", "自锁"], "通识拓展248"),
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
                               "level:L2", "status:verified", "batch:通识拓展248"],
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
    bank["version"] = "v5.19"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
