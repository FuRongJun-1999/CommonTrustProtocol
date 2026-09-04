# -*- coding: utf-8 -*-
"""seed_common_72_cards.py · 通识拓展批次72知识卡+题库（幂等）

72：物理学-晶体与非晶体/化学-地壳元素丰度/生物学-生物的基本特征/历史-安史之乱
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_crystal",
     "晶体与非晶体",
     "基础科学知识点内容（人话接口）", "物理学",
     "固体分两类：**晶体**有固定熔点（熔化时温度保持不变——冰 0℃、食盐 801℃、"
     "金属、海波、石英、萘）；**非晶体**没有固定熔点（熔化过程温度持续上升、逐"
     "渐变软变稀——蜡、玻璃、松香、沥青、橡胶）。本质区别：晶体内部粒子排列有"
     "规则（原子/分子周期性排列成晶格——雪花六角形/食盐立方体是宏观体现），非晶"
     "体排列无序。晶体熔化曲线有一段「水平段」（吸热但温度不变——能量用于破坏晶"
     "格而非升温），非晶体曲线平滑无水平段。同素异形对照：水晶（晶体 SiO₂）vs 石"
     "英玻璃（非晶体 SiO₂）成分相同结构不同。晶体还有各向异性（不同方向导热导电"
     "不同），非晶体各向同性。",
     ["冰是晶体吗", "晶体和非晶体的区别", "哪些是晶体哪些是非晶体",
      "玻璃为什么没有固定熔点", "晶体熔化时温度变吗", "雪花的六角形怎么来的"],
     ["问熔化凝固图像判读", "问晶格与空间点阵"],
     "atomic", "",
     "晶体=有固定熔点(冰0℃/盐/金属·熔化温度不变·粒子规则排列·各向异性)；非晶体=无熔点渐变软(蜡玻璃松香沥青)；熔化水平段=破晶格不升温；水晶vs石英玻璃同成分异结构。"),
    ("kp_card_crustelem",
     "地壳中的元素丰度",
     "基础科学知识点内容（人话接口）", "化学",
     "地壳中元素含量（质量分数）前四位：**氧（O，约 48.6%）＞硅（Si，约 26.3%）"
     "＞铝（Al，约 7.7%）＞铁（Fe，约 5%）**——口诀「养(氧)闺(硅)女(铝)贴(铁)"
     "」，氧硅合计约四分之三。含量最多的金属元素是**铝**（第二是铁）——「金属王"
     "国老大是铝」是常考易错点（很多人以为铁）。地壳中的存在形式：氧和硅主要构成"
     "硅酸盐（岩石/黏土/沙子的主体——二氧化硅即石英/沙）；钙钠钾镁在长石云母中；"
     "活泼金属都以化合物形式存在（金/铂等不活泼金属才有单质——狗头金）。元素含"
     "量对比记忆：生物细胞中最多的是氧（约 65%，水多）其次碳；空气中最多的是氮；"
     "海水中最多也是氧（水）。",
     ["地壳中含量最多的元素", "地壳中含量最多的金属", "养闺女贴口诀",
      "地壳中氧和硅占多少", "铝在地壳中以什么形式存在", "生物细胞中含量最多的元素"],
     ["问元素丰度宇宙对比", "问矿石冶炼难度关联"],
     "atomic", "",
     "地壳前四=氧(48.6%)＞硅(26.3%)＞铝(7.7%)＞铁(5%)——口诀养闺女贴；最多金属=铝(非铁)；氧硅=硅酸盐(岩石沙主体)；活泼金属成化合物·金银有单质；细胞/空气/海水各有其最。"),
    ("kp_card_lifefeat",
     "生物的基本特征",
     "基础科学知识点内容（人话接口）", "生物学",
     "判断「是不是生物」的基本特征：①生活需要营养（植物光合自养/动物捕食异"
     "养）；②能进行呼吸（绝大多数需要氧气）；③能排出体内废物（出汗/呼出 CO₂/"
     "排尿，植物落叶）；④能对外界刺激作出反应——应激性（含羞草合拢/向日葵向"
     "阳/草履虫避开盐滴）；⑤能生长和繁殖；⑥都有遗传和变异的特性（种瓜得瓜+一"
     "母生九子）；⑦除病毒外都由细胞构成。机器人/钟乳石「生长」/珊瑚骨骼不属于生"
     "物（珊瑚是生物，珊瑚骨骼不是）；病毒介于生命与非生命之间（必须寄生活细胞"
     "才表现生命活动）。非生物不具以上全部特征——甄别组合拳。",
     ["生物的基本特征有哪些", "含羞草合拢说明什么", "病毒是生物吗",
      "钟乳石长大为什么不是生物", "应激性是什么", "机器人算生物吗"],
     ["问病毒结构特殊性", "问生命起源假说"],
     "atomic", "",
     "生物七特征=需营养/呼吸/排废物/应激性(含羞草·向日葵)/生长繁殖/遗传变异/细胞构成(病毒除外·寄生态)；机器人钟乳石珊瑚骨骼非生物；病毒=临界态。"),
    ("kp_card_anhistory",
     "安史之乱",
     "人文通识知识点内容（人话接口）", "历史",
     "安史之乱（755-763）：唐朝由盛转衰的转折点。起因：唐玄宗晚年怠政宠杨贵妃，"
     "边将安禄山身兼范阳/平卢/河东三镇节度使拥兵 20 万，与宰相杨国忠争权——755"
     " 年以「讨杨国忠」为名起兵，「渔阳鼙鼓动地来」。经过：叛军迅速攻陷洛阳、长"
     "安，玄宗仓皇奔蜀，马嵬驿兵变（将士杀杨国忠、逼死杨贵妃）；太子李亨灵武即"
     "位（唐肃宗）。郭子仪、李光弼率军平叛，并借回纥兵；安禄山被其子安庆绪所"
     "杀、史思明杀安庆绪复叛、又被其子史朝义杀（「安史」二代相续），763 年叛乱"
     "平定。影响：北方经济破坏、人口锐减；藩镇割据开始；经济重心开始南移；藩镇"
     "割据+宦官专权+党争埋下唐亡祸根。白居易《长恨歌》咏叹此段。",
     ["安史之乱的发动者是谁", "安史之乱是哪一年到哪一年", "马嵬驿兵变",
      "安史之乱的影响", "渔阳鼙鼓动地来", "安禄山史思明的关系"],
     ["问藩镇割据演化", "问唐代经济重心南移"],
     "atomic", "",
     "安史之乱 755-763：安禄山(三镇节度使)史思明父子相续叛乱；节点=马嵬驿(杨贵妃死)/玄宗奔蜀/肃宗灵武即位/郭子仪平叛；影响=藩镇割据·经济南移·唐转衰。"),
]

QUESTIONS = [
    ("QB-421", "冰是晶体吗", "物理学", "技术直答",
     ["是", "固定熔点"], "通识拓展72"),
    ("QB-422", "地壳中含量最多的金属", "化学", "技术直答",
     ["铝"], "通识拓展72"),
    ("QB-423", "生物的基本特征有哪些", "生物学", "技术直答",
     ["营养", "呼吸", "繁殖", "应激性"], "通识拓展72"),
    ("QB-424", "安史之乱的发动者是谁", "历史", "技术直答",
     ["安禄山", "史思明"], "通识拓展72"),
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
                               "level:L2", "status:verified", "batch:通识拓展72"],
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
    bank["version"] = "v1.64"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
