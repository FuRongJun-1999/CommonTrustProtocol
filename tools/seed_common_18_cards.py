# -*- coding: utf-8 -*-
"""seed_common_18_cards.py · 通识拓展批次18知识卡+题库（幂等）

18：化学-溶液浓度/地理学-世界河流/天文学-流星/生物学-蒸腾作用
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_concentration",
     "溶液浓度的表示方法",
     "基础科学知识点内容（人话接口）", "化学",
     "溶液浓度表示溶质在溶液中的含量，最常用的是溶质质量分数：质量分数 = 溶质"
     "质量 ÷ 溶液质量 × 100%（溶液质量 = 溶质 + 溶剂）。例如 10 克食盐溶于 "
     "90 克水，质量分数 = 10÷100×100% = 10%。医疗上还常用体积分数（如医用酒"
     "精 75% 指体积分数）和摩尔浓度（每升溶液含多少摩尔溶质，化学实验常用）。"
     "饱和溶液：一定温度下溶质不能再继续溶解的溶液——饱和与浓稀是两个概念，"
     "饱和溶液不一定浓。",
     ["溶液浓度怎么表示", "溶质质量分数怎么算", "10克盐溶于90克水浓度是多少",
      "医用酒精75%是什么浓度", "什么是饱和溶液", "饱和溶液一定是浓溶液吗"],
     ["问 ppm 表示法", "问胶体"],
     "atomic", "",
     "浓度=溶质质量分数(溶质÷溶液×100%)；酒精75%为体积分数；饱和≠浓稀。"),
    ("kp_card_worldrivers",
     "世界主要河流之最",
     "人文通识知识点内容（人话接口）", "地理学",
     "世界河流之最：尼罗河（非洲，约6650公里）是公认的世界最长河流；亚马孙河"
     "（南美洲）是世界流量最大、流域面积最广的河流，长度与尼罗河孰长存争议；"
     "长江（约6300公里）是亚洲第一长河、世界第三长，中国第一大河；黄河是中国"
     "第二长河，被称为「母亲河」，因含沙量世界最大而河水浑浊；多瑙河流经国家"
     "最多（约10个），有「国际河流」之称。",
     ["世界上最长的河流是哪条", "尼罗河有多长", "世界上流量最大的河流",
      "长江是世界第几长河", "黄河为什么是黄色的", "流经国家最多的河流"],
     ["问运河工程", "问水电站选址"],
     "atomic", "",
     "河流之最：最长=尼罗河(6650km)；流量最大=亚马孙；亚洲第一=长江(6300km)；含沙量最大=黄河；流经国最多=多瑙河。"),
    ("kp_card_meteor",
     "流星与流星雨的成因",
     "基础科学知识点内容（人话接口）", "天文学",
     "流星体是飘在太阳系空间里的尘埃和固体碎块（多来自彗星脱落物或小行星碎"
     "片）；当它们高速闯入地球大气层，与大气剧烈摩擦燃烧发光，划出亮线就是我"
     "们看到的「流星」——大部分在离地80~120公里的高空就烧完了，到不了地面；"
     "没烧完落到地面的是「陨石」。流星雨：地球每年定期穿过某颗彗星留下的尘埃"
     "带，流星看起来从同一点（辐射点）辐射而出——如英仙座流星雨（8月）、双子"
     "座流星雨（12月）。「流星雨」与星星本身无关，是天上的碎屑不是星辰坠落。",
     ["流星雨是怎么形成的", "流星是什么", "陨石和流星什么关系",
      "英仙座流星雨是什么时候", "流星会掉到地上吗", "为什么流星雨每年定时出现"],
     ["问人造卫星再入", "问黄道光"],
     "atomic", "",
     "流星=碎屑闯入大气摩擦燃烧发光(80-120km)；未烧尽落地=陨石；流星雨=地球定期穿越彗星尘埃带，辐射点命名。"),
    ("kp_card_transpiration",
     "植物的蒸腾作用",
     "基础科学知识点内容（人话接口）", "生物学",
     "蒸腾作用是水分从植物叶片（主要是气孔）以水蒸气形式散失到体外的过程。意"
     "义：①产生「蒸腾拉力」，是植物根吸收水分向上运输到茎叶的主要动力（像抽"
     "水机）；②促进溶解在水中的矿物质随水流向上输送；③降低叶片表面温度，防"
     "止骄阳下被灼伤。气孔由一对保卫细胞控制开闭——白天张开（光合作用进气+蒸"
     "腾失水），干旱时关闭以保水。「大树底下好乘凉」就有蒸腾降温的功劳。",
     ["植物的蒸腾作用有什么意义", "什么是蒸腾作用", "植物的水分怎么往上运",
      "气孔的作用是什么", "为什么大树底下好乘凉", "蒸腾拉力"],
     ["问光合作用详细过程", "问根压"],
     "atomic", "",
     "蒸腾作用=水分经气孔散失；意义=蒸腾拉力运水+运输矿物质+降温；气孔由保卫细胞控制，干旱时关闭。"),
]

QUESTIONS = [
    ("QB-205", "溶液浓度怎么表示", "化学", "技术直答",
     ["溶质质量分数"], "通识拓展18"),
    ("QB-206", "世界上最长的河流是哪条", "地理学", "技术直答",
     ["尼罗河"], "通识拓展18"),
    ("QB-207", "流星雨是怎么形成的", "天文学", "技术直答",
     ["彗星", "尘埃", "大气摩擦"], "通识拓展18"),
    ("QB-208", "植物的蒸腾作用有什么意义", "生物学", "技术直答",
     ["蒸腾拉力", "降温"], "通识拓展18"),
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
                               "level:L2", "status:verified", "batch:通识拓展18"],
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
    bank["version"] = "v1.10"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
