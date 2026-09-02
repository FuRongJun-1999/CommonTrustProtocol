# -*- coding: utf-8 -*-
"""seed_night2_v2_cards.py · 夜间候选域清单v0.2第二组知识卡（幂等）

夜批N2：遗传学/生态学/中国历史/世界历史 四域各一张，KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_gene_dna",
     "DNA 与基因的关系",
     "基础科学知识点内容（人话接口）", "遗传学",
     "DNA 与基因的关系：DNA 是携带遗传信息的双螺旋分子（两条链靠碱基配对"
     "A-T、C-G 结合）；基因是 DNA 上具有遗传效应的片段——一段基因编码一个"
     "蛋白质（或发挥调控作用）。染色体由 DNA 缠绕蛋白质构成，人类有 23 对"
     "46 条染色体，其上约有 2 万多个基因。简言之：染色体 ⊃ DNA ⊃ 基因。",
     ["DNA和基因的关系", "什么是基因", "什么是DNA", "基因在哪",
      "染色体上有多少基因", "DNA是什么"],
     ["问基因编辑技术", "问蛋白质合成细节"],
     "atomic", "",
     "染色体 ⊃ DNA（双螺旋）⊃ 基因（有遗传效应的片段）；人类 23 对染色体约 2 万基因。"),
    ("kp_card_foodchain",
     "食物链与食物网",
     "基础科学知识点内容（人话接口）", "生态学",
     "食物链：生物之间「吃与被吃」的顺序关系，如草→兔→鹰。层级为营养级："
     "第一营养级是生产者（绿色植物，光合作用制造有机物），第二级是初级消费者"
     "（植食动物），往上是次级、三级消费者；分解者（细菌真菌）分解动植物残体"
     "回到自然界。能量沿食物链逐级递减（每级约只传递 10%-20%），所以食物链"
     "一般不超过 4-5 个营养级。多条食物链交织成食物网。",
     ["什么是食物链", "食物链", "食物链和食物网", "生产者消费者",
      "为什么食物链不超过五级", "问营养级"],
     ["问碳循环细节", "问种群增长模型"],
     "atomic", "",
     "食物链 = 生产者→各级消费者，能量每级递减至 10-20%（故 ≤4-5 级）；分解者归还物质。"),
    ("kp_card_qinunify",
     "秦统一中国",
     "人文通识知识点内容（人话接口）", "中国历史",
     "秦统一中国：公元前 221 年秦王嬴政灭六国（韩赵魏楚燕齐）建立秦朝，"
     "自称「始皇帝」——中国历史上第一个中央集权的统一王朝。主要制度贡献："
     "统一文字（小篆）、统一货币（圆形方孔钱）、统一度量衡、统一车轨（车同轨"
     "书同文）；地方推行郡县制取代分封制。秦朝虽二世而亡（前 207 年），但"
     "「百代都行秦政法」，其制度框架影响此后两千余年。",
     ["秦统一中国", "秦朝什么时候统一", "秦始皇的统一贡献", "秦统一六国",
      "第一个统一王朝", "郡县制是谁推行的"],
     ["问汉朝历史", "问秦陵兵马俑细节"],
     "atomic", "",
     "秦统一 = 前 221 年嬴政灭六国建首个中央集权王朝；书同文车同轨统一货币度量衡，郡县制。"),
    ("kp_card_renaissance",
     "文艺复兴",
     "人文通识知识点内容（人话接口）", "世界历史",
     "文艺复兴（14-16 世纪）：发源于意大利（佛罗伦萨），以复兴古希腊罗马文化"
     "为旗号的思想文化运动，核心精神是人文主义——以人为中心而非以神为中心。"
     "文学三杰：但丁（《神曲》）、彼特拉克、薄伽丘；美术三杰：达·芬奇（《蒙娜"
     "丽莎》）、米开朗基罗（《大卫》）、拉斐尔（圣母像）。为随后的宗教改革与"
     "科学革命铺路。",
     ["什么是文艺复兴", "文艺复兴", "文艺复兴三杰", "人文主义",
      "文艺复兴发源地", "蒙娜丽莎是谁画的"],
     ["问启蒙运动", "问宗教改革细节"],
     "atomic", "",
     "文艺复兴 = 14-16 世纪意大利起源，人文主义为核心；文学三杰+美术三杰（达芬奇/米开朗基罗/拉斐尔）。"),
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
                               "level:L2", "status:verified", "batch:夜间v0.2第二组"],
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
