# -*- coding: utf-8 -*-
"""seed_tier2_domain_cards.py · 候选域清单第二梯队知识卡（幂等）

批九：哲学/文学/语言学/艺术 四域各一张，KCCS 四要素完整+短触发变体（含题干原句）。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_philbranches",
     "哲学的三大分支",
     "人文通识知识点内容（人话接口）", "哲学",
     "哲学的三大经典分支：形而上学（研究存在与世界本质——世界的本原是什么）、"
     "认识论（研究知识的来源与界限——我们如何知道、能知道什么）、伦理学/价值论"
     "（研究应当如何行动与生活——什么是善、什么是正当）。逻辑学常作为贯穿三者的工具学科。",
     ["哲学的三大分支", "哲学分支有哪些", "什么是形而上学", "什么是认识论",
      "哲学研究什么", "哲学三大分支是什么", "伦理学属于哲学吗"],
     ["问某哲学家具体观点", "问中哲 specifics"],
     "atomic", "",
     "哲学三大分支 = 形而上学（存在）+ 认识论（知识）+ 伦理学（应当），逻辑学是贯穿工具。"),
    ("kp_card_fourtragedies",
     "莎士比亚四大悲剧",
     "人文通识知识点内容（人话接口）", "文学",
     "莎士比亚四大悲剧：《哈姆雷特》（丹麦王子为父复仇，To be or not to be）、"
     "《奥赛罗》（嫉妒毁掉真爱）、《李尔王》（老王分国土错辨忠奸）、《麦克白》"
     "（野心与预言引向弑君篡位）。四部均约作于 1600-1606 年莎士比亚悲剧创作巅峰期。",
     ["莎士比亚四大悲剧", "四大悲剧是哪四部", "哈姆雷特是谁写的",
      "莎士比亚的悲剧", "四大悲剧有哪些", "问莎士比亚悲剧"],
     ["问四大喜剧", "问莎士比亚十四行诗"],
     "atomic", "",
     "四大悲剧 = 哈姆雷特 + 奥赛罗 + 李尔王 + 麦克白（1600-1606 悲剧巅峰期）。"),
    ("kp_card_langfamily",
     "世界主要语系",
     "人文通识知识点内容（人话接口）", "语言学",
     "世界主要语系：印欧语系（英语/法语/俄语/印地语，使用人数最多）、汉藏语系"
     "（汉语/藏语/缅甸语）、闪含语系/亚非语系（阿拉伯语/希伯来语）、阿尔泰语系"
     "（争议分类，土耳其语/蒙古语等）、南岛语系（马来语/毛利语，分布最广）——"
     "同一语系意味着有共同祖先语言，词汇与语法有系统对应。",
     ["世界主要语系", "语系是什么", "汉语属于什么语系", "印欧语系",
      "语言怎么分类", "问语系", "什么是汉藏语系"],
     ["问某种语言语法细节", "问方言分区"],
     "atomic", "",
     "主要语系 = 印欧（最多人）+ 汉藏 + 亚非 + 南岛（分布最广）等，同语系=共同祖先语言。"),
    ("kp_card_threecolors",
     "三原色",
     "人文通识知识点内容（人话接口）", "艺术",
     "三原色分两套：色光三原色是红、绿、蓝（RGB，相加混合——全加得白光，屏幕"
     "显示器用）；颜料/印刷三原色是品红、黄、青（CMY，相减混合——全混近似黑色，"
     "绘画调色与印刷用）。两套不能混用：光混合越混越亮，颜料混合越混越暗。",
     ["三原色是什么", "问三原色", "色彩三原色", "RGB 三原色",
      "三原色有哪三种", "问原色"],
     ["问色彩心理学", "问透视法"],
     "atomic", "",
     "三原色两套 = 色光 RGB 相加（越混越亮）/ 颜料 CMY 相减（越混越暗），不可混用。"),
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
                "name": f"{name}（{dgroup}·人文通识知识卡）",
                "生效条件": conds,
                "子功能": f"{name}——人文通识高频问题知识条目",
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
                               "level:L2", "status:verified", "batch:候选域第二梯队"],
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
