# -*- coding: utf-8 -*-
"""seed_common_181_cards.py · 通识拓展批次181知识卡+题库（幂等）

181：生活常识-雨天水滑效应/生活常识-冲奶粉的正确方法/生活常识-绿豆汤为什么变红
KCCS 四要素+题干原句触发词。三重预检：三主题双库零覆盖（牙龈出血命中
vitamins 卡、流感命中老卡弃选）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_hydroplane",
     "雨天行车与水滑效应",
     "生活常识知识点内容（人话接口）", "生活常识",
     "**水滑效应（水漂）**：雨天高速行驶时，轮胎来不及把积**水排开**，车轮浮"
     "在水膜上失去抓地力——刹车失灵、方向盘发飘，如同滑水板。**易发条件**："
     "时速高（积水+高速最易发生，约 80km/h 以上风险陡增）、积水深、胎纹磨"
     "浅。**发生水滑怎么办**：**松油门**让车自然减速、**握稳方向盘**保持直"
     "行——**切勿急刹车/猛打方向**（一旦恢复抓地力会瞬间失控甩尾）。**预防"
     "**：雨天减速（比平时慢 20-30%）、加大跟车距离（湿路刹车距离约干路的 "
     "1.5-2 倍）、保持**胎纹深度**（<1.6mm 必须换胎）与正常胎压、避开积水与"
     "车辙外深水。雨雾天还应开近光+示廓灯（视需要开雾灯），积水路段低速匀速"
     "通过防发动机进水。",
     ["雨天开车水滑效应", "高速积水路面怎么开车", "水滑了怎么办",
      "雨天刹车距离", "轮胎胎纹深度多少要换"],
     ["问电动车雨天安全（用电动车卡）", "问发动机进水维修"],
     "atomic", "",
     "水滑=高速+积水轮胎来不及排水浮在水膜失去抓地：发生=松油门握稳方向勿急刹急转；预防=减速 20-30%+跟车 1.5-2 倍+胎纹>1.6mm+避开积水；雨雾开近光示廓灯，积水低速匀速防发动机进水。"),
    ("kp_card_formula",
     "冲奶粉的正确方法",
     "生活常识知识点内容（人话接口）", "生活常识",
     "婴儿配方奶粉冲调要点：①**先加水后加粉**——先按刻度加足温水再加奶粉（先"
     "加粉后加水会导致浓度偏高——渗透压过高加重婴儿肾脏负担）；②**水温 40-"
     "50°C**（部分益生菌配方要求更低，看罐体说明）——过烫破坏益生菌与部分营"
     "养（维生素/活性蛋白），过凉难溶；③**水源**——烧开晾凉的的自来水或合格"
     "纯净水即可，**勿用矿泉水**（矿物质含量高增加婴儿肾负担）；④**摇匀方式"
     "**——双手夹紧奶瓶**水平搓滚**，勿上下猛摇（产生大量气泡，宝宝吸入致"
     "胀气吐奶）；⑤**现冲现喝**——常温放置超 2 小时弃用，喝剩的不能留下一顿"
     "（细菌繁殖快）；测温：滴手腕内侧不烫为宜。6 个月后仍需按说明冲调浓度，"
     "勿自作主张冲浓「更有营养」。",
     ["冲奶粉先加水还是先加粉", "冲奶粉水温多少度", "矿泉水能冲奶粉吗",
      "奶粉怎么摇匀不起泡", "冲好的奶粉能放多久"],
     ["问辅食添加", "问奶瓶消毒"],
     "atomic", "",
     "冲奶粉=先加水后加粉(浓度准确护肾脏)+40-50°C 温水(过烫毁益生菌)+烧开晾凉自来水勿矿泉水+双手搓滚匀勿猛摇(防气泡胀气)+现冲现喝 2h 弃；勿冲浓更有营养是误区。"),
    ("kp_card_mungbeansoup",
     "绿豆汤为什么煮着煮着变红了",
     "基础科学知识点内容（人话接口）", "化学",
     "绿豆汤颜色变化=**多酚类物质氧化**：绿豆皮富含多酚（抗氧化成分），煮的"
     "过程中多酚接触**氧气**被氧化聚合，汤色由绿变黄再变**红褐**——抗氧化活"
     "性也随之下降。**加速变红的因素**：①用**碱性水**（北方硬水 pH 高，可滴"
     "一点柠檬汁/白醋中和护色）；②用**铁锅**煮（多酚遇铁离子变深色——用砂"
     "锅/不锈钢/电压力锅）；③**敞开盖久煮**（氧气源源不断进入）。**想保持绿"
     "色**：盖盖煮、缩短煮制时间（8-10 分钟汤色碧绿时先喝汤）、纯净水煮。另"
     "注意：绿豆汤**不能当水喝**（多酚影响蛋白与药物吸收/低血压者大量喝头晕"
     "）、空腹大量喝伤胃；「绿豆汤解药」的说法被夸大，但服药前后 1-2 小时错"
     "开更稳妥。没变红的绿豆汤解暑（补充水分电解质）作用更佳。",
     ["绿豆汤为什么变红", "绿豆汤怎么煮是绿色的", "绿豆汤解药吗",
      "铁锅煮绿豆汤", "绿豆汤能天天喝吗"],
     ["问抗氧化食物", "问夏季解暑饮品"],
     "atomic", "",
     "绿豆汤变红=多酚氧化聚合（碱性水/铁锅/敞盖久煮加速）抗氧化下降；护色=盖盖短时煮+纯净水+柠檬汁中和+非铁锅；勿当水喝（碍药物吸收）、空腹大量伤胃，服药错开 1-2h；碧绿汤解暑更佳。"),
]

QUESTIONS = [
    ("QB-789", "雨天高速行驶发生「水滑效应」时应该怎么办？如何预防水滑？", "生活常识", "技术直答",
     ["松油门", "握稳", "勿急刹", "减速", "胎纹", "1.6mm"], "通识拓展181"),
    ("QB-790", "冲奶粉应该先加水还是先加粉？水温多少度合适？为什么不能用矿泉水？", "生活常识", "技术直答",
     ["先加水", "40-50度", "矿泉水", "肾脏", "搓滚", "气泡"], "通识拓展181"),
    ("QB-791", "绿豆汤煮着煮着为什么会变红？怎样煮能保持绿色？", "化学", "技术直答",
     ["多酚", "氧化", "碱性", "铁锅", "盖盖", "护色"], "通识拓展181"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    whitelist = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
                 "effect", "Additives"}
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{6,}", content):
            if word not in whitelist:
                problems.append((node[0], f"长英文词: {word}"))
    if problems:
        raise SystemExit(f"外文长词检测报警: {problems}")


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
                               "level:L2", "status:verified", "batch:通识拓展181"],
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
    bank["version"] = "v4.54"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
