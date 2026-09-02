# -*- coding: utf-8 -*-
"""seed_tier3a_domain_cards.py · 候选域清单第三梯队前半知识卡（幂等）

批十：管理学/金融学/政治学/材料科学 四域各一张，KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_swot",
     "SWOT 分析",
     "社会科学知识点内容（人话接口）", "管理学",
     "SWOT 分析：从四个维度评估一个主体（企业/项目/个人）的战略处境——"
     "S 优势（Strengths，内部有利因素）、W 劣势（Weaknesses，内部不利因素）、"
     "O 机会（Opportunities，外部有利环境）、T 威胁（Threats，外部不利环境）；"
     "S/W 看内部、O/T 看外部，组合出四种策略取向（SO 进攻/WO 补强/ST 防御/WT 撤退）。",
     ["SWOT 分析", "什么是 SWOT", "问 SWOT", "swot 四个维度",
      "SWOT 分析是什么意思", "怎么用 SWOT"],
     ["问 PDCA 循环", "问波特五力"],
     "atomic", "",
     "SWOT = 优势+劣势（内部）×机会+威胁（外部），四种组合对应进攻/补强/防御/撤退策略。"),
    ("kp_card_compound",
     "复利",
     "社会科学知识点内容（人话接口）", "金融学",
     "复利（利滚利）：每期利息并入本金、下一期按新本金计息——与单利（只按初始本金"
     "计息）相对。终值公式 FV = PV×(1+r)^n：本金 100 元、年利率 10%、复利 2 年 = "
     "100×1.1² = 121 元（单利只有 120 元）。期限越长、利率越高，复利与单利差距越悬殊。",
     ["什么是复利", "复利怎么算", "问复利", "利滚利",
      "复利和单利的区别", "复利公式"],
     ["问股票估值", "问期权定价"],
     "atomic", "",
     "复利 = 利息并入本金滚动计息，FV = PV×(1+r)^n；长期看远超单利。"),
    ("kp_card_veto",
     "联合国安理会否决权",
     "社会科学知识点内容（人话接口）", "政治学",
     "联合国安理会否决权：安理会 15 个理事国中 5 个常任理事国（中/美/英/法/俄）"
     "对实质性决议（如制裁、维和、会员国申请）各有一票否决权——任一常任理事国"
     "投反对票，决议即不通过；程序性事项否决权不适用。这是 1945 年联合国成立时"
     "大国一致原则的制度化。",
     ["安理会否决权", "什么是五常否决权", "联合国否决权",
      "哪些国家有否决权", "问否决权", "联合国常任理事国"],
     ["问联合国大会表决", "问国际法院"],
     "atomic", "",
     "否决权 = 中美英法俄五常对安理会实质决议一票否决，大国一致原则的制度化。"),
    ("kp_card_semiconductor",
     "半导体",
     "社会科学知识点内容（人话接口）", "材料科学",
     "半导体：导电能力介于导体（铜/铝）与绝缘体（橡胶/玻璃）之间的材料，典型代表"
     "是硅（Si）和锗（Ge）。核心特性是可控性——掺入微量杂质（掺杂）可大幅改变导电"
     "性：掺五价元素得 N 型（电子导电）、掺三价元素得 P 型（空穴导电），P-N 结是"
     "二极管、晶体管乃至一切芯片的基础。",
     ["什么是半导体", "问半导体", "半导体材料", "硅为什么是半导体",
      "半导体和导体区别", "P型N型半导体"],
     ["问芯片制程", "问超导"],
     "atomic", "",
     "半导体 = 导电性介于导体绝缘体之间且可控（掺杂改变），硅为代表，P-N 结是芯片基础。"),
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
                "name": f"{name}（{dgroup}·社科工程知识卡）",
                "生效条件": conds,
                "子功能": f"{name}——社科工程高频问题知识条目",
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
                               "level:L2", "status:verified", "batch:候选域第三梯队A"],
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
