# -*- coding: utf-8 -*-
"""seed_common_89_cards.py · 通识拓展批次89知识卡+题库（幂等）

89：物理学-液体压强/化学-影响溶解性的因素/生物学-细菌真菌病毒对比/地理学-中国山脉走向
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_liqpress",
     "液体压强的特点",
     "基础科学知识点内容（人话接口）", "物理学",
     "液体压强的特点（p=ρgh）：①对容器**底部和侧壁**都有压强；②**随深度增加而"
     "增大**（深海鱼被捞上来会「爆炸」——体内外压差；水坝上窄下宽）；③同一深度"
     "向**各个方向**压强相等；④同一深度，**密度越大压强越大**（同一深度盐水>"
     "清水）。重要辨析：液体压强只与深度（到液面的竖直距离）和液体密度有关，与"
     "容器形状、液体总量**无关**——帕斯卡裂桶实验：细长管里仅几杯水就把坚固木桶"
     "压裂（深度大）。连通器（communicator 呼应）是液体压强的应用。潜水员的深度"
     "限制（普通潜水约 60m）、深海潜艇需耐压壳（蛟龙号 7000 米承受约 700 个大气"
     "压）都是应对液体压强。",
     ["液体压强的特点", "液体压强与什么因素有关", "水坝为什么上窄下宽",
      "帕斯卡裂桶实验", "深海鱼捞上来为什么会死", "液体压强与容器形状有关吗"],
     ["问 p=ρgh 计算题", "问连通器复习"],
     "atomic", "",
     "液体压强 p=ρgh：随深度增大/同深各向相等/与容器形状总量无关(帕斯卡裂桶·几杯水裂桶)；水坝上窄下宽；蛟龙号 7000m≈700atm 耐压壳。"),
    ("kp_card_solubility",
     "影响溶解性的因素",
     "基础科学知识点内容（人话接口）", "化学",
     "物质的溶解性由什么决定：①**溶质和溶剂的性质**（内因——「相似相溶」：食盐"
     "溶于水不溶于油；碘几乎不溶于水却易溶于酒精——碘酒）；②**温度**（外因：多"
     "数固体溶解度随温度升高而增大——硝酸钾急剧/食盐缓增；**氢氧化钙（熟石灰）反"
     "而减小**——温度高石灰水更「弱」；气体溶解度随温度升高**减小**（烧开水冒泡"
     "）、随压强增大增大（汽水高压溶 CO₂））。重要辨析：**搅拌只能加快溶解速"
     "率，不能增大溶解度**（溶解度是 100g 水中最多溶解的克数——是性质不是过程）。"
     "溶解度曲线应用：提纯方法——溶解度受温度影响大的用**降温结晶**（硝酸钾提"
     "纯），受温度影响小的用**蒸发结晶**（食盐水提盐）。",
     ["影响溶解性的因素", "搅拌能增大溶解度吗", "气体的溶解度与温度关系",
      "硝酸钾和食盐溶解度曲线", "降温结晶和蒸发结晶怎么选", "氢氧化钙溶解度随温度"],
     ["问溶解度曲线判读", "问混合物提纯综合"],
     "atomic", "",
     "溶解性内因=溶质溶剂性质·外因=温度(固多数升大·熟石灰反小·气体升小压大)；搅拌=只加速率不改溶解度；提纯=温度敏感用降温结晶(硝钾)/不敏感用蒸发结晶(食盐)。"),
    ("kp_card_microbecmp",
     "细菌、真菌、病毒的对比",
     "基础科学知识点内容（人话接口）", "生物学",
     "三类微生物核心对比：①**病毒**——无细胞结构（蛋白质+核酸），必须寄生活细"
     "胞，离开活细胞变结晶；②**细菌**——单细胞原核生物（无成形细胞核），分裂繁"
     "殖，异养或自养；③**真菌**——真核生物（有成形的细胞核），多数多细胞（蘑菇"
     "菌丝），孢子繁殖，异养（腐生/寄生）。共同点：都没有叶绿体、不能自己制造有"
     "机物（营养方式均为异养或寄生腐生——与植物的本质区别）；都有细胞壁（病毒除"
     "外——连细胞都没有）。鉴别意义：感冒（病毒）吃抗生素无效；脚气（真菌）用抗"
     "真菌药；伤口感染（细菌）用抗生素——对症下药的前提是认清「谁在作怪」。三者"
     "在生态系统中多担任**分解者**（病毒为寄生者）。",
     ["细菌真菌病毒的区别", "病毒没有细胞结构对吗", "细菌和真菌哪个有细胞核",
      "抗生素能杀病毒吗", "三者营养方式的共同点", "什么是原核生物"],
     ["问微生物与疾病对应", "问发酵微生物归类"],
     "atomic", "",
     "对比：病毒=无细胞(蛋白+核酸·寄生)；细菌=原核(无核膜·分裂繁殖)；真菌=真核(有核·孢子繁殖)；共性=无叶绿体异养/多为分解者；用药=病毒抗生素无效。"),
    ("kp_card_mountains",
     "中国主要山脉的走向",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国主要山脉走向三大类：①**东北—西南走向**（三列，从东向西）：台湾山脉—"
     "长白山—武夷山；大兴安岭—太行山—巫山—雪峰山；长白山西侧的大兴安岭与内蒙"
     "古高原/黄土高原/华北平原的分界——第三级阶梯界线即大兴安岭—太行山—巫"
     "山—雪峰山；②**东西走向**（三列，从北向南）：天山—阴山；昆仑山—秦岭；南"
     "岭——「三横」，秦岭是中国最重要的地理分界线；③**西北—东南走向**：阿尔泰"
     "山、祁连山；④**南北走向**：横断山脉、贺兰山；⑤弧形山脉：喜马拉雅山脉（世"
     "界最高，主峰珠穆朗玛 8848.86m）。山脉构成地形骨架：两侧=高原盆地或平原（太"
     "行山：西侧黄土高原、东侧华北平原；昆仑山：北塔里木盆地、南青藏高原）。",
     ["中国东北西南走向的山脉有哪些", "东西走向的山脉三列", "秦岭是什么走向",
      "喜马拉雅山脉的走向", "太行山脉两侧是什么地形", "中国地形骨架"],
     ["问山脉与地形区搭配", "问阶梯分界山脉复习"],
     "atomic", "",
     "山脉走向：东北-西南三列(台湾长白武夷/大兴安岭太行巫山雪峰)=阶梯界线；东西三列(天阴/昆秦/南岭)；西北-东南(祁连)；南北(横断)；弧形=喜马拉雅(8848.86m)。"),
]

QUESTIONS = [
    ("QB-489", "液体压强的特点", "物理学", "技术直答",
     ["深度", "密度"], "通识拓展89"),
    ("QB-490", "影响溶解性的因素", "化学", "技术直答",
     ["温度", "溶质", "溶剂"], "通识拓展89"),
    ("QB-491", "细菌真菌病毒的区别", "生物学", "技术直答",
     ["细胞核", "细胞结构"], "通识拓展89"),
    ("QB-492", "中国东北西南走向的山脉有哪些", "地理学", "技术直答",
     ["大兴安岭", "太行山", "武夷山"], "通识拓展89"),
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
                               "level:L2", "status:verified", "batch:通识拓展89"],
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
    bank["version"] = "v1.81"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
