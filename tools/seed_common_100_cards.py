# -*- coding: utf-8 -*-
"""seed_common_100_cards.py · 通识拓展批次100知识卡+题库（幂等·整数批）

100：物理学-发电机与电动机/化学-粗盐提纯/生物学-病原体/地理学-青藏地区
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_genmotor",
     "发电机与电动机：一对「逆运算」",
     "基础科学知识点内容（人话接口）", "物理学",
     "发电机与电动机原理互逆：①**发电机**——电磁感应（法拉第）：闭合电路导体在"
     "磁场中切割磁感线产生感应电流——机械能→电能（火电厂的汽轮机带、水电站的水"
     "轮机带、风车带都是带动发电机转子）；②**电动机**——通电导体在磁场中受力转"
     "动——电能→机械能（电风扇/电动车/洗衣机）。判断技巧：无电源连灯泡=发电机模"
     "型；有电源=电动机模型。交流与直流：发电机天然产生交流电（线圈转动方向周期"
     "变化），家庭用电 220V/50Hz 即交流（每秒方向变 100 次）；换向器可使输出变直"
     "流（直流电动机用换向器持续转动）。能量来源链：风电（风能→电）、水电（势能"
     "→电）、火电（化学→内→机械→电）。",
     ["发电机和电动机的区别", "发电机的原理", "电动机的能量转化",
      "交流电和直流电", "换向器的作用", "风车发电的能量转化"],
     ["问电磁感应定律定量", "问电动机换向器细节"],
     "atomic", "",
     "发电机=电磁感应(机械→电·法拉第)；电动机=磁场对电流受力(电→机械)；互为逆运算；交流=方向周期变化(家庭 50Hz)；风电水电火电末级都是「带发电机」。"),
    ("kp_card_saltpurify",
     "粗盐提纯：溶解过滤蒸发",
     "基础科学知识点内容（人话接口）", "化学",
     "粗盐提纯（去除不溶性泥沙）三步骤：①**溶解**——粗盐放入烧杯加水，玻璃棒搅"
     "拌加速溶解；②**过滤**——「一贴二低三靠」：滤纸紧贴漏斗内壁；滤纸边缘低于"
     "漏斗口、液面低于滤纸边缘；烧杯口靠玻璃棒、玻璃棒下端靠三层滤纸一侧、漏斗"
     "下端靠烧杯内壁（玻璃棒=引流）；③**蒸发**——蒸发皿中加热，玻璃棒不断搅拌"
     "（防局部过热液滴飞溅），出现**较多固体时停止加热**用余热蒸干。玻璃棒三处作"
     "用：溶解（搅拌加速）、过滤（引流）、蒸发（搅拌防飞溅）。所得食盐仍含可溶"
     "性杂质（CaCl₂/MgCl₂ 等）——要得到纯净食盐还需化学法（加试剂沉淀过滤）。过"
     "滤后滤液仍浑浊的原因：滤纸破损/液面高于滤纸/仪器不干净。",
     ["粗盐提纯的步骤", "过滤的操作要点一贴二低三靠", "玻璃棒的作用",
      "蒸发时为什么要用玻璃棒搅拌", "什么时候停止加热", "滤液浑浊的原因"],
     ["问蒸馏与过滤对比", "问可溶性杂质去除"],
     "atomic", "",
     "粗盐提纯=溶解(搅)→过滤(一贴二低三靠·棒引流)→蒸发(棒搅拌防溅·较多固体即停)；玻璃棒三作用=搅拌/引流/搅拌；滤液浑浊=纸破/液高/器脏。"),
    ("kp_card_pathogen",
     "病原体：传染病的「元凶」",
     "基础科学知识点内容（人话接口）", "生物学",
     "病原体=引起传染病的**细菌、病毒、真菌和寄生虫**等病原微生物。常见对应：细"
     "菌——肺结核（结核杆菌）、破伤风、霍乱；病毒——流感、新冠、艾滋病（HIV）、"
     "乙肝、狂犬病；真菌——足癣（脚气）、甲癣（灰指甲）；寄生虫——蛔虫病、疟疾"
     "（疟原虫，按蚊传播）、血吸虫病。传播途径与病原体匹配：呼吸道传染病（飞沫/"
     "空气——流感结核）、消化道传染病（饮水食物——霍乱甲肝蛔虫）、血液传染病"
     "（蚊虫叮咬输血——疟疾乙肝艾滋病）、体表传染病（接触——破伤风沙眼癣）。预"
     "防三环节（epidemic 呼应）：控制传染源、切断传播途径、保护易感人群——接种"
     "疫苗是最经济有效的保护易感人群手段。",
     ["病原体包括哪些", "流感由什么引起", "疟疾由什么传播",
      "病原体和传染源的区别", "真菌引起的疾病", "传染病按传播途径分几类"],
     ["问免疫三防线衔接", "问抗生素与病原体对应"],
     "atomic", "",
     "病原体=细菌(结核)/病毒(流感 HIV)/真菌(足癣)/寄生虫(疟原虫蛔虫)；四传播途径=呼吸道/消化道/血液/体表；预防=控源+切途+护易感(疫苗最经济)。"),
    ("kp_card_qinghaiarea",
     "青藏地区：高寒的世界屋脊",
     "人文通识知识点内容（人话接口）", "地理学",
     "青藏地区（西藏/青海+四川西部等）最突出的自然特征是**高寒**：平均海拔 4000"
     " 米以上（世界屋脊），气温低、空气稀薄、日照强（拉萨「日光城」）。农业特色"
     "**河谷农业**——热量不足使种植集中在海拔较低的河谷地带：雅鲁藏布江谷地（青"
     "稞/小麦）、湟水谷地；青稞是主粮（糌粑/青稞酒）。牲畜：牦牛（「高原之舟」）、"
     "藏绵羊、藏山羊（毛厚耐寒）。资源：太阳能最丰富（日照强空气稀薄吸热多）、地"
     "热（羊八井）、水能（大江大河源头）、矿产资源（柴达木盆地「聚宝盆」——盐/石"
     "油/铅锌）。交通：青藏铁路（qingzangrail 呼应）+川藏/青藏/新藏/滇藏公路。保"
     "护：三江源自然保护区（长江黄河澜沧江源头，「中华水塔」）——保护生态优先。",
     ["青藏地区的自然特征", "河谷农业是什么", "高原之舟指什么动物",
      "日光城是哪里", "三江源为什么重要", "柴达木盆地有什么资源"],
     ["问高寒牧区特点", "问青藏铁路工程复习"],
     "atomic", "",
     "青藏地区=高寒(4000m+·日光城拉萨)：河谷农业(雅鲁藏布/湟水·青稞)+牦牛高原之舟；资源=太阳能最富/羊八井地热/柴达木聚宝盆；三江源=中华水塔重点保护。"),
]

QUESTIONS = [
    ("QB-533", "发电机和电动机的区别", "物理学", "技术直答",
     ["电磁感应", "机械能", "电能"], "通识拓展100"),
    ("QB-534", "粗盐提纯的步骤", "化学", "技术直答",
     ["溶解", "过滤", "蒸发"], "通识拓展100"),
    ("QB-535", "病原体包括哪些", "生物学", "技术直答",
     ["细菌", "病毒", "真菌", "寄生虫"], "通识拓展100"),
    ("QB-536", "青藏地区的自然特征", "地理学", "技术直答",
     ["高寒"], "通识拓展100"),
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
                               "level:L2", "status:verified", "batch:通识拓展100"],
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
    bank["version"] = "v1.92"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
