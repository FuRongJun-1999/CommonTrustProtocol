# -*- coding: utf-8 -*-
"""seed_common_105_cards.py · 通识拓展批次105知识卡+题库（幂等）

105：物理学-长度与时间的测量/化学-洗涤用品的酸碱性/生物学-青春期发育/地理学-中国的世界之最
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_measurelen",
     "长度与时间的测量",
     "基础科学知识点内容（人话接口）", "物理学",
     "**长度测量**——基本工具刻度尺：使用规则①选（量程与分度值合适）；②放（刻"
     "度线紧贴被测物体、零刻度线对齐起点）；③读（视线正对刻度线，估读到分度值"
     "下一位）；④记（数值+单位——没单位的记录无意义）。特殊方法：累积法（测一"
     "张纸厚度——测 100 张除以 100）、滚轮法（测操场跑道）、化曲为直（棉线沿曲"
     "线摆好后拉直测量）。**时间测量**——停表（秒表）：小盘分钟、大盘秒（大盘一"
     "圈 30s，读数=小盘分+大盘秒；注意小盘指针过半格大盘读 30-60s）。国际单位："
     "长度米（m）、时间秒（s）。测量工具演进：游标卡尺（0.1/0.05/0.02mm 精度）、"
     "螺旋测微器（0.01mm）、激光测距（卫星激光测距毫米级）。",
     ["长度测量的基本工具", "刻度尺的使用规则", "怎么测一张纸的厚度",
      "停表怎么读数", "测量的单位", "什么是累积法"],
     ["问误差错误区别复习", "问游标卡尺读数"],
     "atomic", "",
     "长度=刻度尺(选放读记·估读到分度值下一位·必带单位)；特殊法=累积/滚轮/化曲为直；停表=小盘分+大盘秒(过半 30-60)；游标卡尺 0.02mm。"),
    ("kp_card_detergentph",
     "洗涤用品的酸碱性",
     "基础科学知识点内容（人话接口）", "化学",
     "洗涤用品的酸碱性与用途：①**肥皂/洗衣粉**——弱碱性（去油污力强，但碱性强"
     "刺激皮肤、伤丝毛——蛋白质纤维遇碱水解）；②**洗发水**——多数弱酸性或中性"
     "（头发主要成分角蛋白在强碱下受损毛糙，「弱酸性洗发水更护发」）；③**沐浴"
     "露**——接近皮肤 pH（皮肤表面弱酸性 pH 约 5.5，酸性保护膜抑菌）；④**中性洗"
     "涤剂**——洗涤丝毛类（真丝洗涤剂）。知识关联：皮肤表面弱酸性是天然保护屏"
     "障（酸性抑制多数病菌），所以频繁用碱性肥皂洗手洗脸会破坏皮肤屏障致干燥。 "
     "拓展：84 消毒液强碱性（与洁厕灵混用危险——chlorine 呼应）、厨房油污清洁剂"
     "强碱性、卫生间除垢剂酸性——酸碱分区使用避免混合。",
     ["洗涤剂的酸碱性", "洗发水为什么选弱酸性", "皮肤表面是酸性还是碱性",
      "洗衣粉和肥皂哪个碱性强", "丝毛衣物用什么洗", "84消毒液是酸性还是碱性"],
     ["问角蛋白与酸碱", "问清洁剂混用危险清单"],
     "atomic", "",
     "洗涤酸碱：肥皂洗衣粉弱碱(去油强·伤丝毛蛋白纤维)；洗发水弱酸护发；皮肤表面 pH≈5.5 弱酸保护膜——过度清洁破坏屏障；84 碱性+洁厕灵酸性=禁混。"),
    ("kp_card_puberty",
     "青春期的发育特点",
     "基础科学知识点内容（人话接口）", "生物学",
     "青春期是从童年到成年的过渡阶段（女约 10-18 岁、男约 12-20 岁），发育特点"
     "：①**身高突增**（最明显标志——身高体重迅速增长，骨密度增加）；②**第二性"
     "征出现**——性激素（睾丸分泌雄性激素/卵巢分泌雌性激素）作用：男性变声胡"
     "须喉结、女性乳房发育骨盆变宽，男女都出现腋毛阴毛；③神经系统与心肺功能增"
     "强（大脑兴奋性强——学习黄金期）；④生殖器官发育成熟（女性出现月经/男性出"
     "现遗精——正常生理现象不必恐慌）。心理特点：独立意识增强、情绪波动大、性"
     "意识萌动——需正确疏导。健康建议：均衡营养（钙铁补充）、保证睡眠（生长激"
     "素夜间分泌高峰）、坚持运动、坦诚与父母老师沟通。",
     ["青春期的发育特点", "第二性征是什么", "月经和遗精正常吗",
      "青春期身高为什么突增", "青春期的心理变化", "如何健康度过青春期"],
     ["问性激素作用机制", "问青春期营养需求"],
     "atomic", "",
     "青春期(女 10-18/男 12-20)=身高突增+第二性征(性激素作用)+器官功能增强+生殖成熟(月经/遗精=正常现象)；心理=独立意识+情绪波动；健康=营养睡眠运动沟通。"),
    ("kp_card_chinasuper",
     "中国的世界之最（地理）",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国地理世界之最盘点：①世界最高的高原——青藏高原（平均 4000m+，「世界屋"
     "脊」）；②世界最高的山峰——珠穆朗玛峰（8848.86m）；③世界最大的高原湖群—"
     "—青藏高原湖区；④世界最大的黄土堆积区——黄土高原；⑤世界最大的煤炭生产"
     "国/稀土储量第一；⑥世界最长的人工运河——京杭大运河（约 1794 公里）；⑦世界"
     "最大的水利枢纽——三峡工程；⑧世界海拔最高的铁路——青藏铁路（唐古拉山口 "
     "5072m）；⑨世界最大的城墙——长城；⑩世界最大的宫殿群——故宫。中国之「最大"
     "省份」：面积最大=新疆、人口最多（曾）=河南现广东、少数民族最多省=云南、丘"
     "陵最多=福建（「八山一水一分田」）。",
     ["中国的世界之最", "世界最大的高原", "京杭大运河有多长",
      "三峡是世界最大的什么", "中国面积最大的省级行政区", "哪个省少数民族最多"],
     ["问世界地理之最", "问中国之最知识竞赛"],
     "atomic", "",
     "中国世界之最：青藏最高原+珠峰最高峰+黄土最大黄土区+三峡最大水利枢纽+青藏铁路最高+京杭运河最长人工河(1794km)+故宫最大宫殿群；最大省级=新疆·少数民族最多省=云南。"),
]

QUESTIONS = [
    ("QB-553", "长度测量的基本工具", "物理学", "技术直答",
     ["刻度尺"], "通识拓展105"),
    ("QB-554", "洗涤剂的酸碱性", "化学", "技术直答",
     ["肥皂", "弱碱"], "通识拓展105"),
    ("QB-555", "青春期的发育特点", "生物学", "技术直答",
     ["身高突增", "第二性征"], "通识拓展105"),
    ("QB-556", "中国的世界之最", "地理学", "技术直答",
     ["青藏高原", "珠峰"], "通识拓展105"),
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
                               "level:L2", "status:verified", "batch:通识拓展105"],
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
    bank["version"] = "v1.97"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
