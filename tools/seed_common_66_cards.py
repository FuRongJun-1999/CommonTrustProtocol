# -*- coding: utf-8 -*-
"""seed_common_66_cards.py · 通识拓展批次66知识卡+题库（幂等）

66：物理学-磁化与磁性材料/化学-「酸性体质」辟谣/生物学-细胞分裂/历史-文景之治
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_magnetize",
     "磁化与磁性材料",
     "基础科学知识点内容（人话接口）", "物理学",
     "磁体只能吸引铁、钴、镍等磁性材料（不能吸引铜/铝/塑料）——原理：磁体使铁"
     "磁性物质内部的「磁畴」排列一致而被**磁化**。磁化应用与消退：钢被磁化后能"
     "长期保持磁性（硬磁——永磁体/磁带）；软铁磁化后磁性易消失（软磁——电磁铁"
     "铁芯，通电有磁断电磁性消失，用于电磁起重机/继电器/电动机）。去磁方法：敲"
     "击/加热（高温扰乱磁畴排列）。指南针本身就是被地磁场磁化（或天然磁石）的小"
     "磁体。防磁常识：银行卡/手机/机械手表远离强磁体（消磁或磁化机件）；彩电老"
     "式显像管被磁化出现色斑（消磁器处理）。",
     ["磁铁能吸引什么材料", "什么是磁化", "电磁铁的铁芯为什么用软铁",
      "钢和软铁做磁体有什么区别", "怎么给物体去磁", "银行卡为什么怕磁"],
     ["问电磁起重机结构", "问磁畴理论科普"],
     "atomic", "",
     "磁体只吸铁钴镍：磁化=磁畴排列一致；硬磁(钢·长久保磁/永磁体)vs 软磁(软铁·易消磁/电磁铁芯)；去磁=敲击加热；银行卡机械表远离强磁。"),
    ("kp_card_acidbody",
     "「酸性体质」是伪科学",
     "生活常识知识点内容（人话接口）", "生活常识",
     "「人的体质分酸碱性、酸性体质易生病、喝碱性水/吃碱性食物能调理体质」——这"
     "是流传最广的营养学伪科学之一（美国「酸碱体质理论」创始人已被法院判罚数亿"
     "美元）。科学事实：①人体血液 pH 稳定在 7.35-7.45（弱碱性），靠呼吸、肾脏"
     "和血液缓冲系统精密调节，饮食根本改变不了血液 pH；②食物分「酸性/碱性食物」"
     "只是按代谢产物分类（肉蛋米面为酸性食物、蔬果为碱性食物），与吃下去的味道"
     "无关（柠檬很酸却是碱性食物），也不影响体质；③「酸中毒/碱中毒」是严重疾病"
     "状态（如糖尿病酮症酸中毒），不是吃出来的体质。真正该做的：均衡饮食、蔬果"
     "适量（它们健康是因为维生素纤维，不是「碱性」）。凡是拿「调理酸性体质」卖"
     "保健品的，直接拉黑。",
     ["酸性体质是真的吗", "喝碱性水有用吗", "酸性食物碱性食物怎么分",
      "血液的pH是多少", "酸中毒是什么", "碱性食品能改变体质吗"],
     ["问缓冲系统生理学", "问常见伪科学清单"],
     "atomic", "",
     "「酸性体质」=伪科学：血液 pH 7.35-7.45 由呼吸/肾/缓冲系统恒定，饮食改变不了；食物酸碱=代谢产物分类(柠檬酸却为碱)；酸中毒是疾病非体质；均衡饮食才是真。"),
    ("kp_card_celldiv",
     "细胞分裂与生长",
     "基础科学知识点内容（人话接口）", "生物学",
     "生物体由小长大：细胞**分裂**（数量增多）+细胞**生长**（体积增大）+细胞分"
     "化（形成不同组织）。细胞分裂过程：细胞核先一分为二（遗传物质染色体**先复"
     "制再均分**——保证新细胞遗传物质与原细胞相同，这是生命延续的关键），随后"
     "细胞质分成两份，最后形成新的细胞膜/细胞壁。癌变：细胞分裂失控、无限增殖"
     "（正常细胞分裂次数有限——海弗里克极限约 50 次）。染色体：人体细胞 23 对 46"
     " 条（生殖细胞减半 23 条），DNA 载于染色体上。细胞是生命活动的基本结构与功"
     "能单位（细胞学说：施莱登/施旺提出，「所有动植物都由细胞发育而来」）。",
     ["细胞怎么数量增多", "细胞分裂时遗传物质怎么变化", "什么是细胞癌变",
      "人体有多少条染色体", "细胞学说是谁提出的", "细胞分裂和分化的区别"],
     ["问有丝分裂分期", "问干细胞与分化"],
     "atomic", "",
     "长大=分裂(数量·染色体先复制再均分保遗传稳定)+生长(体积)+分化(成组织)；癌变=分裂失控无限增殖；人 23 对 46 条染色体；细胞学说=施莱登施旺。"),
    ("kp_card_wenjing",
     "文景之治",
     "人文通识知识点内容（人话接口）", "历史",
     "文景之治：西汉汉文帝、汉景帝在位时期（前 180-前 141 年）的治世——中国大"
     "一统王朝的第一个盛世。政策核心「休养生息」：①轻徭薄赋——田租从十五税一"
     "降到三十税一甚至全免；②减轻刑罚——文帝废除肉刑（缇萦救父感动文帝改法"
     "的典故）；③提倡节俭——文帝在位 23 年宫室苑囿无所增、宠妃衣不曳地；④与"
     "民休息不扰民。成果：国库充盈到串钱的绳子都烂了、粮仓的粮食陈陈相因，为汉"
     "武帝北击匈奴攒下雄厚国力（「京师之钱累巨万，贯朽而不可校；太仓之粟陈陈相"
     "因」——《史记》）。缇萦救父：少女上书愿代父受刑，文帝感动废除肉刑——仁"
     "政与孝道佳话。",
     ["文景之治是哪个皇帝时期", "休养生息政策的内容", "缇萦救父的典故",
      "文景之治为谁攒下国力", "史记怎么记载文景之治", "中国第一个盛世"],
     ["问汉武帝扩张", "问历代治世对比"],
     "atomic", "",
     "文景之治=汉文帝/景帝(前180-141·首个盛世)：休养生息=三十税一/废肉刑(缇萦救父)/节俭(文帝 23 年不增宫室)；钱贯朽粟陈相因→汉武帝击匈奴资本。"),
]

QUESTIONS = [
    ("QB-397", "磁铁能吸引什么材料", "物理学", "技术直答",
     ["铁", "钴", "镍"], "通识拓展66"),
    ("QB-398", "酸性体质是真的吗", "生活常识", "技术直答",
     ["伪科学", "血液pH"], "通识拓展66"),
    ("QB-399", "细胞怎么数量增多", "生物学", "技术直答",
     ["细胞分裂"], "通识拓展66"),
    ("QB-400", "文景之治是哪个皇帝时期", "历史", "技术直答",
     ["汉文帝", "汉景帝"], "通识拓展66"),
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
                               "level:L2", "status:verified", "batch:通识拓展66"],
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
    bank["version"] = "v1.58"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
