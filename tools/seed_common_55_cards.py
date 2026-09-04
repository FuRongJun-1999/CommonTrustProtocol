# -*- coding: utf-8 -*-
"""seed_common_55_cards.py · 通识拓展批次55知识卡+题库（幂等）

55：物理学-透镜与照相机/化学-淀粉与麦芽糖/生物学-达尔文自然选择/地理学-日本岛国
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_lenscam",
     "凸透镜成像与照相机",
     "基础科学知识点内容（人话接口）", "物理学",
     "凸透镜（中间厚边缘薄）成像规律（f=焦距）：物距 u>2f——倒立缩小实像（照相"
     "机/眼睛）；u=2f——等大实像；f<u<2f——倒立放大实像（投影仪/幻灯机）；u<f"
     "——正立放大**虚像**（放大镜）。口诀「一倍焦距分虚实，二倍焦距分大小」。照"
     "相机：镜头（凸透镜组）把远处的景物成像在感光元件（胶片/CMOS）上——「近"
     "摄远景」靠改变镜头到感光面的距离（对焦）；光圈控制进光量、快门控制曝光时"
     "间。凹透镜（中间薄）只成正立缩小虚像（近视镜）。老花镜是凸透镜（远视矫"
     "正）。人眼与照相机的对应：瞳孔≈光圈、晶状体≈镜头、视网膜≈感光元件。",
     ["照相机的镜头是什么透镜", "凸透镜成像规律", "什么是实像和虚像",
      "投影仪和照相机的成像有什么不同", "放大镜是什么透镜", "人眼和照相机的对应关系"],
     ["问透镜公式1/u+1/v=1/f", "问近视远视矫正原理复习"],
     "atomic", "",
     "凸透镜：u>2f 倒缩实(相机/眼)·f<u<2f 倒大实(投影)·u<f 正大虚(放大镜)；口诀一倍焦距分虚实二倍焦距分大小；凹透镜只成缩虚(近视镜)；瞳孔=光圈/晶状体=镜头/视网膜=底片。"),
    ("kp_card_starchmalt",
     "淀粉与麦芽糖：米饭越嚼越甜",
     "基础科学知识点内容（人话接口）", "化学",
     "米饭馒头主要成分是淀粉（多糖，(C₆H₁₀O₅)n）——本身无甜味；长时间咀嚼变"
     "甜，是因为唾液中的**唾液淀粉酶**把淀粉水解成麦芽糖（二糖，有甜味）——这"
     "也是「细嚼慢咽助消化」的化学依据。淀粉的特性反应：遇碘变蓝（检验淀粉的经"
     "典方法——蓝紫色）。麦芽糖在肠道继续被酶水解成葡萄糖（单糖）才能被吸收利"
     "用——葡萄糖是细胞的主要能源物质（血糖）。淀粉与纤维素都是葡萄糖的聚合物，"
     "人能消化淀粉却不能消化纤维素（没有相应酶），纤维素作为膳食纤维促进肠道蠕"
     "动。淀粉遇碘变蓝 vs 蛋白质双缩脲变紫、灼烧焦毛味——三大检验法。",
     ["米饭咀嚼为什么会变甜", "淀粉遇碘会怎样", "麦芽糖和葡萄糖的区别",
      "人为什么不能消化纤维素", "什么是血糖", "淀粉是多糖吗"],
     ["问酶的高效专一性", "问糖尿病与血糖调控"],
     "atomic", "",
     "淀粉(多糖·无甜)→唾液淀粉酶→麦芽糖(甜)→葡萄糖(吸收·血糖)；淀粉遇碘变蓝=经典检验；人无纤维素酶(膳食纤维促蠕动)；三大检验=碘蓝/双缩脲紫/焦毛味。"),
    ("kp_card_darwin",
     "达尔文与自然选择",
     "基础科学知识点内容（人话接口）", "生物学",
     "达尔文（1809-1882）1859 年出版《物种起源》，提出**自然选择学说**——进化"
     "论的核心：①过度繁殖（生物产生远超存活量的后代）；②生存斗争（资源有限，"
     "后代互相竞争）；③遗传变异（后代各有微小差异）；④适者生存（有利变异被保"
     "留，不利者淘汰）——长期定向选择导致新物种形成。经典案例：加拉帕戈斯群岛"
     "地雀——不同岛喙形不同（适应各自食物），被称为「达尔文雀」。演化常被误读"
     "为「进化=进步」：自然选择无方向、只论当下适应（「适应」不等于「高级」）。"
     "现代综合进化论补充了遗传学（基因突变是变异来源）；拉马克「用进废退」是早"
     "期假说（已被修正）。与孟德尔遗传定律并称现代生物学两大基石。",
     ["自然选择学说是谁提出的", "《物种起源》是哪一年出版的", "自然选择学说的内容",
      "达尔文雀是什么", "用进废退是谁的观点", "进化论有方向吗"],
     ["问孟德尔豌豆实验", "问分子钟与共同祖先"],
     "atomic", "",
     "达尔文《物种起源》1859·自然选择四要点=过度繁殖/生存斗争/遗传变异/适者生存；达尔文雀=喙形适应例证；演化无方向只论适应；拉马克用进废退已被修正。"),
    ("kp_card_japan",
     "日本：多火山地震的岛国",
     "人文通识知识点内容（人话接口）", "地理学",
     "日本是东亚岛国：由北海道、本州、四国、九州四大岛及数千小岛组成（本州最大"
     "），面积约 37.8 万平方公里；首都东京（世界人口最多的都市圈）。多火山地震："
     "位于太平洋板块与亚欧板块交界处（环太平洋火山地震带——「太平洋火环」），全"
     "国有 100 多座活火山，富士山（3776 米，活火山）是其象征；全球约 10% 的地震"
     "发生在日本及周边（1923 关东大地震、2011 东日本大地震并引发海啸与福岛核电"
     "站事故）。资源贫乏但经济发达：进口原料加工出口（进口能源铁矿石→汽车电子精"
     "密仪器输出）；渔业发达（北海道渔场=日本暖流与千岛寒流交汇）。文化符号：樱"
     "花、和服、寿司、茶道。",
     ["日本是个什么样的国家", "日本为什么多火山地震", "富士山是活火山吗",
      "日本的四大岛", "北海道渔场的成因", "日本的经济特点"],
     ["问板块构造三类型边界", "问海啸预警机制"],
     "atomic", "",
     "日本=四岛(北海道本州四国九州)+数千小岛·37.8万km²·东京；多火山地震=太平洋/亚欧板块交界(火环)·富士山活火山；资源贫乏→加工贸易型经济；北海道渔场=暖寒流交汇。"),
]

QUESTIONS = [
    ("QB-353", "照相机的镜头是什么透镜", "物理学", "技术直答",
     ["凸透镜"], "通识拓展55"),
    ("QB-354", "米饭咀嚼为什么会变甜", "化学", "技术直答",
     ["淀粉", "麦芽糖", "唾液"], "通识拓展55"),
    ("QB-355", "自然选择学说是谁提出的", "生物学", "技术直答",
     ["达尔文"], "通识拓展55"),
    ("QB-356", "日本为什么多火山地震", "地理学", "技术直答",
     ["板块交界", "环太平洋"], "通识拓展55"),
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
                               "level:L2", "status:verified", "batch:通识拓展55"],
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
    bank["version"] = "v1.47"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
