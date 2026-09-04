# -*- coding: utf-8 -*-
"""seed_common_22_cards.py · 通识拓展批次22知识卡+题库（幂等）

22：化学-铁生锈/地理学-七大洲四大洋/生物学-骆驼驼峰/历史-春节与春联
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_rust",
     "铁生锈的条件与防锈",
     "基础科学知识点内容（人话接口）", "化学",
     "铁生锈是缓慢氧化：铁与氧气、水同时接触才会生锈——两者缺一不可（干燥空"
     "气中的铁不生锈，完全隔绝氧气的水中铁也不生锈）。铁锈主要成分是氧化铁，"
     "疏松多孔、不能保护内部金属，所以铁器锈穿；这与铝不同——铝表面氧化铝薄膜"
     "致密致密反而「自我保护」。防锈思路就是破坏生锈条件：刷漆/涂油/镀层（隔"
     "绝氧气和水）、保持干燥、制成不锈钢（加铬镍改变内部结构）。",
     ["铁为什么会生锈", "铁生锈需要什么条件", "铁锈的主要成分",
      "怎么防止铁生锈", "铝为什么不容易生锈", "不锈钢为什么不生锈"],
     ["问电化学腐蚀细节", "问金属冶炼"],
     "atomic", "",
     "铁生锈=氧气+水同时接触的缓慢氧化，缺一不可；铁锈=氧化铁(疏松不护内)；防锈=隔氧隔水/干燥/不锈钢。"),
    ("kp_card_continents",
     "七大洲与四大洋",
     "人文通识知识点内容（人话接口）", "地理学",
     "七大洲（按面积从大到小）：亚洲、非洲、北美洲、南美洲、南极洲、欧洲、大"
     "洋洲——口诀「亚非北南美，南极欧大洋」；亚洲最大（约4400万平方公里），大"
     "洋洲最小；亚洲与欧洲陆地相连合称亚欧大陆，以乌拉尔山脉-乌拉尔河-里海-高"
     "加索山脉为界，是最大的一块大陆；南极洲是唯一没有常住人口的洲。四大洋："
     "太平洋（最大最深，马里亚纳海沟约11000米为大洋最深处）、大西洋、印度洋、"
     "北冰洋（最小最浅、跨经度最广）。",
     ["世界上面积最大的洲是哪个", "七大洲按面积怎么排", "四大洋哪个最大",
      "世界最深处马里亚纳海沟", "跨经度最广的大洋", "亚欧大陆",
      "世界七大洲和四大洋", "七大洲四大洋", "最小的洲是哪个洲",
      "亚洲和欧洲的分界线"],
     ["问板块漂移细节", "问各国地形"],
     "atomic", "",
     "七大洲=亚非北南美南极欧大洋(亚洲最大·大洋洲最小)；四大洋=太平洋(最大最深)/大西洋/印度洋/北冰洋(跨经度最广)。"),
    ("kp_card_camel",
     "骆驼驼峰的秘密",
     "基础科学知识点内容（人话接口）", "生物学",
     "骆驼的驼峰里储存的是脂肪，不是水——脂肪在体内氧化时既提供能量，又产生代"
     "谢水，帮助骆驼在缺少食物和水的沙漠里坚持数周。其他沙漠适应：体温可在一定"
     "范围内波动（减少出汗失水）、双排睫毛+可闭合的鼻孔挡风沙、宽大的脚掌不陷"
     "沙、耐渴时一次能饮下大量水快速补水。「驼峰储水」是最常见的误解。",
     ["骆驼的驼峰里储存的是什么", "驼峰里存的是水吗", "骆驼为什么耐渴",
      "骆驼有哪些沙漠适应", "脂肪代谢能产生水吗", "骆驼几天不喝水"],
     ["问其他沙漠动物", "问反刍消化"],
     "atomic", "",
     "驼峰=脂肪(非水)：氧化供能+代谢产水；配套适应=体温波动/双排睫毛/闭鼻孔/宽脚掌。"),
    ("kp_card_springfestival",
     "春节与贴春联的由来",
     "人文通识知识点内容（人话接口）", "历史",
     "春节是农历正月初一，中国最隆重的传统节日。贴春联源于古代的「桃符」——"
     "古人悬挂桃木板（传说桃木驱邪）于门旁；五代后蜀君主孟昶题写的「新年纳余"
     "庆，嘉节号长春」被认为是中国最早的春联；宋代起造纸术普及、纸质春联盛行"
     "（当时称「春贴」），明代起广泛普及并定名「春联」。王安石《元日》「千门万"
     "户曈曈日，总把新桃换旧符」记录了这一习俗。春节习俗还有：除夕守岁/年夜"
     "饭/拜年/压岁钱/贴福字倒贴寓意「福到」。",
     ["贴春联的习俗是怎么来的", "最早的春联是什么", "春联和桃符的关系",
      "春节是农历哪一天", "为什么福字要倒着贴", "总把新桃换旧符什么意思"],
     ["问端午中秋等其他节日", "问生肖完整顺序"],
     "atomic", "",
     "春联源于桃符（桃木驱邪）→五代孟昶「新年纳余庆」=最早春联→宋代春贴→明代普及定名；福字倒贴=「福到」。"),
]

QUESTIONS = [
    ("QB-221", "铁为什么会生锈", "化学", "技术直答",
     ["氧气", "水", "氧化"], "通识拓展22"),
    ("QB-222", "世界上面积最大的洲是哪个", "地理学", "技术直答",
     ["亚洲"], "通识拓展22"),
    ("QB-223", "骆驼的驼峰里储存的是什么", "生物学", "技术直答",
     ["脂肪"], "通识拓展22"),
    ("QB-224", "贴春联的习俗是怎么来的", "历史", "技术直答",
     ["桃符", "孟昶"], "通识拓展22"),
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
                               "level:L2", "status:verified", "batch:通识拓展22"],
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
    bank["version"] = "v1.14"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
