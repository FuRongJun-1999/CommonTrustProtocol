# -*- coding: utf-8 -*-
"""seed_common_61_cards.py · 通识拓展批次61知识卡+题库（幂等）

61：物理学-速度/化学-金属回收/生物学-生物圈/语文-汉字造字法
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_velocity",
     "速度：表示运动快慢的物理量",
     "基础科学知识点内容（人话接口）", "物理学",
     "速度（v）=路程÷时间（v=s/t，单位米/秒 m/s，常用 km/h），表示物体运动快"
     "慢的物理量——换算：1 m/s=3.6 km/h（72km/h=20m/s）。匀速直线运动：快慢不"
     "变、沿直线（最简单的机械运动）；变速运动用平均速度描述（龟兔赛跑：全程平"
     "均速度兔子未必赢——它睡觉时间太长）。常见速度感：人步行约 1.1m/s（4km/"
     "h）、自行车约 5m/s、高速铁路 300km/h（约 83m/s）、声音 340m/s、光 3×10⁸"
     "m/s。测速应用：高速区间测速（两个监测点算平均速度）、雷达测速（多普勒效"
     "应）。s-t 图像：过原点的直线表示匀速（斜率越大越快）；水平线表示静止。",
     ["速度是表示什么的物理量", "速度的计算公式", "1m/s等于多少km/h",
      "什么是匀速直线运动", "高铁每秒跑多少米", "区间测速的原理"],
     ["问s-t v-t图像判读", "问平均速度陷阱题"],
     "atomic", "",
     "速度 v=s/t(m/s·1m/s=3.6km/h)=运动快慢；匀速直线=快慢不变沿直线；变速用平均速度；步行 1.1/高铁 83/声 340/光 3×10⁸ m/s；区间测速=两点平均。"),
    ("kp_card_metalrecycle",
     "金属资源的回收利用",
     "基础科学知识点内容（人话接口）", "化学",
     "金属矿物是不可再生资源，回收废旧金属意义重大：①节约资源与能源——回收一"
     "个铝罐比从矿石炼铝节能约 95%（铝冶炼是耗电大户——电解氧化铝）；②减少污"
     "染（采矿尾矿/冶炼废气/废旧电池重金属渗漏——一节纽扣电池可污染 60 万升"
     "水）。金属回收流程：分类收集→熔炼再生→制品（废钢回炉/铝罐变新罐/铜线再"
     "生）。防金属锈蚀也是保护资源的另一面（涂油刷漆镀层——rust 卡呼应）。扩展"
     "矿物常识：地壳中含量最多的金属元素是**铝**（第二是铁），最多的元素是氧；"
     "铝矿=铝土矿、铁矿=磁铁矿/赤铁矿。金属活动性顺序（K Ca Na Mg Al Zn Fe Sn"
     " Pb (H) Cu Hg Ag Pt Au）决定冶炼难度：越活泼越难从矿石还原。",
     ["回收废旧金属的意义", "回收一个铝罐节约多少能源", "地壳中含量最多的金属",
      "一节纽扣电池能污染多少水", "金属活动性顺序", "怎么防止金属锈蚀"],
     ["问铝电解工艺", "问垃圾分类金属类"],
     "atomic", "",
     "回收金属=节能(铝省 95%)+减污(电池重金属)；地壳金属第一=铝(元素第一=氧)；活动序 K…Au 定冶炼难度；防腐=另一面保护资源(rust 呼应)。"),
    ("kp_card_biosphere",
     "生物圈：最大的生态系统",
     "基础科学知识点内容（人话接口）", "生物学",
     "生物圈是地球上所有生物及其环境的总和——**最大的生态系统**，范围：大气圈"
     "底部（飞鸟/微生物可达万米高空）、水圈的大部（海洋生物/深海热泉生物）、岩"
     "石圈表面（土壤表层动植物根系）——厚度约 20 公里的薄层。生态系统的组成：生"
     "物部分（生产者=绿色植物、消费者=动物、分解者=细菌真菌）+非生物部分（阳光/"
     "空气/水/温度/土壤）。生态系统的类型：森林/草原/海洋/淡水/湿地/农田/城市等"
     "——生物圈是它们的总装配。平衡与保护：生态系统中物质循环、能量沿食物链流"
     "动（逐级递减，10%-20% 传递效率）——人类活动破坏（滥伐/污染/过度捕捞）会"
     "打破平衡；「绿水青山就是金山银山」。生物圈 2 号实验失败证明：人工生态远不"
     "及自然生物圈可靠。",
     ["生物圈的范围包括哪些", "最大的生态系统是什么", "生态系统的组成成分",
      "生产者消费者分解者", "能量沿食物链怎么流动", "生物圈2号是什么实验"],
     ["问食物链书写规则", "问碳循环"],
     "atomic", "",
     "生物圈=最大生态系统(大气圈底+水圈大部+岩石圈表面·厚约20km)；组成=生产者/消费者/分解者+非生物；能量沿食物链逐级递减(10-20%)；生物圈 2 号失败证自然无可替代。"),
    ("kp_card_charmake",
     "汉字的造字法：六书",
     "人文通识知识点内容（人话接口）", "语文",
     "传统「六书」造字与用字法，造字四法：①象形——描摹实物形状（日/月/山/水/"
     "人/木）；②指事——用抽象符号指示意义（上/下/本——木下加横指树根/末——木"
     "上加横指树梢）；③会意——组合两个字的意义（休=人+靠木/明=日+月/从=二人"
     "跟随/森=三木）；④形声——形旁表义+声旁表音（占汉字 80% 以上：河=水形可"
     "声/铜=金形同声/爸=父形巴声）。用字二法：转注、假借（借「自」表鼻子→自"
     "己）。演变：甲骨文→金文→小篆（秦统一文字）→隶书→楷书（隶变是古今文字分"
     "水岭）。会意与形声的区别：会意各部分都表义、形声有声旁——「休」「明」会"
     "意 vs「河」「爸」形声是典型考点。",
     ["汉字的造字方法有哪几种", "什么是象形字", "会意字和形声字的区别",
      "本末是什么造字法", "形声字占汉字的比例", "汉字演变的过程"],
     ["问偏旁部首系统", "问简繁字关系"],
     "atomic", "",
     "六书：象形(日月山)/指事(上下本末)/会意(休明从·全表义)/形声(河铜·80%+)/转注假借；演变=甲骨→金→小篆(秦统一)→隶(古今分水)→楷；会意 vs 形声=有无声旁。"),
]

QUESTIONS = [
    ("QB-377", "速度是表示什么的物理量", "物理学", "技术直答",
     ["运动快慢"], "通识拓展61"),
    ("QB-378", "回收废旧金属的意义", "化学", "技术直答",
     ["节约资源", "减少污染"], "通识拓展61"),
    ("QB-379", "生物圈的范围包括哪些", "生物学", "技术直答",
     ["大气圈底部", "水圈", "岩石圈"], "通识拓展61"),
    ("QB-380", "汉字的造字方法有哪几种", "语文", "技术直答",
     ["象形", "指事", "会意", "形声"], "通识拓展61"),
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
                               "level:L2", "status:verified", "batch:通识拓展61"],
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
    bank["version"] = "v1.53"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
