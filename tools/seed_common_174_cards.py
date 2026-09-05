# -*- coding: utf-8 -*-
"""seed_common_174_cards.py · 通识拓展批次174知识卡+题库（幂等）

174：地理学-五岳/生物学-手指泡水起皱/化学-美拉德反应
KCCS 四要素+题干原句触发词。三重预检：五岳双库零覆盖（泰山仅在世界遗产卡
提及）；泡水起皱/美拉德零覆盖（褐变卡=酶促反应，美拉德=非酶，划界）。
执行前外文长词检测（Maillard 加白名单）。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_fivepeaks",
     "五岳",
     "人文通识知识点内容（人话接口）", "地理学",
     "五岳=中国五大名山的总称，按方位：①**东岳泰山**（山东，1545m）——「五"
     "岳之首」，历代帝王封禅圣地（孔子「登泰山而小天下」、杜甫「会当凌绝"
     "顶」）；②**西岳华山**（陕西，2154m）——「奇险天下第一山」（长空栈"
     "道）；③**南岳衡山**（湖南，1300m）——「五岳独秀」；④**北岳恒山**（山"
     "西，2016m）——悬空寺所在；⑤**中岳嵩山**（河南，1491m）——少林寺与中"
     "岳庙。记忆口诀：「东泰西华，南衡北恒，中间嵩山」。文化：五岳封禅源于古"
     "代山川崇拜与五行方位观；徐霞客「**五岳归来不看山，黄山归来不看岳**」"
     "（此句实为后人假托徐霞客的旅游谚语）把黄山抬到五岳之上。五岳与佛教四大"
     "名山（五台/峨眉/普陀/九华——菩萨道场）是两套体系，勿混。",
     ["五岳是哪五座山", "五岳之首", "泰山华山衡山恒山嵩山",
      "五岳归来不看山", "四大佛教名山", "封禅是什么"],
     ["问黄山风景（风景名山类）", "问四大佛教名山"],
     "atomic", "",
     "五岳=东岳泰山(首·封禅)1545m/西岳华山(奇险)/南岳衡山(秀)/北岳恒山(悬空寺)/中岳嵩山(少林寺)——东泰西华南衡北恒中嵩；佛教四大名山(五台峨眉普陀九华)是另一体系；黄山不在五岳。"),
    ("kp_card_wrinkle",
     "手指泡水为什么会起皱",
     "基础科学知识点内容（人话接口）", "生物学",
     "手指/脚趾泡水久了皮肤起皱：①**老解释（渗透吸水胀皱）已被推翻**——起皱"
     "其实是一种**主动的神经控制反应**：手泡水时神经系统（交感神经）指挥指尖"
     "**血管收缩**，皮下组织体积变化把皮肤「拉」出褶皱（2021 年前后研究确"
     "认）；②**证据**：神经损伤的手指泡水**不起皱**（医生用它检查神经功能）；"
     "起皱只发生在无毛的手指脚趾，身体其他皮肤泡再久也不皱；③**进化意义假"
     "说**——褶皱像**轮胎纹**，把水排开增大湿滑环境的**抓握力**（实验证"
     "实：起皱的手指抓湿物确实更快）；④不影响健康的生理现象，泡久了皮肤发白"
     "变软属正常，擦干后几分钟恢复。",
     ["手指泡水为什么会起皱", "泡水起皱是渗透吗", "皮肤起皱的真正原因",
      "手指泡水起皱好处", "神经功能检查起皱"],
     ["问皮肤结构", "问手足多汗"],
     "atomic", "",
     "泡水起皱=交感神经指挥血管收缩的主动反应（非渗透吸水——神经损伤者不起皱可作神经检查）；假说=褶皱如轮胎纹增湿握力（实验证实抓湿物更快）；无毛的手足才有；生理现象数分钟恢复。"),
    ("kp_card_maillard",
     "美拉德反应：食物为什么越煎越香",
     "基础科学知识点内容（人话接口）", "化学",
     "**美拉德反应（Maillard reaction）**=食物中的**氨基酸**与**还原糖**在加"
     "热（约 140-165°C 起显著）下发生的一系列复杂反应——生成数百种**香气与"
     "风味物质**＋棕褐色素（类黑素）。这就是：烤面包的金黄外壳与麦香、煎牛排"
     "的焦香、咖啡豆烘焙的醇香、红烧肉的酱红、炸薯条的酥香——「**非酶褐"
     "变**」（不需要酶，纯靠热；区别于苹果切开的酶促褐变）。**要点**：①水"
     "分会压低温度（水的沸点 100°C），所以**先把食材表面煎干**才会上色起香——"
     "「煎牛排别频繁翻动」；②温度过高（>200°C）易生成**丙烯酰胺**（潜在致癌"
     "物，薯条炸到焦黑含量飙升）——金黄焦边即可，焦黑部分建议去掉；③烘焙/烤"
     "茶/酿造（酱油老抽的色香）都靠它。口诀：「**没有美拉德，就没有人间烟火"
     "气**」。",
     ["美拉德反应是什么", "牛排为什么煎了香", "面包为什么金黄",
      "美拉德反应和焦糖化", "丙烯酰胺", "非酶褐变"],
     ["问酶促褐变（用苹果褐变卡）", "问焦糖化反应"],
     "atomic", "",
     "美拉德反应=氨基酸+还原糖在 140-165°C 的非酶褐变：生成数百种香气物质+类黑素（面包壳/牛排焦香/咖啡红烧肉）；先煎干表面才上色；>200°C 产丙烯酰胺（焦黑去掉）；与苹果切开的酶促褐变是两条路径。"),
]

QUESTIONS = [
    ("QB-773", "五岳分别是哪五座山？哪一座被称为「五岳之首」？", "地理学", "技术直答",
     ["泰山", "华山", "衡山", "恒山", "嵩山", "东岳"], "通识拓展174"),
    ("QB-774", "手指泡水久了为什么会起皱？起皱反应说明神经系统什么状态？", "生物学", "技术直答",
     ["血管收缩", "主动", "神经", "抓握", "轮胎纹"], "通识拓展174"),
    ("QB-775", "煎牛排、烤面包的香气来自什么化学反应？这个反应需要达到什么温度范围？", "化学", "技术直答",
     ["美拉德", "氨基酸", "还原糖", "140", "165", "褐变"], "通识拓展174"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    whitelist = {"Havilland", "Maillard", "reaction"}  # 正当专名
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{6,}", content):
            if word not in whitelist:
                problems.append((node[0], f"长英文词: {word}"))
    if problems:
        raise SystemExit(f"外文长词检测报警: {problems}")


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
                               "level:L2", "status:verified", "batch:通识拓展174"],
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
    bank["version"] = "v4.47"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
