# -*- coding: utf-8 -*-
"""seed_n7_v3_cards.py · 白箱知识域拓展第二批知识卡（幂等·全天制第二批）

夜批N7：热力学定律/电学电路/植物学/统计学 四域各一张，
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_thermolaws",
     "热力学三大定律",
     "基础科学知识点内容（人话接口）", "热力学",
     "热力学三大定律：第一定律（能量守恒）——能量不能凭空产生或消失，只能转化"
     "或转移，永动机不可能制成；第二定律（熵增原理）——热量自发从高温流向低温，"
     "孤立系统的熵（无序度）永不减少，因此热机效率必小于 100%；第三定律（绝对"
     "零度不可达）——温度越低降温越难，绝对零度（-273.15°C）只能无限接近。",
     ["热力学三大定律", "热力学定律", "什么是熵增原理", "第一定律第二定律第三定律",
      "永动机为什么不可能", "绝对零度是多少"],
     ["问卡诺循环", "问比热容"],
     "atomic", "",
     "三大定律 = 能量守恒（永动机不可能）+ 熵增（热量自发高温→低温）+ 绝对零度 -273.15°C 不可达。"),
    ("kp_card_circuit",
     "串联与并联电路",
     "基础科学知识点内容（人话接口）", "电学",
     "串联与并联电路：串联=元件首尾相连成一条路径，电流处处相同，总电阻等于各"
     "电阻之和，一处断路全部断（如老式圣诞灯串）；并联=元件并列接在同一对节点"
     "间，电压处处相同，总电阻的倒数等于各电阻倒数之和（并联总电阻小于任一支路），"
     "一条支路断路其他支路照常工作（如家庭电路全部并联）。",
     ["串联和并联电路", "串联并联的区别", "什么是串联电路", "什么是并联电路",
      "家庭电路是串联还是并联", "总电阻怎么算"],
     ["问欧姆定律", "问半导体"],
     "atomic", "",
     "串联=一条路电流同/电阻相加/一断全断；并联=同压并列/总电阻更小/互不影响（家庭电路）。"),
    ("kp_card_photosyn",
     "光合作用",
     "基础科学知识点内容（人话接口）", "植物学",
     "光合作用：绿色植物利用叶绿体中的叶绿素，吸收光能，把二氧化碳和水合成为"
     "有机物（葡萄糖）并释放氧气的过程。公式：6CO₂ + 6H₂O + 光能 → C₆H₁₂O₆"
     " + 6O₂。条件=光、叶绿体、二氧化碳、水；场所=叶绿体；意义=把光能转为化学"
     "能储存、为几乎所有生命提供食物与氧气的源头。",
     ["什么是光合作用", "光合作用", "光合作用的公式", "植物为什么释放氧气",
      "光合作用需要什么条件", "叶绿体的作用"],
     ["问呼吸作用", "问蒸腾作用"],
     "atomic", "",
     "光合作用 = 6CO₂+6H₂O+光能→葡萄糖+6O₂（叶绿体内）；能量与氧气几乎全部生命的源头。"),
    ("kp_card_statistics",
     "平均数、中位数与众数",
     "基础科学知识点内容（人话接口）", "统计学",
     "三个集中趋势指标：平均数=所有数之和除以个数（易受极端值拉偏）；中位数="
     "排序后正中间的数（不受极端值影响，收入统计常用）；众数=出现次数最多的数"
     "（可用于非数值数据）。例：2,3,3,5,100——平均数 22.6（被 100 拉高）、中位数"
     " 3、众数 3。数据有极端值时看中位数更真实。",
     ["平均数中位数众数", "平均数怎么算", "中位数是什么", "什么是众数",
      "平均数和中位数的区别", "什么时候用中位数"],
     ["问方差标准差", "问正态分布"],
     "atomic", "",
     "平均数=总和÷个数（怕极端值）；中位数=排序中间值（稳健）；众数=出现最多。"),
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
                "name": f"{name}（{dgroup}·基础科学知识卡）",
                "生效条件": conds,
                "子功能": f"{name}——基础科学高频问题知识条目",
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
                               "level:L2", "status:verified", "batch:白箱拓展第二批"],
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
