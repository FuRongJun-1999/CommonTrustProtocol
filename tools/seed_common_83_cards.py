# -*- coding: utf-8 -*-
"""seed_common_83_cards.py · 通识拓展批次83知识卡+题库（幂等）

83：物理学-奥斯特实验/化学-绿色化学/生物学-病毒的结构与生活/地理学-中国农业分布
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_oersted",
     "奥斯特实验：电流的磁效应",
     "基础科学知识点内容（人话接口）", "物理学",
     "1820 年丹麦物理学家**奥斯特**在课堂上偶然发现：导线通电时，旁边的小磁针"
     "发生偏转——证明**电流周围存在磁场**（电流的磁效应，电生磁）。这是人类第一"
     "次揭示电与磁的联系（此前认为二者无关）——恩格斯称之为「打开了电磁学的大"
     "门」。应用：电磁铁（通电有磁、断电无磁，磁性强弱可由电流大小/线圈匝数控"
     "制）——电磁起重机/电铃/电磁继电器（用低电压弱电流控制高电压强电流的「自"
     "动开关」）/扬声器。后续：安培研究电流间作用力、法拉第 1831 年发现电磁感应"
     "（磁生电——发电机），电与磁的大统一开启电气时代。通电螺线管磁场与条形磁"
     "铁相似，极性可用安培定则（右手螺旋）判断。",
     ["奥斯特实验说明了什么", "什么是电流的磁效应", "电磁铁的原理",
      "电磁继电器的作用", "法拉第发现了什么", "通电螺线管的磁场"],
     ["问右手螺旋定则", "问电铃电路原理"],
     "atomic", "",
     "奥斯特 1820：通电导线使磁针偏转=电流周围存在磁场(电生磁)；应用=电磁铁(可控)→起重机/继电器/扬声器；法拉第 1831 反向磁生电→发电机；右手螺旋判极性。"),
    ("kp_card_greenchem",
     "绿色化学：从源头防污染",
     "基础科学知识点内容（人话接口）", "化学",
     "绿色化学（环境友好化学）核心理念：**从源头上减少或消除污染**，而不是先污"
     "染再治理。原则要点：①原料可再生（生物质替代石油）；②反应原子经济性——尽"
     "可能让原料原子全部进入产物（原子利用率 100% 最理想，减少废料）；③使用无"
     "毒无害的溶剂与催化剂（水相反应/超临界 CO₂ 替代有机溶剂）；④产品环境友"
     "好、可降解。实例：可降解塑料替代传统塑料、生物柴油、二氧化碳作发泡剂替代"
     "氟利昂、催化裂解提高汽油收率。「末端治理」vs「源头防治」：建污水处理厂是"
     "末端，改工艺少产污水是绿色化学思路。与碳中和关系：绿色化学是实现碳减排的"
     "工业路径之一。",
     ["绿色化学的核心理念", "什么是原子经济性", "末端治理和源头防治的区别",
      "绿色化学的实例", "为什么要发展绿色化学", "可降解塑料的原理"],
     ["问原子经济性计算", "问生物质能化工"],
     "atomic", "",
     "绿色化学=源头防污染非末端治理：原料可再生/原子经济性 100% 理想/无毒溶剂/产品可降解；实例=可降解塑料·CO₂ 发泡·生物柴油；衔接碳中和。"),
    ("kp_card_virusstr",
     "病毒：没有细胞结构的寄生者",
     "基础科学知识点内容（人话接口）", "生物学",
     "病毒的结构极其简单：蛋白质外壳+内部的遗传物质（DNA 或 RNA 二者只居其"
     "一）——**没有细胞结构**，是已知最小的生命体（20-300 纳米，需电子显微镜才"
     "能看见）。生活方式：不能独立生活，必须**寄生**在活细胞内——靠自己遗传物"
     "质「劫持」宿主细胞的机器复制自己（离开活细胞通常变成结晶体不表现生命活"
     "动）。分类按宿主：动物病毒（流感/新冠/乙肝）、植物病毒（烟草花叶病毒）、"
     "细菌病毒=噬菌体（吞噬细菌——可治超级细菌感染的替代思路）。与人类的双面"
     "性：致病（流感/艾滋病/新冠）vs 利用（灭活疫苗/基因治疗载体/噬菌体疗法）。"
     "抗生素对病毒无效（只杀细菌）——感冒滥用抗生素是错误用药。",
     ["病毒有细胞结构吗", "病毒的结构", "病毒为什么必须寄生",
      "什么是噬菌体", "抗生素能治病毒感冒吗", "病毒的分类"],
     ["问疫苗类型对比", "问病毒演化与宿主跳转"],
     "atomic", "",
     "病毒=蛋白质外壳+DNA/RANA(居一)·无细胞结构·必须寄生活细胞复制；噬菌体=细菌病毒；抗生素只杀细菌不杀病毒——感冒滥服抗生素=错误用药；利用面=疫苗/载体/噬菌体疗法。"),
    ("kp_card_agridist",
     "中国农业的地区分布",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国农业分布差异鲜明，总体「东耕西牧、南稻北麦」：①种植业集中在东部季风"
     "区（湿润半湿润平原）——北方旱地（小麦/玉米/甜菜，东北一年一熟、华北两年三"
     "熟），南方水田（水稻/油菜/甘蔗，一年两熟到三熟）；②畜牧业集中在西部非季风"
     "区（内蒙古/新疆/青海/西藏四大牧区）；③林业在东北/西南/东南山区；④渔业集中"
     "在东部沿海与长江流域。南北差异界线=秦岭—淮河一线（1 月 0℃ 等温线+800mm "
     "等降水量线）：以北旱地种小麦杂粮、以南水田种水稻。影响因素：气候（热量/降"
     "水）是主导，地形水源土壤次之。「因地制宜」是农业布局的根本原则。",
     ["中国农业的地区分布", "南稻北麦是什么", "秦岭淮河一线的意义",
      "中国四大牧区", "影响农业分布的因素", "什么是因地制宜"],
     ["问商品粮基地", "问特色农业案例"],
     "atomic", "",
     "中国农业「东耕西牧、南稻北麦」：种植业在东部季风区/牧业在西部四牧区；秦岭淮河=1 月 0℃+800mm 线分旱地小麦与水田水稻；因地制宜为根本原则。"),
]

QUESTIONS = [
    ("QB-465", "奥斯特实验说明了什么", "物理学", "技术直答",
     ["电流", "磁场"], "通识拓展83"),
    ("QB-466", "绿色化学的核心理念", "化学", "技术直答",
     ["源头", "减少污染"], "通识拓展83"),
    ("QB-467", "病毒有细胞结构吗", "生物学", "技术直答",
     ["没有", "蛋白质", "核酸"], "通识拓展83"),
    ("QB-468", "中国农业的地区分布", "地理学", "技术直答",
     ["东耕西牧", "南稻北麦"], "通识拓展83"),
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
                               "level:L2", "status:verified", "batch:通识拓展83"],
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
    bank["version"] = "v1.75"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
