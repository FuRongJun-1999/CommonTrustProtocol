# -*- coding: utf-8 -*-
"""seed_common_49_cards.py · 通识拓展批次49知识卡+题库（幂等）

49：物理学-摩擦起电与静电/化学-蛋白质/生物学-克隆羊多莉/地理学-季风
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_staticelec",
     "摩擦起电与静电",
     "基础科学知识点内容（人话接口）", "物理学",
     "用塑料梳子梳干燥的头发，头发会飘起来、梳子能吸小纸屑——摩擦使物体**带电"
     "**（摩擦起电）：电子从一个物体转移到另一个物体，失去电子的带正电、得到电"
     "子的带负电；带电体能吸引轻小物体。冬天脱毛衣噼啪响、碰门把手被「电」一下"
     "（放电）、加油站禁止拍打化纤衣物（电火花可引爆油气）都是静电。防静电：加"
     "湿（潮湿空气导走电荷）、摸墙/金属先放电、穿棉质衣物。雷电=云层摩擦积累的"
     "巨量电荷放电——避雷针把电导入大地。两个电荷规律：同种相斥、异种相吸。",
     ["冬天脱毛衣为什么会噼啪响", "什么是摩擦起电", "梳子为什么能吸小纸屑",
      "怎么防止静电", "避雷针的原理", "电荷之间的作用规律"],
     ["问验电器原理", "问导体绝缘体对比"],
     "atomic", "",
     "摩擦起电=电子转移(失正得负)·带电体吸轻小物；噼啪/被电=放电；雷电=云间巨量放电→避雷针导地；防静电=加湿/先摸金属；同斥异吸。"),
    ("kp_card_protein",
     "蛋白质：生命的物质基础",
     "基础科学知识点内容（人话接口）", "化学",
     "蛋白质是生命的物质基础：肌肉/毛发/酶/抗体/血红蛋白都是蛋白质（占人体干重"
     "约 45%）。它由氨基酸构成——人体需要约 20 种氨基酸，其中 8 种（婴儿 9 种）"
     "必需氨基酸自身不能合成、必须从食物摄取。优质蛋白来源：鸡蛋（氨基酸组成最"
     "接近人体）、牛奶、瘦肉、鱼、大豆（植物蛋白之王）。蛋白质变性：加热/强酸/"
     "酒精使其空间结构破坏而失活——煮熟的鸡蛋凝固、75% 酒精消毒（使病菌蛋白变"
     "性）都是这个原理（变性不可逆）。检测方法：灼烧闻焦毛味（合成纤维无此味）"
     "或双缩脲试剂变紫。每天推荐摄入约 1 克/公斤体重（成人 60-90 克）。",
     ["哪些食物富含蛋白质", "什么是必需氨基酸", "蛋白质变性是什么意思",
      "酒精消毒的原理和蛋白质有关吗", "怎么鉴别蛋白质纤维", "每天需要多少蛋白质"],
     ["问酶的催化机理", "问氨基酸结构通式"],
     "atomic", "",
     "蛋白质=生命基础(肌肉/酶/抗体)，由约20种氨基酸构成(8种必需需食补)；优质=蛋奶肉鱼豆；变性=结构破坏失活(煮蛋凝固/酒精消毒)不可逆。"),
    ("kp_card_dolly",
     "克隆羊多莉",
     "基础科学知识点内容（人话接口）", "生物学",
     "多莉（Dolly）是 1996 年诞生的第一只由成年体细胞克隆出的哺乳动物（英国罗斯"
     "林研究所，2003 年去世）：科学家把一只芬兰多塞特母羊的乳腺体细胞核，植入另"
     "一只羊的去核卵细胞，电激活后发育成胚胎，再移入第三只代孕母羊体内——多莉"
     "的基因与供核母羊几乎完全相同。意义：证明**高度分化的体细胞核**仍具有全能"
     "性（此前认为只有生殖细胞可以），开启克隆技术与再生医学时代。技术名词：体"
     "细胞核移植。克隆≠完全复制：线粒体 DNA 来自卵细胞供体、表观遗传与环境影响"
     "发育。我国克隆进展：克隆猴「中中」「华华」（2018，灵长类难题突破）。克隆人"
     "被全球伦理与法律禁止。",
     ["克隆羊多莉是怎么回事", "多莉羊有几个母亲", "什么是体细胞核移植",
      "克隆技术有什么用", "中国克隆了什么动物", "为什么禁止克隆人"],
     ["问胚胎干细胞", "问基因编辑伦理"],
     "atomic", "",
     "多莉=1996 首例体细胞克隆哺乳动物：供核(乳腺细胞)+去核卵+代孕三只羊参与；证明体细胞核全能性；线粒体 DNA/环境→非完全复制；中国 2018 克隆猴中中华华。"),
    ("kp_card_monsoon",
     "季风：随季节转向的风",
     "人文通识知识点内容（人话接口）", "地理学",
     "季风是大范围风向随季节显著改变的风，成因主要是海陆热力差异：陆地升温快降"
     "温也快、海洋相反——夏季陆地比海洋热，陆上热空气上升、海面气流补入（吹向"
     "陆地的夏季风：中国东部盛行东南风，温暖湿润带来雨季）；冬季陆地冷、高压控"
     "制，风从陆地吹向海洋（冬季风：西北风，寒冷干燥）。中国是典型季风气候区："
     "雨热同期（夏季高温多雨，利于水稻农业），但夏季风不稳定→旱涝灾害（南涝北"
     "旱/江淮梅雨与伏旱）。季风区与非季风区界线：大兴安岭—阴山—贺兰山—巴颜喀"
     "拉山—冈底斯山。印度西南季风（6-9 月）决定其农业命脉。",
     ["中国夏天为什么多吹东南风", "什么是季风", "季风的成因",
      "为什么中国雨热同期", "夏季风不稳定会怎样", "季风区与非季风区分界线"],
     ["问梅雨伏旱成因", "问全球季风分布对比"],
     "atomic", "",
     "季风=海陆热力差异致风向季节反转：夏东南风(陆热低压·暖湿雨季)/冬西北风(冷高压·干冷)；雨热同期利农业·夏季风不稳致旱涝；界线=大兴安岭—阴山—贺兰山等。"),
]

QUESTIONS = [
    ("QB-329", "冬天脱毛衣为什么会噼啪响", "物理学", "技术直答",
     ["静电", "摩擦起电"], "通识拓展49"),
    ("QB-330", "哪些食物富含蛋白质", "化学", "技术直答",
     ["鸡蛋", "牛奶", "肉", "豆"], "通识拓展49"),
    ("QB-331", "克隆羊多莉是怎么回事", "生物学", "技术直答",
     ["体细胞核移植", "克隆"], "通识拓展49"),
    ("QB-332", "中国夏天为什么多吹东南风", "地理学", "技术直答",
     ["季风", "海陆热力差异"], "通识拓展49"),
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
                               "level:L2", "status:verified", "batch:通识拓展49"],
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
    bank["version"] = "v1.41"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
