# -*- coding: utf-8 -*-
"""seed_common_05_cards.py · 通识拓展批次知识卡（幂等）

05：化学-酸碱中和/生物-细胞结构/天文-月相变化/数学-百分数
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_acidbase",
     "酸碱中和反应",
     "基础科学知识点内容（人话接口）", "化学",
     "酸碱中和反应：酸和碱反应生成盐和水——HCl + NaOH → NaCl + H₂O。本质是"
     "酸中的氢离子（H⁺）与碱中的氢氧根离子（OH⁻）结合生成水。中和反应应用广"
     "泛：服用含氢氧化铝的胃药中和过多胃酸、用熟石灰改良酸性土壤、蚊虫叮咬分"
     "泌蚁酸可用碱性肥皂水中和止痒。pH<7 为酸性、pH=7 为中性、pH>7 为碱性。",
     ["什么是酸碱中和反应", "酸碱中和", "中和反应的例子", "胃酸过多怎么办",
      "pH值的范围", "pH值怎么判断酸碱性"],
     ["问氧化还原", "问化学键类型"],
     "atomic", "",
     "中和 = 酸+碱→盐+水（H⁺+OH⁻→H₂O）；应用=胃药/改良土壤/肥皂水止痒；pH<7酸/=7中性/>7碱。"),
    ("kp_card_cellstructure",
     "细胞的基本结构",
     "基础科学知识点内容（人话接口）", "生物学",
     "动物细胞与植物细胞的基本结构：①细胞膜——控制物质进出（所有细胞都有）；"
     "②细胞质——生命活动的主要场所；③细胞核——含遗传物质DNA，是细胞控制中"
     "心。植物细胞特有：细胞壁（支持保护）、液泡（含细胞液）、叶绿体（光合作用"
     "场所）。细胞是生物体结构和功能的基本单位。",
     ["细胞的基本结构", "细胞有哪些结构", "动物细胞和植物细胞的区别",
      "细胞膜的作用", "叶绿体是什么", "细胞核的功能"],
     ["问细胞分裂", "问DNA复制"],
     "atomic", "",
     "细胞基本结构 = 细胞膜+细胞质+细胞核；植物特有 = 细胞壁+液泡+叶绿体。"),
    ("kp_card_moonphase",
     "月相变化的规律",
     "基础科学知识点内容（人话接口）", "天文学",
     "月相变化周期约 29.5 天（朔望月），按新月（朔，不见月）→娥眉月→上弦月"
     "（初七初八，右半亮）→盈凸月→满月（望，十五六，全亮）→亏凸月→下弦月"
     "（廿二三，左半亮）→残月→新月的顺序循环。口诀「上上上西西、下下下东东」"
     "——上弦月上半年出现在上半夜西边天空，下弦月下半年夜出现在东边天空。",
     ["月相变化的规律", "什么是月相", "月相变化顺序", "什么是满月和新月",
      "上弦月和下弦月", "月相变化周期"],
     ["问日食月食", "问潮汐"],
     "atomic", "",
     "月相循环 = 新月→娥眉→上弦→盈凸→满月→亏凸→下弦→残月，周期 29.5 天。"),
    ("kp_card_percentage",
     "百分数的意义与运算",
     "基础科学知识点内容（人话接口）", "数学",
     "百分数：表示一个数是另一个数的百分之几的数，用 % 号表示——只表示比例"
     "关系不带单位。换算：百分数→小数去掉 % 号小数点左移两位（25%→0.25）；小"
     "数→百分数右移两位加 %。常见应用：折扣（七折=原价的70%）、增长率、合格"
     "率、含盐率。增长率可以超过 100%，但比例（如及格率）不能超过 100%。",
     ["什么是百分数", "百分数", "百分数怎么算", "折扣怎么计算",
      "百分数和小数怎么换算", "百分数的应用"],
     ["问利率计算", "问统计图表"],
     "atomic", "",
     "百分数 = 占另一个数的百分之几；换算=去 % 小数点左移两位；折扣/增长率/合格率常用。"),
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
                               "level:L2", "status:verified", "batch:通识拓展05"],
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
