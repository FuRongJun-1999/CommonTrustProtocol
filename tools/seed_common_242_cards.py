# -*- coding: utf-8 -*-
"""seed_common_242_cards.py · 通识拓展批次242知识卡+题库（幂等）

242：生物-候鸟迁徙的导航能力/植物-含羞草的膨压运动
KCCS 四要素+题干原句触发词。预检已过（QB-917/918+双id可用）。
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
    ("kp_card_bird_migrate",
     "候鸟迁徙的导航能力",
     "生物通识知识点内容（人话接口）", "基础科学",
     "候鸟迁徙导航的多重罗盘：①**冠军选手**——北极燕鸥每年南北极往返约 7-9"
     " 万公里（一生飞行距离约等于往返月球三次），大斑蝶四代接力完成北美往返；"
     "②**地磁罗盘**——鸟类眼部含隐色素蛋白，能「看见」地磁场的方向分布"
     "（量子自旋效应），体内还有磁铁矿颗粒充当「生物指南针」；③**天体导航**"
     "——白天按太阳方位角+体内生物钟校时，夜间按北极星等星辰图案定位"
     "（园丁鸟能识别旋转星图中不动的中心点）；④**气味与地标**——海上鸟类"
     "靠气味地图回家，陆地鸟类记忆山脉海岸河流等地标；⑤**双重保障**——多"
     "种导航系统互相校验，单一系统失效（阴天/磁暴）不致迷路；⑥**能量管理**"
     "——出发前大量进食囤积脂肪（体重可增加四成），顺风起飞省油。",
     ["候鸟迁徙为什么不迷路", "鸟类怎么导航", "北极燕鸥飞多远",
      "鸟靠地磁场导航吗", "候鸟迁徙靠什么认路"],
     ["问鸟类环志科研方法", "问昆虫迁飞性"],
     "atomic", "",
     "候鸟导航=地磁罗盘(眼部隐色素量子效应+磁铁矿颗粒)+太阳星辰定位(生物钟"
     "校时)+气味地图与地标记忆+多重系统互校验防迷路+北极燕鸥年飞 7-9 万"
     "km+囤脂肪增重四成。"),
    ("kp_card_mimosa",
     "含羞草的膨压运动",
     "生物通识知识点内容（人话接口）", "基础科学",
     "含羞草「害羞」的科学原理：①**结构基础**——叶柄基部和小叶根部有膨大"
     "的「叶枕」，里面装满水分维持挺立；②**运动机制=膨压变化**——受触碰时"
     "电信号瞬间传到叶枕，细胞迅速排水失压，小叶成对闭合、叶柄下垂——不是"
     "肌肉收缩，是「放水泄压」；③**速度**——电信号传导约每秒 1-3 厘米，"
     "整片复叶闭合不到 1 秒（植物界少有的快速运动）；④**为什么进化出这本事"
     "**——防御假说为主：突然闭合吓退停落的昆虫+暴雨大风时收拢叶片减少"
     "水分蒸发和机械损伤；⑤**疲劳现象**——连续刺激后反应变慢直至「不再"
     "害羞」（叶枕水分来不及补充+离子泵泵水耗能），休息一段时间恢复；⑥"
     "**夜晚也「睡觉」**——光周期触发叶片夜间自动闭合（睡眠运动），与触碰"
     "无关。",
     ["含羞草为什么会害羞", "含羞草的原理", "碰含羞草叶子为什么合拢",
      "含羞草会累吗", "植物也会运动吗"],
     ["问捕蝇草夹闭机制", "问植物激素研究"],
     "atomic", "",
     "含羞草=叶枕膨压运动(触电信号→细胞排水失压→小叶闭合叶柄下垂[非肌肉]"
     ")+不到1秒+防御(吓退昆虫/风雨减少蒸发损伤)+连续刺激疲劳待恢复+光周期"
     "睡眠运动。"),
]

QUESTIONS = [
    ("QB-917", "候鸟迁徙几千公里为什么不迷路？它们靠什么导航？", "基础科学", "技术直答",
     ["地磁", "太阳", "星辰", "地标"], "通识拓展242"),
    ("QB-918", "含羞草被碰后为什么会合拢叶子？它会「累」吗？", "基础科学", "技术直答",
     ["叶枕", "膨压", "电信号", "疲劳"], "通识拓展242"),
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
                               "level:L2", "status:verified", "batch:通识拓展242"],
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
    bank["version"] = "v5.13"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
