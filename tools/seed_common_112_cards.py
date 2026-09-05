# -*- coding: utf-8 -*-
"""seed_common_112_cards.py · 通识拓展批次112知识卡+题库（幂等）

112：物理学-传感器应用/化学-化石燃料的综合利用/生物学-食品腐败的原因
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_sensor",
     "传感器：把非电信号变成电信号",
     "基础科学知识点内容（人话接口）", "物理学",
     "传感器是将非电学量（温度/光/压力/气体浓度等）转化为电学量的元件——是现代"
     "自动控制的「感觉器官」。常见传感器：①热敏电阻（温度↑电阻↓——电子体温"
     "计）；②光敏电阻（光照强电阻小——路灯自动开关）；③气体传感器（燃气报警"
     "器——检测甲烷泄漏）；④压力传感器（电子秤）；⑤湿度传感器。应用链：传感器"
     "（感知）→处理器（分析）→执行器（动作）——空调恒温、自动门、火灾报警都"
     "是这套组合。 smartphone 里的传感器：加速度（计步/翻转）、陀螺仪、距离、指"
     "纹、人脸识别。传感器技术+计算机+通信=物联网（IoT）的三大支柱。",
     ["传感器的作用是什么", "热敏电阻的原理", "光敏电阻的应用",
      "什么是物联网", "智能手机有哪些传感器", "燃气报警器的原理"],
     ["问传感器分类大全", "问智能家居系统"],
     "atomic", "",
     "传感器=非电量→电量：热敏(测温)/光敏(路灯)/气敏(燃气报警)/压力(电子秤)；链路=感知→处理→执行；手机有加速度陀螺仪等；+计算机+通信=物联网。"),
    ("kp_card_fossilcompre",
     "化石燃料的综合利用",
     "基础科学知识点内容（人话接口）", "化学",
     "化石燃料综合利用的思路（变「燃料」为「原料」）：①**煤**——干馏（隔绝空"
     "气强热）：焦炭（冶金）+煤焦油（化工原料）+焦炉煤气（燃料）；②**石油**——"
     "分馏（按沸点分离：石油气→汽油→煤油→柴油→润滑油→石蜡→沥青，物理变化）"
     "与裂化裂解（把长链断成短链——增产汽油和化工原料：乙烯丙烯，化学变化）；③"
     "**天然气**——直接燃料+合成氨/甲醇原料。意义：综合利用提高资源利用率、减"
     "少浪费与污染——「石油是工业的血液，煤是工业的粮食」。发展方向：煤的气化"
     "液化（煤制油/煤制气）、可燃冰开采、生物质能替代。",
     ["化石燃料的综合利用", "煤的干馏和石油的分馏区别", "石油分馏得到什么",
      "什么是裂化", "煤焦油有什么用", "石油是工业的血液"],
     ["问乙烯工业重要性", "问煤制油技术"],
     "atomic", "",
     "综合利用：煤→干馏(焦炭/煤焦油/煤气)；石油→分馏(物理·按沸点分离汽油煤油柴油)+裂化裂解(化学·增产汽油乙烯)；变燃料为原料提高利用率。"),
    ("kp_card_foodspoil",
     "食品腐败的原因与保存",
     "基础科学知识点内容（人话接口）", "生物学",
     "食品腐败的**根本原因**：微生物（细菌和真菌）在食品中**生长和繁殖**——分"
     "解食品中的有机物。保存食品的核心原理：**杀死微生物或抑制其生长繁殖**。常"
     "见方法与原理：①脱水法（晒干/风干——去除水分，细菌无法生长：干香菇）；②"
     "腌制法（高盐/高糖——渗透压脱水抑菌：咸菜/蜜饯）；③巴氏消毒法（牛奶——高"
     "温杀死致病菌但保留营养）；④高温灭菌密封（罐头）；⑤冷冻（-18℃ 抑菌不停"
     "止代谢）；⑥真空包装（隔绝氧气抑制需氧菌）；⑦添加防腐剂（山梨酸钾等）。"
     "「防腐剂都有害」是误区——合规使用是安全的。",
     ["食品腐败的根本原因是什么", "食品保存的方法有哪些", "真空包装的原理",
      "腌制为什么能防腐", "巴氏消毒和高温灭菌的区别", "防腐剂有害吗"],
     ["问 HACCP 复习", "问食品添加剂安全"],
     "atomic", "",
     "腐败根因=微生物生长繁殖；保存原理=杀菌或抑菌：脱水/腌制(渗透压)/巴氏消毒/罐头灭菌/冷冻抑菌/真空隔氧/合规防腐剂——「防腐剂都有害」是误区。"),
]

QUESTIONS = [
    ("QB-595", "传感器的作用是什么", "物理学", "技术直答",
     ["非电", "电"], "通识拓展112"),
    ("QB-596", "化石燃料的综合利用", "化学", "技术直答",
     ["干馏", "分馏"], "通识拓展112"),
    ("QB-597", "食品腐败的根本原因是什么", "生物学", "技术直答",
     ["微生物", "生长繁殖"], "通识拓展112"),
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
                               "level:L2", "status:verified", "batch:通识拓展112"],
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
    bank["version"] = "v2.8"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
