# -*- coding: utf-8 -*-
"""seed_common_31_cards.py · 通识拓展批次31知识卡+题库（幂等）

31：物理学-巨轮浮沉（浮力深化）/生活常识-食品干燥剂/历史-文成公主入藏/音乐-中国国歌
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_shipfloat",
     "万吨巨轮为什么能浮在水面",
     "基础科学知识点内容（人话接口）", "物理学",
     "阿基米德原理：物体在水中受到的浮力等于它排开的水的重量。钢铁密度比水大，"
     "实心铁块会沉；但轮船做成空心——巨大的船体排开大量的水，浮力大到等于整船"
     "重力，就能漂浮。判断沉浮看平均密度：船体+货物的总重除以船的总体积小于水"
     "的密度即漂浮；超载会让平均密度逼近甚至超过水，吃水线（载重线）就是安全警"
     "戒。同一原理：密度计漂浮测密度、热气球浮在空气（排开空气的重量=浮力）。",
     ["轮船为什么能浮在水面上", "钢铁做的船为什么不沉", "什么是阿基米德原理",
      "吃水线是干什么用的", "船超载为什么会沉", "热气球为什么能升空"],
     ["问潜水艇沉浮原理", "问浮力计算题"],
     "atomic", "",
     "巨轮漂浮=空心增大排水量→浮力=重力(阿基米德)；平均密度<水即浮；吃水线=超载警戒；热气球=排开空气的浮力。"),
    ("kp_card_dryagent",
     "食品袋里的干燥剂",
     "生活常识知识点内容（人话接口）", "生活常识",
     "食品干燥剂的作用是吸收包装内的水汽，防止食物受潮变软、发霉变质。常见两"
     "类：①生石灰干燥剂（白色块状，氧化钙，吸水后变成熟石灰氢氧化钙）——吸水"
     "强但有强碱性腐蚀性，切勿拆开玩弄、误食或入眼（入眼立即用清水冲洗并就医）；"
     "②硅胶干燥剂（透明或彩色小颗粒，物理多孔吸附）——相对安全，常带变色指示"
     "（吸湿后由蓝变粉/由橙变绿）。咖啡饼、海苔、药品里的「勿食」小包多为干燥"
     "剂或脱氧剂（铁粉氧化耗氧，黑色颗粒、吸水会发热）。",
     ["食品袋里的干燥剂是什么", "生石灰干燥剂能碰吗", "硅胶干燥剂有毒吗",
      "误食干燥剂怎么办", "脱氧剂和干燥剂的区别", "干燥剂吸水后变成什么"],
     ["问真空包装原理", "问食品防腐剂种类"],
     "atomic", "",
     "干燥剂防潮：生石灰(CaO→Ca(OH)₂·强碱勿近眼口)/硅胶(多孔物理吸附·变色指示)；脱氧剂=铁粉氧化耗氧会发热。"),
    ("kp_card_wencheng",
     "文成公主入藏",
     "人文通识知识点内容（人话接口）", "历史",
     "文成公主入藏：唐太宗贞观年间（641 年），宗室女文成公主远嫁吐蕃赞普（君主）"
     "松赞干布，史称唐蕃和亲。她带去谷物种子、纺织/医药/历法等工匠与技术典籍，"
     "促进吐蕃经济文化发展；松赞干布为她修建宫室（布达拉宫的前身），今拉萨大昭"
     "寺供奉的释迦牟尼十二岁等身像相传即文成公主带入。和亲奠定了汉藏密切交往的"
     "基础，「和同为一家」；后来金城公主再嫁赤德祖赞，唐蕃「甥舅会盟碑」（拉萨）"
     "见证长期友好。藏戏《文成公主》与「唐卡」中多有此题材。",
     ["文成公主嫁给了谁", "文成公主入藏是哪个皇帝时期", "松赞干布是哪个民族的领袖",
      "布达拉宫和文成公主的关系", "唐蕃和亲的意义", "甥舅会盟碑在哪里"],
     ["问吐蕃历史细节", "问金城公主事迹"],
     "atomic", "",
     "文成公主 641 年嫁吐蕃松赞干布（唐太宗时）：带工匠种子典籍入藏；布达拉宫前身为其建；汉藏「和同为一家」。"),
    ("kp_card_nationalanthem",
     "中国国歌《义勇军进行曲》",
     "人文通识知识点内容（人话接口）", "音乐",
     "中国国歌是《义勇军进行曲》：田汉作词、聂耳作曲，诞生于 1935 年——原为电"
     "影《风云儿女》的主题歌，在抗日战争中传遍全国，激励军民救亡。1949 年 9 月"
     "中国人民政治协商会议第一届全体会议决定以其为代国歌，2004 年写入宪法正式"
     "确定为中华人民共和国国歌；2017 年《国歌法》施行，规定奏唱场合与礼仪（肃"
     "立、庄重，不得用于商标广告等）。作曲家聂耳另有《毕业歌》《卖报歌》；田汉"
     "是话剧《关汉卿》作者、中国戏剧奠基人之一。",
     ["中国国歌的词曲作者是谁", "义勇军进行曲诞生于哪一年", "国歌是哪部电影的主题歌",
      "国歌哪一年写入宪法", "国歌法是哪年实施的", "聂耳的作品有哪些"],
     ["问其他抗战歌曲", "问国旗国徽设计者"],
     "atomic", "",
     "国歌=《义勇军进行曲》：田汉词·聂耳曲·1935《风云儿女》主题歌；2004 入宪·2017 国歌法；奏唱须肃立庄重。"),
]

QUESTIONS = [
    ("QB-257", "轮船为什么能浮在水面上", "物理学", "技术直答",
     ["浮力", "排水量"], "通识拓展31"),
    ("QB-258", "食品袋里的干燥剂是什么", "生活常识", "技术直答",
     ["生石灰", "硅胶"], "通识拓展31"),
    ("QB-259", "文成公主嫁给了谁", "历史", "技术直答",
     ["松赞干布"], "通识拓展31"),
    ("QB-260", "中国国歌的词曲作者是谁", "音乐", "技术直答",
     ["田汉", "聂耳"], "通识拓展31"),
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
                               "level:L2", "status:verified", "batch:通识拓展31"],
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
    bank["version"] = "v1.23"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
