# -*- coding: utf-8 -*-
"""seed_common_138_cards.py · 通识拓展批次138知识卡+题库（幂等·两卡精批次）

138：地理学-欧盟欧元申根三概念/历史学-新航路开辟与地理大发现
KCCS 四要素+题干原句触发词。三重预检：欧盟（beidou 仅提伽利略）与大航海
（zhhe/earthshape 仅对比提及）均为主题未覆盖。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_euunion",
     "欧盟、欧元区与申根区",
     "人文通识知识点内容（人话接口）", "地理学",
     "三个易混概念：①**欧盟（EU）**=欧洲政治经济联盟，1993 年《马斯特里赫特"
     "条约》生效成立（前身 1957 年欧洲经济共同体），现有 **27 个成员国**"
     "（2020 年英国脱欧后）；②**欧元区**=统一使用**欧元**（€）的欧盟国家，"
     "约 20 国（1999 年欧元启用、2002 年纸币硬币流通）——注意欧盟成员不必用"
     "欧元（波兰用兹罗提、瑞典丹麦保留本币），非欧盟小国也可用欧元（摩纳哥/"
     "圣马力诺）；③**申根区**=取消内部边境检查的自由通行区（22 个欧盟国+挪"
     "威/瑞士等非欧盟国）——**瑞士是申根区但不是欧盟**，一句话区分：「欧盟是"
     "政治经济俱乐部，欧元区是统一用钱的圈子，申根区是免护照检查的圈子」。北"
     "约是军事联盟，与欧盟成员重叠但不是一回事。",
     ["欧盟是什么组织", "欧盟有多少成员国", "欧元是哪年启用的",
      "欧元区和欧盟的区别", "申根区是什么", "瑞士用欧元吗"],
     ["问欧洲旅游行程规划", "问脱欧政治影响分析"],
     "atomic", "",
     "欧盟=27 国政治经济联盟(1993 马约成立)；欧元区=约 20 国统一货币欧元(2002 纸币流通，欧盟国可不用如波兰)；申根区=免内部边境检查(含瑞士挪威等非欧盟国)；三者概念独立有交集；北约=军事联盟另算。"),
    ("kp_card_ageexploration",
     "新航路开辟与地理大发现",
     "人文通识知识点内容（人话接口）", "历史学",
     "15-17 世纪西欧**新航路开辟**（地理大发现）：**动因**=欧洲人对香料/黄金"
     "的渴求（传统东西方商路被奥斯曼帝国控制涨价）+地圆说流行+罗盘与帆船技术"
     "进步。四段关键航程：①**迪亚士**（葡萄牙，1488）——到达非洲最南端**好望"
     "角**；②**哥伦布**（西班牙资助，1492）——向西横渡大西洋「寻找印度」，误"
     "达美洲巴哈马群岛，至死以为到了印度（美洲原住民因此被误称「印第安人」）；"
     "③**达·伽马**（葡萄牙，1498）——绕好望角直达**印度**；④**麦哲伦船队"
     "（1519-1522）**——穿越大西洋-太平洋-印度洋完成**人类首次环球航行**（麦"
     "哲伦本人在菲律宾死于冲突，剩余船员完成全程）——实证地圆说。**影响**：世"
     "界开始连成一个整体；哥伦布大交换（美洲的玉米/土豆/番茄传入欧亚，马/小麦"
     "进入美洲）；同时开启殖民掠夺与奴隶贸易。对照：郑和下西洋（1405）比哥伦"
     "布早 87 年且规模宏大，但为和平朝贡贸易，未开辟殖民航路。",
     ["新航路开辟的原因", "哥伦布什么时候发现美洲", "麦哲伦环球航行",
      "谁第一个绕过好望角", "地理大发现的影响", "印第安人名称的由来"],
     ["问郑和下西洋详情（用郑和卡）", "问殖民史细节评价"],
     "atomic", "",
     "新航路开辟(15-17 世纪)：动因=香料黄金+奥斯曼断商路+地圆说+罗盘帆船；迪亚士 1488 好望角→哥伦布 1492 西航误达美洲(印第安人误称由来)→达·伽马 1498 到印度→麦哲伦船队 1519-1522 首次环球；影响=世界连成整体+物种交换(玉米土豆入华)+殖民掠夺始。"),
]

QUESTIONS = [
    ("QB-679", "欧盟现在有多少个成员国？欧元区和申根区与欧盟是什么关系？", "地理学", "技术直答",
     ["27", "二十七", "欧元", "申根", "边境"], "通识拓展138"),
    ("QB-680", "哥伦布是哪一年到达美洲的？他原本想航行到哪里？", "历史学", "技术直答",
     ["1492", "印度", "美洲"], "通识拓展138"),
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
                               "level:L2", "status:verified", "batch:通识拓展138"],
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
    bank["version"] = "v4.11"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
