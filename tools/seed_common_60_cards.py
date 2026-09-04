# -*- coding: utf-8 -*-
"""seed_common_60_cards.py · 通识拓展批次60知识卡+题库（幂等）

60：物理学-光的色散/化学-海水淡化/生物学-根瘤菌固氮/历史-淝水之战
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_dispersion",
     "光的色散与彩虹",
     "基础科学知识点内容（人话接口）", "物理学",
     "白光（太阳光）是复色光，由红橙黄绿蓝靛紫七种色光混合而成——1666 年牛顿用"
     "三棱镜把它分解开来，这就是**色散**：不同颜色的光在玻璃中折射程度不同（紫"
     "光偏折最大、红光最小），所以被「拆开」。彩虹是天然的色散：雨后空气悬浮的"
     "小水滴像无数小棱镜，阳光进入水滴折射-反射-再折射，不同色光折向不同方向——"
     "所以彩虹总是出现在太阳的**对面**（背对太阳才看得到），内紫外红。人工彩虹："
     "背着阳光喷水雾即可。相关：三棱镜分光用于光谱分析（每种元素有特征光谱——"
     "宇宙中恒星的成分就是靠光谱「读」出来的）。红光波长最长→穿透力强→交通灯用"
     "红、雾灯黄。",
     ["彩虹是怎么形成的", "什么是光的色散", "牛顿的三棱镜实验",
      "为什么彩虹在太阳对面", "红光为什么穿透力强", "光谱分析是什么"],
     ["问红外线紫外线应用", "问光的波长频率表"],
     "atomic", "",
     "色散=白光(复色)经棱镜分解七色(1666 牛顿)：紫偏折最大红最小；彩虹=水滴折射反射·太阳对面·内紫外红；光谱分析读恒星成分；红光波长长穿透强。"),
    ("kp_card_desalination",
     "海水淡化",
     "基础科学知识点内容（人话接口）", "化学",
     "地球 97.5% 的水是海水，淡水仅 2.5%——海水淡化是人类水资源的重要出路。主"
     "要方法：①蒸馏法——加热海水让水蒸发再冷凝收集（最古老，中东大量使用，可"
     "利用电厂余热；耗能高）；②反渗透膜法——对海水加压，水分子透过半透膜、盐离"
     "子被截留（现代主流，能耗比蒸馏低，与「渗透」方向相反故名反渗透）；③电渗"
     "析/冷冻法等。中国最大海水淡化基地在天津、青岛等地；沙特约 70% 饮用水靠淡"
     "化。淡化水成本已降至每吨几元，但仍高于自来水——主要用于沿海缺水城市与岛"
     "屿（如西沙永兴岛）。副产浓盐水需妥善排放（防破坏海洋生态）。",
     ["海水淡化的方法有哪些", "什么是反渗透", "淡化海水能喝吗",
      "哪些国家靠海水淡化生活", "海水淡化为什么耗能", "中国哪里用海水淡化"],
     ["问半透膜原理", "问水资源危机对策"],
     "atomic", "",
     "海水 97.5%·淡水仅 2.5%；淡化=蒸馏法(古老耗能)与反渗透膜法(主流·加压透水截盐)；沙特 70% 饮用靠淡化；中国天津青岛/西沙永兴岛；浓盐水生态排放注意。"),
    ("kp_card_rhizobium",
     "根瘤菌：大豆为什么能肥田",
     "基础科学知识点内容（人话接口）", "生物学",
     "大豆、花生等豆科植物的根上长着许多小瘤——根瘤，里面住着**根瘤菌**：它能把"
     "空气中植物无法直接利用的氮气（N₂）转化为含氮养料（固氮作用），与植物「共"
     "生」——植物供给它糖类「口粮」，它供给植物氮肥，双赢。所以种过豆科植物的土"
     "壤更肥（留下的根瘤相当于施过氮肥），轮作/间作（玉米与大豆间作）能少施肥还"
     "增产——「种豆肥田」的农业智慧。全球工业固氮（合成氨，哈伯法）耗能巨大，而"
     "生物固氮常温常压高效完成——仿生固氮是农业科研热点。其他固氮者：土壤中的固"
     "氮菌、与满江红共生的蓝藻（古代稻田天然肥料）。",
     ["大豆为什么能肥田", "什么是根瘤菌", "生物固氮是什么",
      "玉米和大豆间作的好处", "共生关系是什么", "哈伯法固氮"],
     ["问豆科植物种类", "问微生物肥料前景"],
     "atomic", "",
     "根瘤菌与豆科共生：固 N₂→含氮养料(植物供糖互惠)——种豆肥田/豆禾间作省肥；工业哈伯法固氮耗能巨大·生物常温常压；蓝藻满江红同款。"),
    ("kp_card_feishui",
     "淝水之战：风声鹤唳",
     "人文通识知识点内容（人话接口）", "历史",
     "淝水之战（383 年）：东晋以约 8 万北府兵大败前秦苻坚号称百万（实约 80 余"
     "万）大军——中国历史上著名的以少胜多战役。成语之源：苻坚骄傲轻敌，登城望"
     "晋军齐整「草木皆兵」；溃退时士兵闻风声鹤唳以为追兵（「风声鹤唳」）；谢安"
     "下棋淡定「小儿辈大破贼」。战术关键：晋军请求秦军后撤让出决战场地，苻坚想"
     "趁半渡而击下令后撤——结果阵脚一乱，降将大喊「秦军败了」，全军崩溃。影响："
     "前秦瓦解北方再度分裂；东晋稳住江南，南北朝对峙格局延续。投鞭断流（苻坚战"
     "前狂言）也出自此役——四大成语：投鞭断流/草木皆兵/风声鹤唳/东山再起（谢安"
     "隐居东山）。",
     ["风声鹤唳草木皆兵出自哪场战役", "淝水之战双方是谁", "以少胜多的战役",
      "投鞭断流是什么意思", "谢安是谁", "淝水之战的影响"],
     ["问赤壁官渡对比", "问南北朝格局"],
     "atomic", "",
     "淝水之战 383：东晋 8 万北府兵 vs 前秦苻坚 80 余万——撤阵自乱崩溃；四成语=投鞭断流/草木皆兵/风声鹤唳/东山再起(谢安)；影响=南北对峙延续。"),
]

QUESTIONS = [
    ("QB-373", "彩虹是怎么形成的", "物理学", "技术直答",
     ["色散", "折射", "水滴"], "通识拓展60"),
    ("QB-374", "海水淡化的方法有哪些", "化学", "技术直答",
     ["蒸馏", "反渗透"], "通识拓展60"),
    ("QB-375", "大豆为什么能肥田", "生物学", "技术直答",
     ["根瘤菌", "固氮"], "通识拓展60"),
    ("QB-376", "风声鹤唳草木皆兵出自哪场战役", "历史", "技术直答",
     ["淝水之战"], "通识拓展60"),
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
                               "level:L2", "status:verified", "batch:通识拓展60"],
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
    bank["version"] = "v1.52"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
