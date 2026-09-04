# -*- coding: utf-8 -*-
"""seed_common_94_cards.py · 通识拓展批次94知识卡+题库（幂等）

94：物理学-磁场与磁感线/化学-酸碱盐的定义/生物学-食物链书写规则/地理学-农业的部门
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_maglines",
     "磁场与磁感线",
     "基础科学知识点内容（人话接口）", "物理学",
     "磁体周围存在**磁场**（看不见摸不着但真实存在的特殊物质——对放入其中的磁"
     "体产生磁力作用）。**磁感线**是为描述磁场而**假想的曲线**（不是真实存在的"
     "线！）：从磁体 N 极出来回到 S 极（磁体内部则从 S 到 N），越密处磁场越强。"
     "常见磁感线分布：条形磁铁（两端最密=磁性最强）、蹄形磁铁、通电螺线管（与条"
     "形磁铁相似，极性用安培定则/右手螺旋定则判断——右手四指沿电流方向，大拇指"
     "指 N 极）。地球是个大磁体（地磁场）——指南针原理；地磁两极与地理两极相反"
     "且不重合（磁偏角，沈括最早记载）。磁场对放入其中的磁体产生磁力的作用，磁"
     "极间规律：同名磁极相斥、异名磁极相吸。",
     ["磁感线是真实存在的线吗", "磁感线从哪个极出来", "安培定则怎么用",
      "地磁场和地理南北极重合吗", "磁极间的相互作用规律", "什么是磁场"],
     ["问电磁铁磁性强弱", "问磁偏角与指南针史"],
     "atomic", "",
     "磁场=真实存在的物质；磁感线=假想曲线(N出S回·密=强)非实物；通电螺线管极性=安培定则(右手螺旋)；地磁两极与地理相反不重合(沈括记磁偏角)；同名斥异名吸。"),
    ("kp_card_abbdefinition",
     "酸、碱、盐的定义",
     "基础科学知识点内容（人话接口）", "化学",
     "**酸**：解离出的阳离子**全部是氢离子（H⁺）**的化合物——盐酸 HCl、硫酸"
     " H₂SO₄、硝酸 HNO₃、碳酸 H₂CO₃；性质：使紫色石蕊变红（酚酞不变色）、与活"
     "泼金属/金属氧化物/碱/某些盐反应，有酸味（食用醋/柠檬酸）。**碱**：解离出的"
     "阴离子**全部是氢氧根离子（OH⁻）**的化合物——氢氧化钠 NaOH（烧碱/火碱/"
     "苛性钠）、氢氧化钙 Ca(OH)₂（熟石灰/消石灰）、氨水 NH₃·H₂O；性质：使石蕊"
     "变蓝、酚酞变红，滑腻感（肥皂）。**盐**：金属离子（或铵根 NH₄⁺）+酸根离子"
     "构成的化合物——食盐 NaCl、纯碱 Na₂CO₃（是盐不是碱！）、碳酸钙、硫酸铜。"
     "酸碱中和：酸+碱→盐+水（胃酸用氢氧化铝中和的原理）。",
     ["酸碱盐的定义", "纯碱是碱吗", "酸使石蕊变什么色", "什么是中和反应",
      "烧碱的化学名称", "胃酸过多用什么中和"],
     ["问 pH 与酸碱度", "问常见酸碱盐俗名"],
     "atomic", "",
     "酸=阳离子全 H⁺(盐酸硫酸硝酸·石蕊红)；碱=阴离子全 OH⁻(烧碱/熟石灰/氨水·酚酞红)；盐=金属离子+酸根(纯碱 Na₂CO₃ 是盐非碱)；中和=酸+碱→盐+水。"),
    ("kp_card_foodchainrule",
     "食物链的书写规则",
     "基础科学知识点内容（人话接口）", "生物学",
     "食物链书写的规则（foodchain 概念卡的规范版）：①**起点必须是生产者**（绿色"
     "植物——不能从阳光或分解者开始）；②箭头指向**捕食者**（表示物质和能量流动"
     "方向：草→兔→鹰，被吃者→吃者）；③**不包括分解者**（细菌真菌不写入食物"
     "链）和非生物成分（阳光/水/土壤）；④食物链内只写生物名称。常见错误：把「狐"
     "狸吃兔」写成「兔→狐狸」（方向反了）；写成「阳光→草→兔」。食物网：多条食"
     "物链交织（一种生物可被多种捕食者吃）。营养级：生产者是第一营养级，往上依"
     "次递增；能量沿食物链**逐级递减**（10%~20% 传递效率）——所以营养级一般不超"
     "过 4-5 级，顶级捕食者（虎/鹰）数量必然稀少。食物链积累效应：有害物质（重金"
     "属/农药）沿食物链**逐级富集**——鹰体内 DDT 浓度可达水中数万倍（《寂静的春"
     "天》警示）。",
     ["食物链书写的规则", "食物链从什么开始写", "食物链包括分解者吗",
      "为什么营养级不超过五级", "有害物质在食物链中怎么变化", "什么是食物网"],
     ["问能量流动计算", "问生物富集案例"],
     "atomic", "",
     "食物链规则=起点生产者+箭头指捕食者+不含分解者非生物；营养级递增·能量逐级递减 10-20%（故虎鹰稀少）；生物富集=有害物沿链倍增(鹰 DDT 数万倍·《寂静的春天》)。"),
    ("kp_card_agrisections",
     "农业的五大部门",
     "人文通识知识点内容（人话接口）", "地理学",
     "农业主要包括五个部门：①**种植业**（耕作业）——在耕地上栽培农作物（粮/棉/"
     "油/糖/菜），是中国农业的主体（东部季风区平原盆地）；②**林业**——培育保护"
     "森林（木材/经济林/防护林——三北防护林工程），分布山区；③**畜牧业**——放"
     "牧牲畜（牛羊马）与圈养（猪禽），分牧区畜牧（西部四大牧区：内蒙古/新疆/青"
     "海/西藏）与农耕区畜牧（东部农区养猪禽）；④**渔业**（水产业）——海洋捕捞与"
     "养殖、淡水养殖（东南沿海与长江流域——「渔米之乡」）；⑤副业——附带生产。"
     "农业是国民经济的基础（「无农不稳」）；中国用世界约 9% 的耕地养活世界近 20%"
     " 的人口——粮食安全是头等大事（谷物基本自给、口粮绝对安全）。",
     ["农业主要包括哪些部门", "中国四大牧区", "种植业分布在哪",
      "农业在国民经济中的地位", "中国用多少耕地养活多少人口", "渔业分布在哪里"],
     ["问现代农业新业态", "问耕地保护政策"],
     "atomic", "",
     "农业五部门=种植业(主体·东部季风区)/林业(山区·三北防护林)/畜牧业(牧区四区+农区)/渔业(东南沿海长江流域)/副业；农业=国民经济基础；9% 耕地养活近 20% 人口。"),
]

QUESTIONS = [
    ("QB-509", "磁感线是真实存在的线吗", "物理学", "技术直答",
     ["不是", "假想"], "通识拓展94"),
    ("QB-510", "纯碱是碱吗", "化学", "技术直答",
     ["不是", "盐"], "通识拓展94"),
    ("QB-511", "食物链书写的规则", "生物学", "技术直答",
     ["生产者", "捕食者", "不含分解者"], "通识拓展94"),
    ("QB-512", "农业主要包括哪些部门", "地理学", "技术直答",
     ["种植业", "林业", "畜牧业", "渔业"], "通识拓展94"),
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
                               "level:L2", "status:verified", "batch:通识拓展94"],
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
    bank["version"] = "v1.86"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
