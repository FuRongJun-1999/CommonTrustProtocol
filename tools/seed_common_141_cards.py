# -*- coding: utf-8 -*-
"""seed_common_141_cards.py · 通识拓展批次141知识卡+题库（幂等）

141：生活常识-衣物洗涤标识/历史学-西安事变/地理学-喀斯特地貌
KCCS 四要素+题干原句触发词。预检：洗涤标识零覆盖；西安事变零覆盖；对联卡
与诗词格律卡划界、喀斯特与巴西高原卡仅提及划界。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_carelabe",
     "衣物洗涤标识怎么看",
     "生活常识知识点内容（人话接口）", "生活常识",
     "水洗标五个基本符号（从上到下）：①**水洗槽**——可水洗，槽内数字=最高水"
     "温（30 表示 ≤30°C），手加点=只能轻柔手洗，打叉=不可水洗；②**三角形**—"
     "—可漂白，打叉=不可漂白（含氯漂白剂伤色伤纤维，白衣服发黄慎用）；③**正"
     "方形内圆圈**——可翻转烘干，圆内一点=低温烘干，打叉=不可烘干（高温收缩"
     "变形——羊毛衫缩成童装多因烘干）；④**熨斗**——可熨烫，点越多温度越高"
     "（一点=低温适合化纤/真丝，三点=高温适合棉麻），打叉=不可熨；⑤**圆圈**—"
     "—可干洗（圆圈字母=干洗剂种类），打叉=不可干洗。材质对应：羊毛/真丝=冷"
     "水轻柔或干洗（热水碱水缩水伤纤）；化纤=忌高温；棉麻=耐洗耐高温易皱。",
     ["衣服洗涤标识怎么看", "洗涤标签符号含义", "三角形标识是什么意思",
      "羊毛衫怎么洗", "衣服可以烘干吗", "不可干洗是什么标志"],
     ["问去渍技巧（墨渍油渍）", "问洗衣液选购"],
     "atomic", "",
     "水洗标五符号=水洗槽(数字=最高温·叉=不可洗)+三角(漂白·叉=禁氯漂)+方内圆(烘干·叉=禁烘防缩)+熨斗(点多温高·化纤低温棉麻高温)+圆圈(干洗)；羊毛真丝冷水轻柔/化纤忌高温/棉麻耐高热。"),
    ("kp_card_xianincident",
     "西安事变",
     "人文通识知识点内容（人话接口）", "历史学",
     "西安事变（双十二事变）：**1936 年 12 月 12 日**，国民党将领**张学良**（东"
     "北军）、**杨虎城**（十七路军）为劝谏蒋介石停止内战、一致抗日，在西安临潼"
     "华清池发动「兵谏」，扣留蒋介石。背景：九一八后日本步步侵华（华北事变民"
     "族危机加深），蒋介石仍坚持「攘外必先安内」围剿红军；中共抗日民族统一战"
     "线政策感召下东北军将士厌战。**和平解决**：中共派周恩来等赴西安调停，蒋"
     "介石被迫接受「停止内战、联共抗日」——事变的和平解决成为时局转换的枢纽："
     "十年内战基本结束，国共**第二次合作**初步形成，**抗日民族统一战线**初步"
     "建立。后果：张学良送蒋回宁被扣押软禁半个多世纪，杨虎城后被杀害——二人"
     "被誉为「民族的千古功臣」。",
     ["西安事变发生在哪一年", "西安事变的发动者是谁", "双十二事变",
      "西安事变和平解决的意义", "张学良杨虎城", "抗日民族统一战线"],
     ["问九一八事变详情", "问抗战具体战役"],
     "atomic", "",
     "西安事变=1936.12.12 张学良+杨虎城西安兵谏扣蒋逼其抗日；周恩来调停和平解决→十年内战基本结束+国共第二次合作+抗日民族统一战线初步形成=时局转换枢纽；张被囚半个世纪杨遇害，千古功臣。"),
    ("kp_card_karst",
     "喀斯特地貌",
     "人文通识知识点内容（人话接口）", "地理学",
     "喀斯特地貌（岩溶地貌）=可溶性岩石（**石灰岩**，主要成分碳酸钙）被含二氧"
     "化碳的水长期**溶蚀**形成的地貌——「水滴石穿」的化学版：CaCO₃+CO₂+H₂O"
     "→Ca(HCO₃)₂（可溶）。地表形态：峰林/峰丛/石林（云南路南石林）/天坑；地下"
     "形态：**溶洞**（广西桂林芦笛岩/贵州织金洞）、地下河；洞内沉淀景观：**钟"
     "乳石**（洞顶向下长）、**石笋**（洞底向上长）、两者相接成**石柱**——是含"
     "钙水滴析出碳酸钙逐年堆积（一百年长几毫米到几厘米）。中国分布：广西、贵"
     "州、云南最典型——「桂林山水甲天下」就是喀斯特峰林+漓江；贵州天眼 FAST"
     "就建在喀斯特天然洼坑里。影响：风景绝美但地表水易漏入地下（工程防渗/干旱"
     "），地面易塌陷。",
     ["喀斯特地貌是怎么形成的", "桂林山水是什么地貌", "钟乳石和石笋的区别",
      "溶洞是怎么形成的", "云南石林", "天坑是怎么来的"],
     ["问丹霞地貌（红色砂砾岩风化）", "问雅丹地貌（风蚀）"],
     "atomic", "",
     "喀斯特=石灰岩(CaCO₃)被含 CO₂ 水溶蚀：石林/峰林/天坑/溶洞地下河；钟乳石下垂+石笋上长相接成石柱（碳酸钙逐年沉淀）；桂黔滇最典型=桂林山水+贵州天眼选址天然洼坑；美则美矣易塌陷漏水。"),
]

QUESTIONS = [
    ("QB-687", "衣服洗涤标识上打叉的三角形和打叉的烘干符号分别是什么意思？", "生活常识", "技术直答",
     ["不可漂白", "漂白", "不可烘干", "烘干"], "通识拓展141"),
    ("QB-688", "西安事变发生在哪一年？由哪两位将领发动？和平解决有什么历史意义？", "历史学", "技术直答",
     ["1936", "张学良", "杨虎城", "抗日", "统一战线"], "通识拓展141"),
    ("QB-689", "喀斯特地貌是怎么形成的？桂林山水属于什么地貌？", "地理学", "技术直答",
     ["石灰岩", "溶蚀", "碳酸钙", "喀斯特", "水"], "通识拓展141"),
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
                               "level:L2", "status:verified", "batch:通识拓展141"],
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
    bank["version"] = "v4.14"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
