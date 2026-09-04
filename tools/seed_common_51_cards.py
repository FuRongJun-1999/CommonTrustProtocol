# -*- coding: utf-8 -*-
"""seed_common_51_cards.py · 通识拓展批次51知识卡+题库（幂等）

51：物理学-密度/化学-化学肥料/生物学-反射弧/生活常识-苹果削皮变色
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_density",
     "密度：单位体积的质量",
     "基础科学知识点内容（人话接口）", "物理学",
     "密度（ρ）=质量÷体积（ρ=m/V，单位 kg/m³ 或 g/cm³，1g/cm³=1000kg/m³），是"
     "物质本身的特性——与物体大小形状无关。经典问题「一斤铁和一斤棉花哪个重」："
     "一样重（质量相同）；「同样体积铁和棉花」：铁重（铁密度约 7.9g/cm³ 远大于"
     "棉花）。水的密度是 1.0×10³kg/m³（即 1g/cm³，1 升水恰好 1 千克）——物体密"
     "度小于水就漂浮（冰约 0.9，所以浮）。应用：鉴别物质（测密度对照表）、航空用"
     "轻质合金、选种（饱满种子密度大下沉）。温度会小幅影响密度（热胀冷缩），气体"
     "密度受温度压强影响显著。",
     ["铁和棉花哪个重", "密度的公式和单位", "冰为什么浮在水面上",
      "水的密度是多少", "密度能鉴别物质吗", "一升水是多少千克"],
     ["问密度混合计算", "问阿基米德原理衔接"],
     "atomic", "",
     "密度 ρ=m/V 是物质特性(与形状无关)；铁 7.9 vs 棉花极小；水=1g/cm³(1L=1kg)；ρ<水→浮(冰 0.9)；应用=鉴别/选种/航空材料。"),
    ("kp_card_fertlizer",
     "化学肥料：氮磷钾",
     "基础科学知识点内容（人话接口）", "化学",
     "农作物需要量最大的三种营养元素——氮（N）、磷（P）、钾（K），对应三大肥"
     "料：①氮肥（尿素/铵盐）——促进枝叶繁茂（「长叶子」），缺氮叶色发黄植株矮"
     "小；②磷肥（过磷酸钙等）——促进根系发达、开花结果（「长根和花果」），缺磷"
     "植株暗绿无光泽；③钾肥（氯化钾/草木灰主要成分 K₂CO₃）——茎秆粗壮抗倒伏、"
     "抗病虫害（「长茎秆」），缺钾叶尖焦枯。复合肥：同时含两种以上营养元素（如磷"
     "酸二铵）。注意：化肥过量使用导致土壤板结与水体富营养化（蓝藻爆发）——要"
     "与农家肥（有机肥）配合施用。铵态氮肥不能与碱性物质（草木灰/熟石灰）混用"
     "（放出氨气损失肥效）——常考。",
     ["庄稼缺氮肥会怎样", "氮磷钾肥的作用", "草木灰是什么肥料",
      "什么是复合肥", "化肥用多了有什么坏处", "铵态氮肥为什么不能和草木灰混用"],
     ["问光合作用与养分关系", "问有机农业"],
     "atomic", "",
     "三大肥：氮长叶(缺则黄矮)/磷长根花果/钾长茎秆抗倒伏(草木灰=K₂CO₃)；复合肥≥2 营养元素；过量→板结+富营养化；铵态氮肥忌混碱(氨气逸失)。"),
    ("kp_card_reflexarc",
     "反射弧：缩手反射的秘密",
     "基础科学知识点内容（人话接口）", "生物学",
     "手碰到烫的东西会先缩手后感觉疼——因为缩手反射的中枢在**脊髓**（不经大脑"
     "，速度快），痛觉信号随后才传到大脑皮层。反射弧五环节：感受器（皮肤感受刺"
     "激）→传入神经→神经中枢（脊髓）→传出神经→效应器（肌肉收缩）——五者缺一"
     "反射就不能完成。反射分两类：非条件反射（生来就有，如缩手/眨眼/膝跳，中枢"
     "在脊髓或脑干）与条件反射（后天学习获得，如「望梅止渴」——中枢在大脑皮层，"
     "人类特有的还有语言文字相关反射）。膝跳反射是最简单的反射（只有两个神经元"
     "），体检敲髌韧带小腿前踢即它。",
     ["缩手反射的神经中枢在哪里", "为什么先缩手后感觉疼", "反射弧包括哪五个部分",
      "什么是条件反射", "望梅止渴是什么反射", "膝跳反射的原理"],
     ["问大脑皮层功能区", "问激素与神经调节对比"],
     "atomic", "",
     "缩手反射中枢在脊髓→先缩手后觉疼；反射弧五环=感受器→传入→中枢→传出→效应器(缺一不可)；非条件(天生·脊髓)/条件(习得·大脑皮层·望梅止渴)。"),
    ("kp_card_applebrow",
     "苹果削皮后为什么变色",
     "生活常识知识点内容（人话接口）", "生活常识",
     "苹果削皮或咬开后很快变褐色——是氧化反应：果肉细胞里的多酚类物质（酚类）"
     "与多酚氧化酶接触空气中的氧气，氧化聚合成褐色的醌类物质（酶促褐变）。变色的"
     "苹果可以吃（只是口感外观变差），营养略降。防变色方法：①隔绝氧气——淡盐"
     "水/柠檬水浸泡（维生素C 是抗氧化剂且酸性抑制酶活性）、密封保鲜膜冷藏；②高"
     "温使酶失活（焯水，但苹果不适用）。同类现象：香蕉/土豆/梨削开后变褐、绿茶变"
     "红；反向利用：红茶的发酵、巧克力的褐色都是「美拉德/酶促褐变」的正面应用。 "
     "柠檬汁护色就是靠维生素 C（抗坏血酸）抢先被氧化。",
     ["苹果削皮后为什么会变色", "变色苹果还能吃吗", "怎么防止苹果变色",
      "柠檬水为什么能护色", "什么是酶促褐变", "土豆切开后变黑是什么原因"],
     ["问抗氧化剂食品工业", "问维生素C化学性质"],
     "atomic", "",
     "苹果变褐=多酚+多酚氧化酶+O₂ 酶促褐变(生成醌类)，可吃；防=柠檬水/盐水泡(VC 抗氧化+抑酶)·密封冷藏；土豆变黑同理；红茶巧克力=褐变的正向利用。"),
]

QUESTIONS = [
    ("QB-337", "铁和棉花哪个重", "物理学", "技术直答",
     ["密度", "一样重"], "通识拓展51"),
    ("QB-338", "庄稼缺氮肥会怎样", "化学", "技术直答",
     ["叶黄", "矮小"], "通识拓展51"),
    ("QB-339", "缩手反射的神经中枢在哪里", "生物学", "技术直答",
     ["脊髓"], "通识拓展51"),
    ("QB-340", "苹果削皮后为什么会变色", "生活常识", "技术直答",
     ["氧化"], "通识拓展51"),
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
                               "level:L2", "status:verified", "batch:通识拓展51"],
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
    bank["version"] = "v1.43"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
