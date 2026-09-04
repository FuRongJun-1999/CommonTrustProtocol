# -*- coding: utf-8 -*-
"""seed_common_57_cards.py · 通识拓展批次57知识卡+题库（幂等）

57：物理学-热传递与内能/化学-一氧化碳/生物学-人的一生牙齿/历史-红军长征
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_heattrans",
     "热传递与内能",
     "基础科学知识点内容（人话接口）", "物理学",
     "内能是物体内部所有分子动能与分子势能的总和——一切物体都有内能（冰山冷水"
     "也有）。改变内能的两种方式：热传递与做功（等效）。热传递三方式：传导（固"
     "体，金属勺柄变热）、对流（液体气体，暖气循环）、辐射（不需介质，太阳晒"
     "暖）。热传递方向：热量自发从高温物体传向低温物体（温度相同即热平衡——热"
     "量不是温度！温度是分子运动剧烈程度、热量是传递中的能量）。做功改变内能：搓"
     "手取暖（机械能→内能）、开汽水盖冒白气（内能→机械能，气体对外做功降温）。"
     "保温瓶三重防热传递：真空夹层（断传导对流）、软木塞（断传导）、镀银面（反辐"
     "射）。",
     ["热传递的实质是什么", "改变内能有哪两种方式", "热传递有哪三种方式",
      "热量和温度有什么区别", "搓手为什么暖和", "保温瓶为什么能保温"],
     ["问比热容与吸放热计算", "问内燃机四冲程"],
     "atomic", "",
     "内能=分子动能+势能(一切物体都有)；改变内能=热传递+做功(等效)；三方式=传导/对流/辐射·自发高温→低温；热量≠温度；保温瓶=真空+木塞+镀银三断。"),
    ("kp_card_co",
     "一氧化碳：无形的杀手",
     "基础科学知识点内容（人话接口）", "化学",
     "一氧化碳（CO）是无色无味无刺激性的剧毒气体——「无形杀手」：它与血红蛋白"
     "的结合能力约是氧气的 200-300 倍，吸入后血红蛋白被「占座」无法携氧，人体缺"
     "氧中毒（头晕/恶心/昏迷甚至死亡，俗称煤气中毒）。来源：含碳燃料不完全燃"
     "烧（冬季煤炉取暖/燃气热水器装在浴室内/炭火火锅紧闭门窗都是高危场景）。急"
     "救：立即开窗通风、把中毒者移到空气新鲜处、重症送高压氧舱（高压纯氧加速排"
     "出 CO）。性质对照：CO 能燃烧（蓝色火焰，2CO+O₂→2CO₂，曾是水煤气成分）、有"
     "还原性（工业炼铁的还原剂）；CO₂ 无毒但不供呼吸——「CO 中毒、CO₂ 窒息」两"
     "码事。防 CO 中毒：通风！装一氧化碳报警器。",
     ["煤气中毒是一氧化碳吗", "一氧化碳中毒的原理", "煤气中毒怎么办",
      "一氧化碳和二氧化碳的区别", "一氧化碳有什么用途", "怎么预防煤气中毒"],
     ["问血红蛋白结构", "问炼铁还原反应"],
     "atomic", "",
     "CO=无色无味剧毒：与血红蛋白结合力是 O₂ 的 200-300 倍→缺氧（煤气中毒）；来源=不完全燃烧(煤炉/燃气热水器/炭盆紧闭)；急救=通风移人/高压氧舱；能燃有还原性(炼铁)。"),
    ("kp_card_teeth",
     "人的一生有两副牙齿",
     "基础科学知识点内容（人话接口）", "生物学",
     "人一生有两副牙齿：乳牙 20 颗（约 6 个月萌出第一颗，2-3 岁长齐）——6-12 岁"
     "乳牙陆续脱落换恒牙；恒牙 28-32 颗（28 颗基础+0-4 颗智齿，智齿 18 岁后萌出"
     "或终生不出）。恒牙一旦龋坏（蛀牙）脱落不再自己长出——蛀牙成因：口腔细菌分"
     "解食物残渣产酸腐蚀牙釉质（预防=早晚刷牙/少吃糖/含氟牙膏增强牙釉质）。牙"
     "齿按形态分工：切牙（切）、尖牙/犬齿（撕）、前磨牙/磨牙（磨碎咀嚼）。刷牙要"
     "领：巴氏刷牙法 45° 角、每次 2 分钟、半年洗牙检查一次。恒牙外伤脱落后可把"
     "牙含在舌下或泡牛奶里 30 分钟内就医再植。",
     ["人一生有几副牙齿", "乳牙和恒牙各多少颗", "智齿是什么",
      "蛀牙是怎么形成的", "恒牙掉了还会长吗", "怎么保护牙齿"],
     ["问牙釉质成分", "问正畸原理"],
     "atomic", "",
     "两副牙：乳牙 20 颗(6 月萌·3 岁齐)→恒牙 28-32(含智齿 0-4)；恒牙坏不再生；蛀牙=细菌产酸蚀釉质(预防=刷牙/少糖/氟)；分工=切/尖撕/磨磨。"),
    ("kp_card_longmarch",
     "红军长征",
     "人文通识知识点内容（人话接口）", "历史",
     "红军长征（1934.10-1936.10）：第五次反「围剿」失败后，中央红军（红一方面"
     "军）从江西瑞金出发实行战略转移。关键节点：1935 年 1 月**遵义会议**——确"
     "立毛泽东在党和红军的领导地位，是生死攸关的转折点；四渡赤水（机动歼敌）、"
     "巧渡金沙江、强渡大渡河、飞夺泸定桥、爬雪山（夹金山）过草地；1935 年 10 月"
     "中央红军到达陕北吴起镇；1936 年 10 月红军三大主力（红一/红二/红四方面军）"
     "在甘肃会宁会师——长征胜利结束。历时两年、纵横十一省、行程约二万五千里"
     "（中央红军）。意义：保存了革命骨干力量，实现战略转移，「长征是宣言书、宣"
     "传队、播种机」；长征精神成为精神谱系。湘江战役减员过半是出发初期最大损"
     "失。",
     ["红军长征从什么时候开始到什么时候结束", "遵义会议的意义",
      "飞夺泸定桥", "红军长征走了多少里", "长征三大主力在哪会师", "长征的原因"],
     ["问抗日民族统一战线", "问陕北根据地发展"],
     "atomic", "",
     "长征 1934.10 瑞金出发→1936.10 会宁三军会师(两年·十一省·二万五千里)；遵义会议(1935.1)=转折点确立毛泽东领导；节点=四渡赤水/金沙江/大渡河/泸定桥/雪山草地。"),
]

QUESTIONS = [
    ("QB-361", "热传递的实质是什么", "物理学", "技术直答",
     ["内能", "转移"], "通识拓展57"),
    ("QB-362", "煤气中毒是一氧化碳吗", "化学", "技术直答",
     ["是", "CO", "血红蛋白"], "通识拓展57"),
    ("QB-363", "人一生有几副牙齿", "生物学", "技术直答",
     ["两副", "乳牙", "恒牙"], "通识拓展57"),
    ("QB-364", "红军长征从什么时候开始到什么时候结束", "历史", "技术直答",
     ["1934", "1936"], "通识拓展57"),
]


def ensure_seed() -> dict:
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
                               "level:L2", "status:verified", "batch:通识拓展57"],
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

    bank = json.load(open(BANK, encoding="utf-8"))
    qs = bank["questions"]
    have = {q["id"] for q in qs}
    added = 0
    for qid, question, domain, qtype, keywords, source in QUESTIONS:
        if qid in have:
            continue
        qs.append({"id": qid, "question": question, "domain": domain,
                   "type": qtype, "keywords": keywords, "source": source,
                   "added": "2026-09-04"})
        added += 1
    bank["version"] = "v1.49"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
