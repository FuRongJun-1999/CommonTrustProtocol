# -*- coding: utf-8 -*-
"""seed_common_33_cards.py · 通识拓展批次33知识卡+题库（幂等）

33：生物学-维生素/地理学-世界高原之最/历史-卧薪尝胆/数学-分数与小数互化
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_vitamins",
     "主要维生素与缺乏症",
     "基础科学知识点内容（人话接口）", "生物学",
     "维生素是人体必需的微量有机物，多数不能自身合成、须从食物摄取。经典对应"
     "关系：维生素 A 缺乏→夜盲症（暗处看不清，动物肝脏/胡萝卜素补充）；维生素 "
     "B1 缺乏→脚气病（粗粮豆类富含；注意不是真菌感染的「脚气/足癣」）；维生素 "
     "C 缺乏→坏血病（牙龈出血，新鲜蔬果补充——古代远航水手的噩梦）；维生素 D "
     "缺乏→儿童佝偻病/成人骨质疏松（晒太阳自身可合成）；维生素 K 与凝血相关。"
     "水溶性维生素（B 族/C）多余部分随尿排出、需每日补充；脂溶性（A/D/E/K）可"
     "在体内储存、过量反而中毒。",
     ["缺乏维生素C会得什么病", "缺乏维生素A会得什么病", "夜盲症缺什么维生素",
      "晒太阳合成什么维生素", "脚气病和脚气是一回事吗", "什么是水溶性维生素"],
     ["问具体剂量推荐", "问维生素药品选择"],
     "atomic", "",
     "维A缺→夜盲；B1缺→脚气病(≠足癣)；C缺→坏血病(牙龈出血)；D缺→佝偻/骨质疏松(晒太阳合成)；B族C水溶·ADEK脂溶可蓄积。"),
    ("kp_card_brazilplateau",
     "世界高原之最",
     "人文通识知识点内容（人话接口）", "地理学",
     "世界面积最大的高原是巴西高原（南美洲，约 500 多万平方公里，占据巴西国土"
     "大半）；世界海拔最高的高原是青藏高原（亚洲，平均海拔 4000 米以上，被称为"
     "「世界屋脊」「第三极」）——「最大」与「最高」是常考辨析点。其他高原之最："
     "黄土高原是世界最大的黄土沉积区（水土流失严重、沟壑纵横）；云贵高原地形崎"
     "岖、喀斯特地貌典型（溶洞/石林）；内蒙古高原地势平坦开阔。高原气候总体特点"
     "：气温随海拔升高而降低（每升 1000 米约降 6℃），青藏高原因此雪山连绵。",
     ["世界最大的高原是哪个", "世界最高的高原是哪个", "世界屋脊指哪个高原",
      "黄土高原的特点", "海拔每升高1000米气温降多少", "云贵高原什么地貌典型"],
     ["问高原反应原理", "问各高原经济特产"],
     "atomic", "",
     "高原之最：最大=巴西高原(500万km²)；最高=青藏高原(4000m+·世界屋脊)；最大黄土区=黄土高原；气温每升1000m降约6℃。"),
    ("kp_card_goujian",
     "卧薪尝胆：勾践复国",
     "人文通识知识点内容（人话接口）", "历史",
     "卧薪尝胆说的是春秋末期越王勾践：吴越争霸中越国兵败会稽，勾践向吴王夫差"
     "称臣为奴三年；归国后他睡柴草、尝苦胆，时刻提醒自己不忘亡国之耻（「汝忘"
     "会稽之耻邪？」），同时任用范蠡、文种发展生产训练军队，采用文种之计示弱"
     "麻痹吴国（进献西施、借粮还种）；十年生聚十年教训，终于趁夫差北上会盟、"
     "国力空虚之际伐吴，前 473 年灭吴，夫差自刎——勾践成为春秋最后一位霸主。"
     "成语寓意：忍辱负重、发愤图强。「兔死狗烹」也出自这段历史（灭吴后范蠡急"
     "流勇退，警告文种「飞鸟尽，良弓藏」）。",
     ["卧薪尝胆说的是谁", "勾践灭的是哪个国家", "范蠡文种是谁的谋臣",
      "会稽之耻指什么", "十年生聚十年教训什么意思", "兔死狗烹出自哪里"],
     ["问西施结局传说", "问春秋霸主完整名单"],
     "atomic", "",
     "卧薪尝胆=越王勾践：败于吴王夫差→称臣三年→归国励精图治十年→前473灭吴称霸；谋臣范蠡文种；典出「飞鸟尽良弓藏」。"),
    ("kp_card_fractiondecimal",
     "分数与小数互化",
     "基础科学知识点内容（人话接口）", "数学",
     "分数与小数可以互化：小数化分数——一位小数是十分之几（0.5=5/10=1/2），两"
     "位小数是百分之几（0.25=25/100=1/4），写成分数后约分成最简分数（0.75=75/"
     "100=3/4）。分数化小数——用分子除以分母（3/4=3÷4=0.75；1/8=0.125）。关键"
     "判别：最简分数的分母只含质因数 2 和 5 时能化成有限小数（1/4、3/8、7/20 "
     "都可以），分母含其他质因数（如 3、7）则化成无限循环小数（1/3=0.333…，"
     "1/7=0.142857 循环）。比较大小先统一形式：0.8 与 4/5 相等（4/5=0.8）。",
     ["0.5等于几分之几", "小数怎么化成分数", "分数怎么化成小数",
      "什么分数能化成有限小数", "0.75等于几分之几", "三分之一等于0.3循环对吗"],
     ["问循环小数记法", "问百分数三者互化"],
     "atomic", "",
     "互化：0.5=1/2·0.25=1/4(约分)；分数化小数=分子÷分母；分母只含质因数2和5→有限小数，含3等→无限循环(1/3=0.3循环)。"),
]

QUESTIONS = [
    ("QB-265", "缺乏维生素C会得什么病", "生物学", "技术直答",
     ["坏血病"], "通识拓展33"),
    ("QB-266", "世界最大的高原是哪个", "地理学", "技术直答",
     ["巴西高原"], "通识拓展33"),
    ("QB-267", "卧薪尝胆说的是谁", "历史", "技术直答",
     ["勾践"], "通识拓展33"),
    ("QB-268", "0.5等于几分之几", "数学", "技术直答",
     ["1/2", "二分之一"], "通识拓展33"),
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
                               "level:L2", "status:verified", "batch:通识拓展33"],
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
    bank["version"] = "v1.25"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
