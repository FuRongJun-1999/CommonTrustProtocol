# -*- coding: utf-8 -*-
"""seed_common_332_cards.py · 通识拓展批次332知识卡+题库（幂等）

332：科技-蓝牙与Wi-Fi无线连接/科技-无线充电原理
KCCS 四要素+题干原句触发词。预检已过（QB-1235/1236+双id可用）。
注：雷达QB-435仿生角度、电磁波QB-628已有，本批取无线连接技术角度。
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
             "Dijkstra", "Bellman", "Floyd", "logV", "Bluetooth",
             "GHz", "Qi"}


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
    ("kp_card_bluetooth",
     "蓝牙与无线连接",
     "科技通识知识点内容（人话接口）", "科技",
     "蓝牙是怎么「连」的：①**蓝牙**——2.4GHz 频段短距离无线通信（一般"
     "10 米内），设备配对后点对点/小网络传数据（耳机/手环/键盘）——名字"
     "来自 10 世纪统一丹麦的国王「蓝牙哈拉尔」（寓意统一各协议）；②"
     "**Wi-Fi**——2.4/5GHz 频段无线局域网（覆盖几十至百米，速率高），"
     "负责大流量上网；③**分工**——蓝牙省电低速传小数据（耳机听歌/传感器"
     "），Wi-Fi 高速传大数据（视频下载），互补而非竞争；④**近场技术家族**"
     "——NFC（几厘米，刷公交/门禁/支付）、红外（老电视遥控，需对准直线）"
     "——距离越近越安全省电；⑤**配对原理**——首次配对交换密钥建立加密"
     "通道（防第三方窃听），之后自动重连；⑥**省电设计**——蓝牙低功耗"
     "（BLE）让手环/耳机续航数天到数月。",
     ["蓝牙是什么原理", "蓝牙和Wi-Fi的区别", "NFC是什么",
      "蓝牙名称由来", "无线连接技术", "蓝牙低功耗"],
     ["问蓝牙耳机连接问题", "问智能家居协议"],
     "atomic", "",
     "蓝牙=2.4GHz短距10米省电低速传小数据(耳机手环)+名取自丹麦统一国王"
     "+Wi-Fi无线局域网高速大流量互补+NFC厘米级刷公交门禁+配对交换密钥"
     "加密防窃听+BLE低功耗续航数天。"),
    ("kp_card_wirelesscharge",
     "无线充电原理",
     "科技通识知识点内容（人话接口）", "科技",
     "不插线也能充电：①**主流=电磁感应**——充电板内的线圈通交流电产生"
     "交变磁场，手机内线圈「感应」出电流（法拉第电磁感应定律）——两个"
     "线圈像没有电线的变压器；②**Qi 标准**——无线充电联盟统一协议（"
     "不同品牌通用的关键）；③**效率与距离**——感应式充电距离极近（几"
     "毫米，紧贴充电板），能量传输效率 70-80%（比有线损耗大，发热明显）"
     "；磁共振式可隔空几厘米但效率再降；④**功率现状**——手机常用 "
     "15-50W（慢于有线快充），电动汽车无线充电在推广（停车即充）；⑤"
     "**辐射疑虑**——近距离非电离电磁场，功率可控对健康无害（远低于"
     "安全限值）；⑥**便利与代价**——随手一放免插拔（减少接口磨损）"
     "换来的是速度慢+发热+挑设备。",
     ["无线充电是什么原理", "无线充电伤电池吗", "Qi标准",
      "无线充电效率", "电磁感应充电", "无线充电有辐射吗"],
     ["问反向无线充电", "问远场无线输电"],
     "atomic", "",
     "无线充电=电磁感应充电板线圈交变磁场→手机线圈感生电流(无线变压器)"
     "+Qi标准通用+距离毫米级效率70-80%发热+磁共振可隔空几厘米效率降+"
     "非电离辐射功率可控无害+免插拔省接口磨损换慢与热。"),
]

QUESTIONS = [
    ("QB-1235", "蓝牙是怎么工作的？蓝牙和Wi-Fi有什么区别？", "科技", "技术直答",
     ["蓝牙", "2.4GHz", "Wi-Fi", "低功耗"], "通识拓展332"),
    ("QB-1236", "无线充电是什么原理？它有辐射危害吗？", "科技", "技术直答",
     ["电磁感应", "线圈", "效率", "辐射"], "通识拓展332"),
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
                               "level:L2", "status:verified", "batch:通识拓展332"],
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
    bank["version"] = "v6.02"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
