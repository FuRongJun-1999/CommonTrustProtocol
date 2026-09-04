# -*- coding: utf-8 -*-
"""seed_common_73_cards.py · 通识拓展批次73知识卡+题库（幂等）

73：物理学-蒸发与沸腾/化学-燃料充分燃烧/生物学-植物的类群/历史-李自成起义
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_evapboil",
     "蒸发与沸腾：汽化的两种方式",
     "基础科学知识点内容（人话接口）", "物理学",
     "汽化的两种方式——蒸发与沸腾，都吸热。差异：①蒸发：**任何温度**下都能发"
     "生、只发生在液体**表面**、缓慢平和；②沸腾：达到**沸点**且继续吸热才发生、"
     "在液体**内部和表面同时**进行、剧烈（大量气泡上升破裂）。影响蒸发快慢的三"
     "因素：温度高、表面积大、空气流动快（晾衣服摊开/晒/通风的道理）。蒸发吸热"
     "有致冷作用：出汗降温、酒精擦身退烧、狗伸舌头（无汗腺靠唾液蒸发）、打针前"
     "擦酒精觉得凉。沸腾时温度不变（水的沸点 100℃/标准大气压）；「扬汤止沸」治"
     "标（暂时降温低于沸点），「釜底抽薪」治本（移走热源彻底停沸）。",
     ["蒸发和沸腾的异同", "影响蒸发快慢的因素", "为什么出汗能降温",
      "沸腾需要什么条件", "扬汤止沸和釜底抽薪", "酒精擦身退烧的原理"],
     ["问沸点气压关系复习", "问蒸发致冷计算"],
     "atomic", "",
     "汽化两式：蒸发(任何温度·仅表面·缓)vs 沸腾(沸点+吸热·内外同时·烈)；蒸发三因素=温度/面积/气流；蒸发吸热致冷(出汗/酒精擦身)；扬汤止沸治标·抽薪治本。"),
    ("kp_card_burnfull",
     "燃料充分燃烧的条件",
     "基础科学知识点内容（人话接口）", "化学",
     "燃料充分燃烧两个条件：①足够的**空气（氧气）**；②足够的**接触面积**（燃"
     "料与空气充分接触）。工程应用：锅炉把煤磨成粉（增大接触面积）、鼓风机送足"
     "空气；汽车发动机喷油雾化；烧柴架起来架空烧（比堆实烧旺）。不充分燃烧的代"
     "价：放热减少（浪费能源）+产生一氧化碳（中毒风险）和黑烟（碳颗粒污染）——"
     "灰渣多也说明烧不透。氢能源优势呼应：氢气热值高（同质量放热约为汽油 3 倍）"
     "且产物只有水。热值（q）=单位质量燃料完全燃烧放出的热量（J/kg）——是燃料"
     "的特性，与是否充分燃烧无关（不充分只是实际放热达不到理论值）。",
     ["燃料充分燃烧的条件", "为什么不充分燃烧会产生一氧化碳", "热值是什么",
      "锅炉为什么要把煤磨成粉", "氢气的热值", "架空烧柴为什么更旺"],
     ["问热值计算题", "问煤的综合利用"],
     "atomic", "",
     "充分燃烧=足氧+大接触面积(煤磨粉/喷雾/架空)；不充分=浪费热+CO 中毒+黑烟；热值 q=单位质量完全燃烧放热(燃料特性·氢最高)；同质量氢≈汽油 3 倍。"),
    ("kp_card_plantgroup",
     "植物的四大类群",
     "基础科学知识点内容（人话接口）", "生物学",
     "植物由低等到高等四大类群：①藻类植物——无根茎叶分化、大多水生（衣藻/水"
     "绵/海带紫菜），是大气氧的主要贡献者之一；②苔藓植物——有茎叶无根（假根）、"
     "无输导组织，矮小喜阴湿（葫芦藓/墙藓），可作监测空气污染的指示植物（叶只"
     "有一层细胞对 SO₂ 敏感）；③蕨类植物——有根茎叶分化+输导组织，孢子繁殖，"
     "古代蕨类变成今天的煤（石炭纪蕨类森林）；④种子植物——用种子繁殖，分裸子"
     "植物（种子裸露无果皮包被：松/杉/银杏——「白果」是种子非果实）与被子植物"
     "（种子有果皮包被、有真正的花，种类最多最高等——占植物界半数以上）。演化"
     "主线：水生→陆生、孢子→种子、无根茎叶→完善器官。",
     ["植物分为哪几类", "苔藓植物为什么矮小", "裸子和被子的区别",
      "煤是由什么植物变成的", "监测空气污染的指示植物", "白果是果实吗"],
     ["问孢子与种子对比", "问被子植物优势"],
     "atomic", "",
     "植物四群（低→高）：藻类(无根茎叶·产氧)→苔藓(茎叶无根·SO₂ 指示植物)→蕨类(根茎叶+输导·成煤)→种子(裸子松杉银杏·白果是种子/被子花+果皮·最高等)。"),
    ("kp_card_lizicheng",
     "李自成起义与明亡",
     "人文通识知识点内容（人话接口）", "历史",
     "李自成（1606-1645）：明末农民起义领袖，陕西米脂人，原为驿站驿卒（裁撤失"
     "业后投身起义——明末财政困难裁驿卒是导火索之一），绰号「闯王」（继承高迎"
     "祥）。口号「均田免赋」（分田地、不纳粮）深得民心，民间传唱「迎闯王，不纳"
     "粮」。1644 年 3 月建立大顺政权，年号永昌，随后攻入北京——崇祯帝在煤山（景"
     "山）自缢，明朝灭亡（276 年）。但进京后军纪迅速败坏，追赃助饷拷掠官员；山"
     "海关之战败于吴三桂引清军入关的联合兵力，退出北京，1645 年在湖北九宫山遇"
     "害。同时期张献忠转战四川（大西政权）。明亡清兴与全球小冰期气候（旱灾蝗灾"
     "饥荒）密切相关。",
     ["闯王是谁", "李自成是什么时候攻入北京的", "均田免赋是什么口号",
      "崇祯帝是怎么死的", "明朝是被谁灭亡的", "迎闯王不纳粮"],
     ["问吴三桂降清始末", "问明清鼎革全球背景"],
     "atomic", "",
     "李自成=闯王(驿卒出身·均田免赋·迎闯王不纳粮)：1644.3 建大顺攻入北京·崇祯煤山自缢·明亡(276 年)；山海关败于吴三桂+清军，1645 九宫山遇害；背景含小冰期灾荒。"),
]

QUESTIONS = [
    ("QB-425", "蒸发和沸腾的异同", "物理学", "技术直答",
     ["任何温度", "沸点", "表面"], "通识拓展73"),
    ("QB-426", "燃料充分燃烧的条件", "化学", "技术直答",
     ["空气", "接触面积"], "通识拓展73"),
    ("QB-427", "植物分为哪几类", "生物学", "技术直答",
     ["藻类", "苔藓", "蕨类", "种子植物"], "通识拓展73"),
    ("QB-428", "闯王是谁", "历史", "技术直答",
     ["李自成"], "通识拓展73"),
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
                               "level:L2", "status:verified", "batch:通识拓展73"],
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
                   "added": "2026-09-05"})
        added += 1
    bank["version"] = "v1.65"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
