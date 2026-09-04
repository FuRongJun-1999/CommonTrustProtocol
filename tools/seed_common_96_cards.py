# -*- coding: utf-8 -*-
"""seed_common_96_cards.py · 通识拓展批次96知识卡+题库（幂等）

96：物理学-水循环/化学-化学与生活/生物学-生命的起源/地理学-中国的自然灾害
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞——本批预检命中
kp_card_ecobalance（通识拓展07旧卡·生态平衡已覆盖），生物题改生命的起源。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_watercycle2",
     "自然界的水循环",
     "基础科学知识点内容（人话接口）", "物理学",
     "水循环的主要环节：**蒸发**（海洋/江河/植物蒸腾）→水汽**输送**（风把水汽带"
     "向内陆）→**降水**（雨雪冰雹）→**下渗**与**径流**（地表径流=江河、地下径"
     "流）→回到海洋——循环往复、永不停歇。动力：太阳辐射（蒸发与大气运动的能量"
     "来源）+重力（降水与径流）。意义：①维持全球水量平衡（海洋蒸发量≈降水量+江"
     "河补入量）；②塑造地表形态（流水侵蚀/堆积——黄土高原沟壑/三角洲）；③淡"
     "水资源不断补充更新（水是可再生资源的前提）；④调节气候。人类影响：植树造"
     "林增涵养、修水库调径流、过度开采地下水致地面沉降、城市硬化路面减少下渗（"
     "内涝原因之一——海绵城市理念）。",
     ["水循环的环节有哪些", "水循环的动力是什么", "海绵城市是什么",
      "水循环的意义", "城市内涝的原因", "地下径流和地表径流"],
     ["问三态变化衔接", "问水资源保护复习"],
     "atomic", "",
     "水循环环节=蒸发→输送→降水→下渗径流：动力=太阳+重力；意义=水量平衡/塑地貌/淡水更新/调节气候；人类=水库调径流·硬化致内涝→海绵城市。"),
    ("kp_card_chemlife",
     "化学与生活：无处不在的化学",
     "基础科学知识点内容（人话接口）", "化学",
     "化学与衣、食、住、行、医全面相关：**衣**——合成纤维（涤纶）与天然纤维（"
     "棉毛）、染料化学；**食**——食品添加剂（防腐剂苯甲酸钠/抗氧化剂 VC/甜味"
     "剂）、加碘盐、补铁酱油、馒头发酵的小苏打；**住**——水泥玻璃陶瓷（无机非金"
     "属）、涂料胶水（注意甲醛——新装修房通风）、铝合金门窗；**行**——汽油柴油"
     "（石油分馏产品）、锂电池车、飞机铝合金碳纤维；**医**——阿司匹林、青霉素、"
     "疫苗冷链、胃药氢氧化铝。化学是「中心科学」：连接物理、生物、材料、医学。正"
     "确观念：化学品不是「有毒」代名词——剂量决定毒性（毒理学基本原理），关键在"
     "合理使用与监管。",
     ["化学与生活有什么关系", "食品添加剂都有害吗", "甲醛来自哪里",
      "汽油是石油分馏的产品吗", "剂量决定毒性什么意思", "化学是一门什么学科"],
     ["问食品科学", "问新材料医学应用"],
     "atomic", "",
     "化学=中心科学：衣(合成纤维)食(添加剂/加碘盐)住(水泥涂料·甲醛通风)行(燃油锂电)医(阿司匹林青霉素)；剂量决定毒性——化学品≠有毒，关键合理使用。"),
    ("kp_card_liforigin",
     "生命的起源：原始海洋的化学进化",
     "基础科学知识点内容（人话接口）", "生物学",
     "化学进化假说（主流理论）：生命起源于 40 多亿年前的**原始海洋**，经历四个"
     "阶段：①无机小分子（甲烷/氨/水蒸气/氢/氰化氢）→生成有机小分子（氨基酸等）"
     "——能量来自闪电/紫外线/火山；②有机小分子聚合成生物大分子（蛋白质/核酸）；"
     "③大分子组装成多分子体系；④出现原始生命（能自我复制、代谢）。**米勒实验"
     "（1953）**：模拟原始大气（甲烷/氨/氢/水蒸气）火花放电一周，产生了氨基酸等"
     "有机小分子——为阶段①提供了有力支持（被誉为「生命起源研究里程碑」）。原始"
     "大气特点：无氧气（还原性大气）。其他假说：宇宙胚种论（陨石带来有机物——默"
     "奇森陨石含氨基酸）、深海热泉起源说（「黑烟囱」化能合成）。生命最早证据：约"
     " 38.5 亿年前（原核生物化石）。",
     ["生命起源于哪里", "米勒实验证明了什么", "原始大气有什么成分",
      "生命起源的化学进化过程", "什么是宇宙胚种论", "最早的生物出现在多少年前"],
     ["问外星生命探索", "问 RNA 世界假说"],
     "atomic", "",
     "化学进化四阶段(原始海洋·40 多亿年前)：无机小分子→有机小分子(米勒 1953 火花放电产氨基酸佐证)→生物大分子→多分子体系→原始生命；原始大气无氧；最早生命证据≈38.5 亿年。"),
    ("kp_card_disaster",
     "中国的自然灾害",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国自然灾害频繁（季风气候+板块交界+地形复杂），分两大类：**气象灾害**——"
     "干旱（最普遍，华北春旱/江淮伏旱）、洪涝（东部季风区夏秋，1998/2021 型流域"
     "性大水）、台风（东南沿海夏秋）、寒潮（冬半年，北方剧烈降温霜冻）、沙尘暴"
     "（春季西北华北）；**地质灾害**——地震（环太平洋带+地中海喜马拉雅带交界："
     "汶川 2008/唐山 1976）、滑坡、泥石流（山区暴雨诱发，西南山区多发）。分布规"
     "律：气象灾害东部季风区为主；地质灾害西南山区与板块边界。防灾减灾：监测预警"
     "体系（气象卫星/地震预警秒级系统）、工程措施（堤坝/防护林/抗震建筑）、应急"
     "演练与避难场所、救灾储备——「以防为主、防抗救结合」。",
     ["中国常见的自然灾害有哪些", "气象灾害和地质灾害", "中国地震多发的原因",
      "泥石流多发区在哪里", "防灾减灾的措施", "寒潮的影响"],
     ["问汶川地震复盘", "问预警技术与体系"],
     "atomic", "",
     "中国灾害两族：气象(干旱最普遍/洪涝/台风/寒潮/沙尘暴·季风区)+地质(地震·两带交界汶川唐山/滑坡泥石流·西南山区)；防=监测预警+工程+演练，以防为主。"),
]

QUESTIONS = [
    ("QB-517", "水循环的环节有哪些", "物理学", "技术直答",
     ["蒸发", "降水", "径流"], "通识拓展96"),
    ("QB-518", "食品添加剂都有害吗", "化学", "技术直答",
     ["不是", "剂量", "合理使用"], "通识拓展96"),
    ("QB-519", "米勒实验证明了什么", "生物学", "技术直答",
     ["无机小分子", "氨基酸", "原始大气"], "通识拓展96"),
    ("QB-520", "中国常见的自然灾害有哪些", "地理学", "技术直答",
     ["干旱", "洪涝", "地震", "台风"], "通识拓展96"),
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
                               "level:L2", "status:verified", "batch:通识拓展96"],
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
    bank["version"] = "v1.88"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
