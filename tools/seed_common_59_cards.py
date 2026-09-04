# -*- coding: utf-8 -*-
"""seed_common_59_cards.py · 通识拓展批次59知识卡+题库（幂等）

59：物理学-大气压强/化学-锂电池/生物学-内分泌腺与胰岛素/地理学-中国的世界文化遗产
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_atmpress",
     "大气压强",
     "基础科学知识点内容（人话接口）", "物理学",
     "大气对浸在其中的物体有压强（大气压强，约 1.013×10⁵ 帕）——证明实验：1654 "
     "年马德堡半球实验（16 匹马才拉开两个抽成真空的铜半球）；标准大气压数值由托"
     "里拆利用水银柱测出（760mm 汞柱≈76cm）。大气压的应用与现象：吸管喝饮料（吸"
     "气降低管内气压，大气压把饮料压上来）、吸盘挂钩、钢笔吸墨水、高压锅（增大气"
     "压提高沸点）、真空压缩袋。海拔越高大气压越低（高原上水约 80 多度就沸腾、山"
     "顶气压只有平原的约一半）；大气压还随天气变化（晴高阴低）。流速与压强：流体"
     "流速越大压强越小（飞机机翼升力/两船不能并行/喷雾器原理）——伯努利原理。",
     ["大气压强是怎么发现的", "马德堡半球实验", "吸管为什么能吸上饮料",
      "海拔越高大气压越低吗", "流体压强与流速的关系", "飞机的升力原理"],
     ["问托里拆利实验细节", "问 Bernoulli 应用题"],
     "atomic", "",
     "大气压≈1.013×10⁵Pa：马德堡半球(1654)证明·托里拆利测值(760mmHg)；应用=吸管/吸盘/高压锅；海拔升气压降；流速大压强小(伯努利·机翼升力)。"),
    ("kp_card_libattery",
     "锂电池：化学能与电能",
     "基础科学知识点内容（人话接口）", "化学",
     "锂电池是现代社会的「能量心脏」：放电时化学能→电能（锂离子从负极经电解液"
     "移向正极、电子走外电路），充电时逆转。锂是最轻的金属、电极电势最负——能量"
     "密度最高（是铅酸电池的 5-6 倍），所以手机/笔记本/电动车全用它。两大类：锂"
     "原电池（一次性，纽扣电池）与锂离子电池（可充放电，无记忆效应）。中国掌握全"
     "产业链（宁德时代/比亚迪全球前列），新能源汽车爆发带动电池技术竞赛：磷酸铁"
     "锂（安全便宜·比亚迪刀片）vs 三元锂（能量密度高·宁德时代）；固态电池是下一"
     "代方向（更安全更高密度）。安全注意：过充/穿刺/高温可能热失控起火（电动车起"
     "火别用水泼，用干粉/大量水持续降温按消防指引处理）。",
     ["锂电池放电时能量怎么转化", "锂为什么适合做电池", "磷酸铁锂和三元锂的区别",
      "什么是固态电池", "电动车起火怎么办", "电池有记忆效应吗"],
     ["问原电池电化学原理", "问钠电池前景"],
     "atomic", "",
     "锂电=化学能⇄电能(锂离子正负极迁移)；锂最轻最负→能量密度最高(铅酸 5-6 倍)；磷酸铁锂(安全)vs 三元锂(高密)；固态=下一代；热失控禁乱泼水。"),
    ("kp_card_endocrine",
     "内分泌腺与胰岛素",
     "基础科学知识点内容（人话接口）", "生物学",
     "内分泌腺没有导管，分泌物（激素）直接进入血液运往全身——「化学信使」调节"
     "生命活动。人体主要内分泌腺与激素：①垂体（大脑底部，「内分泌之王」——生长"
     "激素，幼年过少=侏儒症、过多=巨人症、成年过多=肢端肥大症）；②甲状腺（喉部"
     "——甲状腺激素，促进发育代谢，幼年缺乏=呆小症，缺碘致地方性甲状腺肿「大脖"
     "子病」）；③胰岛（散布在胰腺中——胰岛素，唯一**降**血糖的激素，缺乏→糖尿"
     "病，需注射胰岛素——口服会被消化分解）；④肾上腺/性腺。激素调节特点：量少"
     "而作用大、通过血液运输、与神经调节共同构成人体调节网络（神经为主导）。",
     ["胰岛素由哪个器官分泌", "生长激素过多会怎样", "大脖子病缺什么",
      "糖尿病为什么要注射胰岛素而不是口服", "什么是内分泌腺", "激素调节的特点"],
     ["问血糖调节负反馈", "问激素与酶的区别"],
     "atomic", "",
     "内分泌腺无导管·激素入血：垂体(生长激素·侏儒/巨人)/甲状腺(缺碘大脖子·呆小症)/胰岛(胰岛素=唯一降血糖·糖尿病须注射)；量少效大；神经主导+激素协同。"),
    ("kp_card_wcheritage",
     "中国的世界文化遗产",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国的世界遗产总数约 59 项（截至 2024 年居世界前列），分三类：文化遗产、"
     "自然遗产、文化与自然双遗产。代表文化遗产：长城、故宫（1987 首批）、莫高"
     "窟、秦始皇陵及兵马俑坑、周口店北京人遗址、泰山（中国首个世界文化与自然双"
     "遗产，1987）、苏州园林、颐和园、天坛、丽江古城、平遥古城、大运河、良渚古"
     "城遗址（2019，实证中华五千年文明史）。自然遗产：九寨沟、黄龙、武陵源、三"
     "江并流、四川大熊猫栖息地、梵净山（2018）。双遗产：泰山、黄山、峨眉山-乐山"
     "大佛、武夷山。近年新增：泉州（2021）、普洱景迈山古茶林（2023，全球首个茶"
     "主题）、北京中轴线（2024）。",
     ["中国的世界文化遗产有哪些", "泰山是什么类型的世界遗产",
      "良渚古城遗址证明了什么", "中国第一项世界遗产", "北京中轴线申遗成功是哪年",
      "景迈山古茶林"],
     ["问申遗流程与意义", "问遗产保护与旅游平衡"],
     "atomic", "",
     "中国世遗约 59 项(三类)：文化=长城故宫莫高窟良渚(2019·实证五千年)；自然=九寨沟梵净山；双遗产=泰山(1987 首个)黄山峨眉武夷；2024 北京中轴线。"),
]

QUESTIONS = [
    ("QB-369", "大气压强是怎么发现的", "物理学", "技术直答",
     ["马德堡半球", "托里拆利"], "通识拓展59"),
    ("QB-370", "锂电池放电时能量怎么转化", "化学", "技术直答",
     ["化学能", "电能"], "通识拓展59"),
    ("QB-371", "胰岛素由哪个器官分泌", "生物学", "技术直答",
     ["胰岛", "胰腺"], "通识拓展59"),
    ("QB-372", "中国的世界文化遗产有哪些", "地理学", "技术直答",
     ["长城", "故宫", "莫高窟"], "通识拓展59"),
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
                               "level:L2", "status:verified", "batch:通识拓展59"],
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
    bank["version"] = "v1.51"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
