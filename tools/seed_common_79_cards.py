# -*- coding: utf-8 -*-
"""seed_common_79_cards.py · 通识拓展批次79知识卡+题库（幂等）

79：物理学-热气球升空/化学-原子结构/生物学-基因DNA染色体关系/地理学-中国气候特征
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞——本批预检命中
kp_card_telescope（通识拓展14旧卡·望远镜类型已覆盖），物理题换热气球升空。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_balloon",
     "热气球为什么能升空",
     "基础科学知识点内容（人话接口）", "物理学",
     "热气球升空原理：**热空气密度小于冷空气**——燃烧器加热球囊内空气，空气受"
     "热膨胀、部分逸出，囊内空气密度变小；当（球内热空气+球体装备总重）小于排开"
     "的冷空气重量（浮力）时，热气球上升。控制方法：加大火力升高（更轻）、让空"
     "气冷却或放气下降——不像飞机需要机翼速度，热气球垂直浮沉，随风飘行（水平方"
     "向靠找不同高度的风向层）。同源原理：孔明灯（古代热气球，三国诸葛亮传"
     "说）、加氢/氦的飞艇与气球（充轻气体）。热气球运动：1783 年法国孟格菲兄弟"
     "完成人类首次载人热气球飞行（比莱特兄弟飞机早 120 年）。",
     ["热气球为什么能升空", "热气球的原理", "孔明灯为什么会飞",
      "热气球怎么控制升降", "人类第一次载人飞行", "热气球和飞艇的区别"],
     ["问浮沉条件复习", "问阿基米德在气体中的应用"],
     "atomic", "",
     "热气球=热空气密度小于冷空气→浮力大于总重升空；控制=火力升降(随风飘行)；孔明灯=古代版；孟格菲兄弟 1783 首次载人(早飞机 120 年)；飞艇=充轻气体同源。"),
    ("kp_card_atomstr",
     "原子的结构",
     "基础科学知识点内容（人话接口）", "化学",
     "原子由居于中心的**原子核**（质子+中子）和核外**电子**组成：①质子——带正"
     "电，数目=核电荷数=原子序数（决定元素种类：1 个质子是氢、6 个是碳）；②中"
     "子——不带电（质子+中子≈质量）；③电子——带负电，在核外分层排布（质量极"
     "小，约质子 1/1836）。原子整体不显电性：质子数=电子数。原子极小（约 10⁻¹⁰"
     " 米），原子核更小（万分之一）——但集中了 99.9% 以上质量（「如教堂里的苍"
     "蝇」——卢瑟福语），电子云在「空旷」的空间运动。历史模型演进：道尔顿实心"
     "球→汤姆孙枣糕→卢瑟福核式（α 粒子散射实验——大部分穿过、少数大角度偏转"
     "证明核小而重）→玻尔分层轨道→现代电子云。",
     ["原子由什么构成", "质子数等于什么", "原子核和电子谁大",
      "卢瑟福α粒子散射实验", "原子为什么不带电", "原子模型怎么演变的"],
     ["问核外电子排布规律", "问同位素概念"],
     "atomic", "",
     "原子=原子核(质子+中子·99.9%质量)+核外电子；质子数=核电荷数=原子序数(定元素)=电子数(中性)；卢瑟福α散射证核式结构；模型演进=道尔顿→枣糕→核式→玻尔→电子云。"),
    ("kp_card_genetrio",
     "基因、DNA、染色体的关系",
     "基础科学知识点内容（人话接口）", "生物学",
     "三者从属关系：**染色体 ⊃ DNA ⊃ 基因**——染色体（细胞核中易被碱性染料染"
     "色的线状体）主要由 DNA 和蛋白质组成；DNA 是遗传信息的载体（双螺旋结构，"
     "1953 年沃森、克里克发现——分子生物学开端）；**基因是有遗传效应的 DNA 片"
     "段**——决定生物性状（单双眼皮/血型/豌豆高矮）的基本单位。形象比喻：染色"
     "体像「一本书」，DNA 是书中的「文字」，基因是表达具体意思的「句子/段落」。"
     "人的体细胞 23 对染色体约含 2-3 万个基因、30 亿碱基对（人类基因组计划 2003"
     " 年完成测序）。基因通过指导蛋白质合成控制性状（中心法则：DNA→RNA→蛋白"
     "质）。",
     ["基因和DNA什么关系", "染色体由什么组成", "DNA双螺旋是谁发现的",
      "人类基因组计划", "基因决定什么", "中心法则"],
     ["问 DNA 复制过程", "问显性隐性遗传"],
     "atomic", "",
     "染色体⊃DNA⊃基因(有遗传效应的 DNA 片段·定性状)；DNA 双螺旋=沃森克里克 1953；人 23 对染色体·2-3 万基因·30 亿碱基对(基因组计划 2003)；中心法则 DNA→RNA→蛋白质。"),
    ("kp_card_climatchina",
     "中国气候的两大特征",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国气候两大特征：①**气候复杂多样**——跨多个温度带（热带至寒温带）和干"
     "湿区（湿润/半湿润/半干旱/干旱），地形抬升加剧差异：海南终年夏装、黑龙江冬"
     "季零下 30℃、青藏高原终年低温；植被景观从雨林到荒漠齐全——一个国家装下了"
     "「从赤道到北极」的景观。②**季风气候显著**——冬夏季风交替（夏季东南风带来"
     "降水，冬季西北风干冷），雨热同期利于农业；但夏季风年际不稳定导致旱涝灾害"
     "频发（南涝北旱/1998/2021 型极端降水）。分界：大兴安岭—阴山—贺兰山—巴颜"
     "喀拉山—冈底斯山一线以东为季风区。比同纬度世界其他地区：中国冬季更冷（寒"
     "潮南下无屏障）、夏季更热（雨热同期优势）。",
     ["中国气候的主要特征", "为什么中国季风气候显著", "中国气候复杂多样",
      "季风区与非季风区分界线", "雨热同期对农业的好处", "为什么中国冬天比同纬度冷"],
     ["问秦岭淮河意义", "问中国干湿地区划分"],
     "atomic", "",
     "中国气候两特征=复杂多样(多温度带干湿区·地形加剧·一国装下赤道到北极景观)+季风显著(雨热同期利农·夏季风不稳致旱涝)；季风界=大兴安岭—阴山—贺兰山—巴颜喀拉—冈底斯。"),
]

QUESTIONS = [
    ("QB-449", "热气球为什么能升空", "物理学", "技术直答",
     ["热空气", "密度", "浮力"], "通识拓展79"),
    ("QB-450", "原子由什么构成", "化学", "技术直答",
     ["原子核", "电子", "质子", "中子"], "通识拓展79"),
    ("QB-451", "基因和DNA什么关系", "生物学", "技术直答",
     ["DNA片段"], "通识拓展79"),
    ("QB-452", "中国气候的主要特征", "地理学", "技术直答",
     ["季风", "复杂多样"], "通识拓展79"),
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
                               "level:L2", "status:verified", "batch:通识拓展79"],
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
    bank["version"] = "v1.71"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
