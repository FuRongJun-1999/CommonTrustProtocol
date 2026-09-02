# -*- coding: utf-8 -*-
"""seed_night3_v2_cards.py · 夜间候选域清单v0.2第三组知识卡（幂等）

夜批N3：乐理/宪法常识/急救常识/消防安全 四域各一张，KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_musicnotes",
     "音符时值",
     "人文通识知识点内容（人话接口）", "乐理",
     "音符时值（以四分音符为一拍）：全音符 4 拍、二分音符 2 拍、四分音符 1 拍、"
     "八分音符半拍、十六分音符四分之一拍——每加一条符尾时值减半；附点音符在"
     "原时值上加一半（附点四分音符 = 1+0.5 = 1.5 拍）。休止符与同名音符时值相同。",
     ["音符时值", "全音符几拍", "四分音符几拍", "什么是附点音符",
      "八分音符是多少拍", "问乐理音符"],
     ["问调式调性", "问和弦构成"],
     "atomic", "",
     "音符时值 = 全4/二分2/四分1/八分半拍（加符尾减半）；附点加原值一半。"),
    ("kp_card_constitution",
     "宪法的地位",
     "人文通识知识点内容（人话接口）", "宪法常识",
     "宪法是国家的根本大法：规定国家根本制度与公民基本权利义务，具有最高法律"
     "效力——一切法律、行政法规都不得与宪法相抵触（违宪无效）。我国现行宪法"
     "为 1982 年宪法（历经五次修正）；全国人民代表大会为最高国家权力机关，"
     "行使修改宪法、监督宪法实施的职权；宪法的修改由全国人大常委会或五分之一"
     "以上全国人大代表提议，需全体代表三分之二以上多数通过。",
     ["宪法的地位是什么", "为什么宪法是根本大法", "宪法最高法律效力",
      "现行宪法是哪年", "宪法怎么修改", "问宪法"],
     ["问民法典", "问具体案例判决"],
     "atomic", "",
     "宪法 = 根本大法最高效力（抵触即无效）；82 年现行宪法；修改需人大全体 2/3 多数。"),
    ("kp_card_cpr",
     "心肺复苏步骤",
     "生活常识知识点内容（人话接口）", "急救常识",
     "心肺复苏（CPR）步骤：①判断意识与呼吸（轻拍双肩大声呼唤，观察胸廓起伏"
     "5-10 秒）；②呼救并拨打 120、取 AED；③胸外按压：两乳头连线中点，双手"
     "交叠掌根用力，深度 5-6 厘米、频率每分钟 100-120 次，按压与放松时间相等；"
     "④开放气道（仰头抬颏）后人工呼吸，按压与吹气比 30:2；持续到专业人员到达"
     "或 AED 就绪。未经训练时可只做持续胸外按压。",
     ["心肺复苏步骤", "CPR怎么做", "胸外按压深度频率", "有人晕倒怎么急救",
      "按压吹气比是多少", "问急救"],
     ["问止血包扎", "问骨折固定"],
     "atomic", "",
     "CPR = 判断→呼救取 AED→按压（5-6cm 深，100-120 次/分）→开放气道人工呼吸（30:2）。"),
    ("kp_card_fireext",
     "灭火器选用与电器火灾处置",
     "生活常识知识点内容（人话接口）", "消防安全",
     "灭火器选用：干粉灭火器适用最广（固体/液体/气体火灾与带电设备）；二氧化碳"
     "灭火器适合精密仪器与电器（不留残迹）；水基型禁用于带电与油类火灾。电器"
     "火灾处置原则：先断电再灭火——绝不直接泼水（水导电且会使油溅射）；油锅"
     "起火用锅盖盖灭或倒入大量青菜，切勿加水。灭火要对准火焰根部而非火苗上方。",
     ["灭火器怎么选用", "电器着火怎么办", "油锅起火怎么灭", "干粉灭火器",
      "电器火灾能用水扑灭吗", "问灭火"],
     ["问火场逃生绳结", "问消防栓使用"],
     "atomic", "",
     "灭火器选型：干粉最通用/二氧化碳适合精密电器；电器火先断电禁泼水；对准火焰根部。"),
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
                "name": f"{name}（{dgroup}·生活通识知识卡）",
                "生效条件": conds,
                "子功能": f"{name}——生活通识高频问题知识条目",
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
                               "level:L2", "status:verified", "batch:夜间v0.2第三组"],
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
    return {"inserted": inserted, "updated": updated, "skipped": skipped}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
