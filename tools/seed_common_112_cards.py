# -*- coding: utf-8 -*-
"""seed_common_112_cards.py · 通识拓展批次112知识卡+题库（幂等）

112：物理学-大气压强的应用/化学-实验室制取气体的思路/生物学-心肺复苏急救
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_atmuse",
     "大气压强的应用：吸管吸盘抽水机",
     "基础科学知识点内容（人话接口）", "物理学",
     "大气压强的三大经典应用：①**吸管**——吸气使管内气压降低，管外大气压把饮"
     "料「压」进嘴里（不是「吸」上来的，是「压」上来的）；②**吸盘**——挤出内部"
     "空气，外部大气压把吸盘紧压在墙上；③**活塞式抽水机**——活塞上提使泵内气压"
     "降低，大气压把井水压入泵体（理论最大吸水高度约 10.3 米——一个大气压只能支"
     "持 10.3 米水柱）。拓展：高压锅（增大气压提高沸点）、真空压缩袋、拔火罐。也"
     "是托里拆利实验（atmpress 呼应）测出大气压值的原理应用。",
     ["吸管吸饮料的原理", "吸盘挂钩为什么能吸在墙上", "活塞式抽水机的原理",
      "抽水机最多能把水抽多高", "大气压强的应用有哪些", "为什么高压锅煮饭快"],
     ["问托里拆利实验复习", "问大气压随高度变化"],
     "atomic", "",
     "大气压应用=吸管(降压压入)+吸盘(挤出空气压紧)+活塞抽水机(最大 10.3m 水柱)+高压锅(增压升沸点)+真空压缩袋+拔火罐——本质都是大气压差。"),
    ("kp_card_gasprep",
     "实验室制取气体的思路",
     "基础科学知识点内容（人话接口）", "化学",
     "实验室制取气体的通用思路（以制氧气/二氧化碳/氢气为例）：①**反应原理**——"
     "选择合适的药品与反应（制 O₂：分解过氧化氢；制 CO₂：大理石+稀盐酸；制 H₂："
     "锌+稀硫酸）；②**发生装置**——由反应物状态和反应条件决定：固+固加热型"
     "（高锰酸钾制氧）/固+液不加热型（过氧化氢制氧/大理石制 CO₂）；③**收集装"
     "置**——排水法（气体不易溶于水，较纯）、向上排空气法（密度比空气大：O₂/"
     "CO₂）、向下排空气法（密度比空气小：H₂）；④**验满/检验**——O₂：带火星木"
     "条复燃；CO₂：澄清石灰水变浑浊。思路迁移：制氢气用锌+稀硫酸（固液不加热），"
     "排水法收集。",
     ["实验室制取气体的思路", "发生装置怎么选择", "收集装置怎么选择",
      "制氧气和制二氧化碳装置的区别", "排水法收集的气体有什么优点",
      "怎么检验二氧化碳已收集满"],
     ["问气体制取对比表", "问实验装置图识别"],
     "atomic", "",
     "制气体思路=原理→发生装置(固固加热/固液不加热)→收集装置(排水较纯/向上排空气密度大/向下排空气密度小)→验满检验(O₂ 木条复燃·CO₂ 石灰水浑浊)。"),
    ("kp_card_cprfirst",
     "心肺复苏（CPR）急救步骤",
     "生活常识知识点内容（人话接口）", "生活常识",
     "发现有人倒地无意识无呼吸，立即心肺复苏（黄金 4 分钟）：①**判断**——轻拍"
     "双肩大声呼唤、观察胸廓起伏（5-10 秒）；②**呼救**——拨打 120、取 AED（自动"
     "体外除颤器）；③**胸外按压**——两乳头连线中点，双手交叠掌根用力，深度 5-6"
     " 厘米，频率 100-120 次/分（跟着《最炫民族风》节奏刚好）；④**人工呼吸**——"
     "仰头抬颏开放气道，捏鼻吹气 1 秒见胸廓隆起；⑤按压与吹气比 **30:2** 循环，直"
     "到专业急救人员到达。AED 使用：开机听语音提示、贴电极片、放电时任何人不得"
     "接触患者。儿童按压深度约 5 厘米、单掌或两指。普及 CPR+AED 是提高心脏骤停"
     "存活率的关键（我国每分钟配置率仍低）。",
     ["心肺复苏的步骤", "胸外按压的位置深度频率", "AED是什么怎么用",
      "按压与人工呼吸的比例", "黄金四分钟是什么意思", "心肺复苏到什么时候停止"],
     ["问海姆立克急救法", "问AED分布与普法"],
     "atomic", "",
     "CPR=判断→呼救(120+取AED)→胸外按压(两乳连线中点·5-6cm·100-120次/分)→开放气道人工呼吸，30:2 循环；黄金 4 分钟；AED 语音操作放电勿触。"),
]

QUESTIONS = [
    ("QB-584", "吸管吸饮料的原理", "物理学", "技术直答",
     ["大气压"], "通识拓展112"),
    ("QB-585", "实验室制取气体的思路", "化学", "技术直答",
     ["发生装置", "收集装置"], "通识拓展112"),
    ("QB-586", "心肺复苏的步骤", "生物学", "技术直答",
     ["胸外按压", "人工呼吸"], "通识拓展112"),
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
    bank["version"] = "v2.4"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
