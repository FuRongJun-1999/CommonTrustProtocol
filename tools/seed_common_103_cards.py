# -*- coding: utf-8 -*-
"""seed_common_103_cards.py · 通识拓展批次103知识卡+题库（幂等）

103：物理学-超声波与次声波/化学-四种基本反应类型/生物学-耳与听觉/地理学-世界的语言与宗教
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_ulinfra",
     "超声波与次声波",
     "基础科学知识点内容（人话接口）", "物理学",
     "人耳听不到的声波两大类：**超声波**（>20000Hz）——方向性好、穿透力强、在水"
     "中传播远：应用=声呐（潜艇/测深）、B超（医学成像，无创安全）、超声清洗（眼"
     "镜/精密仪器）、超声碎石（击碎肾结石）、雷达式倒车探测器。**次声波**"
     "（<20Hz）——波长长传播远、穿透强不易衰减：来源=地震/海啸/火山/台风/核爆"
     "炸；应用=监测自然灾害（次声仪提前预警海啸）；危害=与人体器官共振致伤（自"
     "然界动物异常行为可作地震前兆参考）。大象/鲸鱼用次声远距离交流，狗能听到部"
     "分超声（犬笛）。「超声波洗牙」「超声波加湿器」都是超声应用。",
     ["超声波和次声波的区别", "超声波的应用", "次声波的应用与危害",
      "B超用的是什么波", "大象怎么交流", "次声波为什么能预警海啸"],
     ["问多普勒效应", "问动物听觉范围对比"],
     "atomic", "",
     "超声>20kHz：方向好穿透强→声呐/B超/清洗/碎石；次声<20Hz：传远衰减慢→灾害监测·器官共振伤人；大象鲸次声交流·狗听超声；犬笛原理。"),
    ("kp_card_4react",
     "四种基本反应类型",
     "基础科学知识点内容（人话接口）", "化学",
     "化学反应四大基本类型：①**化合反应**——多变一（A+B→AB）：二氧化碳+水→碳"
     "酸、铁+氧气→四氧化三铁；②**分解反应**——一变多（AB→A+B）：电解水、高锰"
     "酸钾加热分解；③**置换反应**——单质+化合物→新单质+新化合物（A+BC→AC+B）："
     "铁+硫酸铜、锌+稀硫酸制氢气；④**复分解反应**——两化合物互换成分（AB+CD→"
     "AD+CB）：酸碱中和、盐酸+碳酸钙。判断口诀：化合「多变一」、分解「一变多」、"
     "置换「换单质」、复分解「换朋友」。注意：四大类型不覆盖所有反应（如 CO 还原"
     "氧化铁、甲烷燃烧不属于其中任何一类）。氧化还原则是从电子转移角度的另一套分"
     "类（交叉关系而非并列）。",
     ["四种基本反应类型是什么", "化合反应和分解反应的例子", "什么是置换反应",
      "什么是复分解反应", "甲烷燃烧属于什么反应类型", "氧化还原和四大类型的关系"],
     ["问反应类型判断练习", "问复分解发生条件"],
     "atomic", "",
     "四基本类型：化合(A+B→AB 多变一)/分解(AB→A+B)/置换(A+BC→AC+B 换单质)/复分解(AB+CD 换成分)；CO 还原与甲烷燃烧不属四类；氧化还原是电子转移角度的另一套分类。"),
    ("kp_card_earhear",
     "耳与听觉的形成",
     "基础科学知识点内容（人话接口）", "生物学",
     "耳的结构三部分：①**外耳**——耳廓（收集声波）+外耳道（传导）；②**中耳"
     "**——鼓膜（声波振动它）、听小骨（锤骨/砧骨/镫骨——放大并传递振动，镫骨是"
     "人体最小骨骼）、鼓室与咽鼓管（连通咽喉，平衡气压——坐飞机嚼口香糖防「耳"
     "闷」）；③**内耳**——耳蜗（内有听觉感受器，把振动转化为神经信号——听觉形"
     "成的关键）、前庭与半规管（感受头部位置变动——晕车晕船与此有关）。听觉形成"
     "路径：声波→鼓膜振动→听小骨→耳蜗（转神经信号）→听神经→**大脑皮层听觉中"
     "枢**（在脑中「听到」）——耳蜗只是转换器，「听到」发生在大脑。晕车=前庭过"
     "于敏感；鼻炎咽鼓管堵塞会耳闷听力下降。",
     ["听觉的形成过程", "耳的结构包括哪三部分", "耳蜗的作用是什么",
      "坐飞机耳朵闷怎么回事", "晕车与什么结构有关", "人体最小的骨"],
     ["问听力损伤分级", "问前庭功能"],
     "atomic", "",
     "耳=外耳(收集)+中耳(鼓膜+听小骨放大·咽鼓管调压)+内耳(耳蜗转换·前庭平衡)；听觉形成=声波→鼓膜→听小骨→耳蜗→听神经→大脑皮层；晕车=前庭敏感；镫骨最小骨。"),
    ("kp_card_langrelig",
     "世界的语言与宗教",
     "人文通识知识点内容（人话接口）", "地理学",
     "**语言**：联合国六种工作语言——汉语（使用人数最多，约 15 亿）、英语（使用"
     "范围最广的国际通用语）、西班牙语、俄语、法语、阿拉伯语。汉语主要分布中国与"
     "东南亚；英语源自英国，因殖民扩张与美国影响力成为世界通用语；西班牙语分布西"
     "班牙与拉美（除巴西——葡萄牙语）。**三大宗教**：①基督教——信徒最多（约 24"
     " 亿），经典《圣经》，分布在欧洲/美洲/大洋洲，教堂十字架；②伊斯兰教——约 19"
     " 亿，经典《古兰经》，分布西亚/北非/东南亚（印尼人口最多国），清真寺新月，信"
     "徒称穆斯林；③佛教——约 5 亿，起源于古印度，分布东亚东南亚，寺庙佛像。中国"
     "多元并存：道教本土宗教+佛/伊斯兰/基督/天主教。宗教自由受宪法保护。",
     ["世界上使用人数最多的语言", "联合国六种工作语言", "三大宗教",
      "伊斯兰教分布在哪里", "基督教的经典和标志", "佛教起源于哪里"],
     ["问语言谱系学", "问宗教地理分布"],
     "atomic", "",
     "六工作语=汉语(人数最多)/英语(范围最广)/西俄法阿；三大宗教=基督教(24 亿·圣经十字架)/伊斯兰(19 亿·古兰经新月·穆斯林·印尼最多)/佛教(古印度起源·东亚东南亚)。"),
]

QUESTIONS = [
    ("QB-545", "超声波和次声波的区别", "物理学", "技术直答",
     ["频率", "20000", "20"], "通识拓展103"),
    ("QB-546", "四种基本反应类型是什么", "化学", "技术直答",
     ["化合", "分解", "置换", "复分解"], "通识拓展103"),
    ("QB-547", "听觉的形成过程", "生物学", "技术直答",
     ["鼓膜", "耳蜗", "大脑"], "通识拓展103"),
    ("QB-548", "世界上使用人数最多的语言", "地理学", "技术直答",
     ["汉语"], "通识拓展103"),
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
                               "level:L2", "status:verified", "batch:通识拓展103"],
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
    bank["version"] = "v1.95"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
