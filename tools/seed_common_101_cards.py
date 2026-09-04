# -*- coding: utf-8 -*-
"""seed_common_101_cards.py · 通识拓展批次101知识卡+题库（幂等）

101：物理学-做功改变内能/化学-区分纯碱和小苏打/生物学-动物体的结构层次/地理学-中国主要油田
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_workinternal",
     "做功改变物体内能",
     "基础科学知识点内容（人话接口）", "物理学",
     "改变内能的两种方式之一是**做功**（另一种是热传递）：①对物体做功——物体内"
     "能增大（温度升高）：搓手取暖（摩擦生热）、反复弯折铁丝弯折处发热、压缩气体"
     "点火（压缩空气引火仪——急剧压缩筒内空气达棉花着火点）；②物体对外做功——"
     "内能减小（温度降低）：开汽水瓶盖「嘭」的一声瓶口出现白气（气体膨胀对外做"
     "功、内能减小温度降低、水蒸气液化）；火箭发射尾部白气同理。与热传递的区别："
     "热传递是能量**转移**（高温→低温），做功是能量**转化**（机械能⇄内能）——"
     "效果相同但本质不同（energy 呼应能量守恒）。",
     ["做功改变物体内能的例子", "搓手取暖的原理", "开汽水盖为什么冒白气",
      "压缩空气引火仪", "做功和热传递的区别", "对物体做功内能怎么变"],
     ["问热传递三方式复习", "问内燃机压缩冲程"],
     "atomic", "",
     "做功改内能=机械能⇄内能**转化**(热传递=转移)：对物做功升温(搓手/压缩点火)/对外做功降温(开汽水白气)；效果同热传递但本质不同。"),
    ("kp_card_distsoda",
     "区分纯碱和小苏打",
     "基础科学知识点内容（人话接口）", "化学",
     "纯碱（Na₂CO₃ 碳酸钠）与小苏打（NaHCO₃ 碳酸氢钠）都是白色固体、都显碱性，"
     "区分方法：①**加热法**——小苏打受热分解产生 CO₂（使澄清石灰水变浑浊），纯"
     "碱受热不分解（稳定）——最可靠；②加酸剧烈程度——两者遇酸都冒泡，但小苏打"
     "反应更剧烈（同质量产气多）；③滴加澄清石灰水——都变浑浊（无法区分）。烘焙"
     "选择：做馒头用小苏打或酵母（产气蓬松），纯碱碱性太强不能直接发面（发面用碱"
     "是中和老面发酵的酸）。用途区分：纯碱→玻璃/造纸/洗涤；小苏打→食品发酵/中"
     "和胃酸/清洁除垢（温和）。",
     ["怎么区分纯碱和小苏打", "小苏打加热会怎样", "纯碱受热分解吗",
      "做馒头用纯碱还是小苏打", "碳酸钠和碳酸氢钠的区别", "小苏打遇到酸会怎样"],
     ["问碳酸盐检验", "问发酵化学复写"],
     "atomic", "",
     "区分=加热法：小苏打 NaHCO₃ 受热分解放 CO₂(石灰水变浑)·纯碱 Na₂CO₃ 稳定；发面用小苏打/纯碱用于玻璃洗涤；小苏打遇酸更剧烈且中和胃酸温和。"),
    ("kp_card_bodylevels",
     "动物体的结构层次",
     "基础科学知识点内容（人话接口）", "生物学",
     "动物体的结构层次（由微观到宏观）：**细胞 → 组织 → 器官 → 系统 → 动物"
     "体**。①细胞——基本单位（受精卵分裂分化而来）；②组织——形态相似、结构和"
     "功能相同的细胞群（动物四大组织：上皮/肌肉/神经/结缔）；③器官——不同组织"
     "按一定次序组合（心脏=肌肉+神经+结缔+上皮组织构成）；④系统——能共同完成一"
     "种或几种生理功能的多个器官（消化/呼吸/循环/泌尿/神经/运动/内分泌/生殖八大"
     "系统）；⑤动物体——八大系统协调配合。植物体层次：细胞→组织→器官（根茎叶"
     "花果实种子六大器官）→植物体——**没有系统**这一层（植物与动物结构层次的最"
     "大区别）。最基本的生命系统：细胞；最大的生命系统：生物圈。",
     ["动物体的结构层次", "动物的四大组织", "植物和动物结构层次的区别",
      "心脏属于什么层次", "八大系统", "生命系统的基本单位"],
     ["问器官系统举例", "问植物层次对比表"],
     "atomic", "",
     "动物体五层=细胞→组织(上皮肌肉神经结缔)→器官→系统(八大)→个体；植物=细胞→组织→器官(六大)→个体·无系统层；细胞=最基本生命系统/生物圈=最大。"),
    ("kp_card_oilfield",
     "中国的主要油田",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国石油工业布局「北方为主、陆上起步、海上跟进」：①**大庆油田**（黑龙江松"
     "嫩平原）——中国最大油田（1959 年发现，铁人王进喜「宁肯少活二十年，拼命也要"
     "拿下大油田」），结束「中国贫油」论（李四光地质理论指导）；②胜利油田（山东"
     "东营，黄河三角洲）；③辽河油田、华北油田、中原油田；④西部新兴：塔里木油田"
     "（西气东输起点）、准噶尔（新疆）、长庆油田（陕甘宁，天然气主产区，现为国内"
     "第一大油气田）；⑤海上：渤海（蓬莱）、东海、南海（深海油气——蓝鲸一号可燃"
     "冰试采）。能源安全：对外依存度超 70%，加大勘探（深地工程——万米深井）与新"
     "能源替代并进。",
     ["中国最大的油田是大庆油田", "铁人王进喜", "李四光的贡献",
      "长庆油田在哪里", "西气东输的起点油田", "中国海上油田分布"],
     ["问能源对外依存度", "问深地钻井工程"],
     "atomic", "",
     "中国油田：最大历史=大庆(1959·王进喜·李四光理论破贫油论)/当前油气第一=长庆(陕甘宁)；西部=塔里木(西气东输源)准噶尔；海上=渤海南海(可燃冰试采)；对外依存 70%+。"),
]

QUESTIONS = [
    ("QB-537", "做功改变物体内能的例子", "物理学", "技术直答",
     ["搓手", "压缩", "白气"], "通识拓展101"),
    ("QB-538", "怎么区分纯碱和小苏打", "化学", "技术直答",
     ["加热", "分解"], "通识拓展101"),
    ("QB-539", "动物体的结构层次", "生物学", "技术直答",
     ["细胞", "组织", "器官", "系统"], "通识拓展101"),
    ("QB-540", "中国最大的油田是大庆油田", "地理学", "技术直答",
     ["对", "最大", "黑龙江"], "通识拓展101"),
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
                               "level:L2", "status:verified", "batch:通识拓展101"],
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
    bank["version"] = "v1.93"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
