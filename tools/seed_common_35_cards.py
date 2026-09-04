# -*- coding: utf-8 -*-
"""seed_common_35_cards.py · 通识拓展批次35知识卡+题库（幂等）

35：化学-实验室制氧气/地理学-世界最大岛屿/历史-玄奘西行/艺术-卢浮宫三宝
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_o2lab",
     "实验室制取氧气",
     "基础科学知识点内容（人话接口）", "化学",
     "实验室制氧气常用三法：①分解过氧化氢溶液（双氧水 H₂O₂），加二氧化锰作催"
     "化剂——常温进行、最快最安全，是首选；②加热高锰酸钾（KMnO₄，暗紫色固"
     "体），试管口放一团棉花防止粉末进入导管；③加热氯酸钾（KClO₃）加二氧化锰"
     "催化。收集方法：排水法（氧气不易溶于水，较纯）或向上排空气法（氧气密度"
     "略大于空气）；验满：带火星的木条伸入瓶口复燃即满。工业上则用分离液态空"
     "气法（氮气先蒸发）。三个反应都是分解反应（一变多）——催化剂「一变二不"
     "变」：改变化学速率、自身质量和化学性质不变。",
     ["实验室用什么制取氧气", "实验室制氧气为什么要放棉花", "二氧化锰在制氧气中的作用",
      "氧气怎么收集和验满", "工业上怎么制氧气", "什么是分解反应"],
     ["问催化剂工业应用", "问氧气性质检验"],
     "atomic", "",
     "制氧三法：H₂O₂+MnO₂(常温首选)/加热KMnO₄(管口棉花)/加热KClO₃+MnO₂；收集=排水法(不易溶)；验满=带火星木条复燃；催化「一定二不变」。"),
    ("kp_card_greenland",
     "世界最大的岛屿：格陵兰",
     "人文通识知识点内容（人话接口）", "地理学",
     "世界最大的岛屿是格陵兰岛（Greenland）：位于北美洲东北部与欧洲之间，面积约"
     "216 万平方公里，是丹麦的自治领地——「岛」的定义：四面环水、涨潮时仍露出"
     "水面的陆地，且面积小于最小的大陆；澳大利亚（约 769 万平方公里）因被定为"
     "最小大陆而不算岛——「最大岛=格陵兰 vs 澳大利亚是大陆」是常考辨析。格陵"
     "兰约 80% 被冰盖覆盖（世界第二大冰盖，仅次于南极），冰盖若全部融化全球海平"
     "面将上升约 7 米；因纽特人（爱斯基摩人）世居于此，首府努克。名字由来：维京"
     "人埃里克为吸引移民而起的「绿色之地」营销。",
     ["世界最大的岛是哪个", "格陵兰岛属于哪个国家", "澳大利亚为什么不算是岛",
      "格陵兰岛有多少冰", "因纽特人住在哪里", "格陵兰名字的由来"],
     ["问冰盖融化与海平面", "问岛屿类型分类"],
     "atomic", "",
     "最大岛=格陵兰(216万km²·丹麦自治领·80%冰盖)；澳大利亚=最小大陆故不算岛；冰盖全融海平面升约7米。"),
    ("kp_card_xuanzang",
     "玄奘西行取经",
     "人文通识知识点内容（人话接口）", "历史",
     "玄奘（602-664）：唐代高僧，法相宗创始人，史称「三藏法师」。贞观元年（627"
     " 年）前后他从长安出发西行，穿越河西走廊、大沙漠（莫贺延碛八百里「上无飞"
     "鸟下无走兽」）、翻越凌山，历十七年、行程五万里、途经一百多个国家，到达"
     "天竺（古印度）那烂陀寺师从戒贤法师研习佛法；回国后主持翻译佛经 75 部 1335"
     " 卷，并口述《大唐西域记》——由弟子辩机撰写，记录沿途 138 国风土，是研究"
     "中亚与南亚古代历史地理的珍贵文献。注意：《西游记》是明代吴承恩以此事为原"
     "型的神魔小说——唐僧、悟空、八戒、沙僧是艺术虚构，历史上玄奘是孤身偷渡出"
     "关（未获批准出行）的坚毅学者。",
     ["玄奘去哪里取经", "玄奘西行用了多少年", "大唐西域记是谁写的",
      "西游记和玄奘的关系", "那烂陀寺在哪里", "玄奘翻译了多少佛经"],
     ["问鉴真东渡对比", "问佛教东传路线"],
     "atomic", "",
     "玄奘：唐贞观年间孤身西行十七年五万里→天竺那烂陀寺；译经75部1335卷；口述《大唐西域记》(辩机撰)；《西游记》=明代小说化演绎。"),
    ("kp_card_venus",
     "卢浮宫三宝",
     "人文通识知识点内容（人话接口）", "艺术",
     "巴黎卢浮宫「三宝」：《蒙娜丽莎》（达·芬奇油画）、《断臂维纳斯》（又称米洛"
     "的维纳斯）与《胜利女神像（萨莫色雷斯的尼刻）》。断臂维纳斯是古希腊雕"
     "塑（约公元前 2 世纪，1820 年在希腊米洛岛出土），表现爱与美之神阿佛洛狄"
     "忒，残缺的双臂反而成就「残缺美」的经典；胜利女神像为纪念海战胜利而作，"
     "展翅立于船头形基座上，虽无头仍气势磅礴。卢浮宫原为法国王宫，1793 年改"
     "为博物馆，是世界参观人数最多的博物馆；玻璃金字塔入口由美籍华裔建筑师贝"
     "聿铭设计（1989）。",
     ["断臂维纳斯是什么时期的作品", "卢浮宫三宝是哪三件", "胜利女神像在哪里",
      "卢浮宫玻璃金字塔是谁设计的", "维纳斯的双臂去哪了", "米洛的维纳斯出土于哪里"],
     ["问古希腊雕塑其他名作", "问世界四大博物馆对比"],
     "atomic", "",
     "卢浮宫三宝=蒙娜丽莎+断臂维纳斯(古希腊·前2世纪·米洛岛出土)+胜利女神像；贝聿铭玻璃金字塔(1989)；1793 王宫改馆。"),
]

QUESTIONS = [
    ("QB-273", "实验室用什么制取氧气", "化学", "技术直答",
     ["高锰酸钾", "过氧化氢", "二氧化锰"], "通识拓展35"),
    ("QB-274", "世界最大的岛是哪个", "地理学", "技术直答",
     ["格陵兰"], "通识拓展35"),
    ("QB-275", "玄奘去哪里取经", "历史", "技术直答",
     ["天竺", "印度"], "通识拓展35"),
    ("QB-276", "断臂维纳斯是什么时期的作品", "艺术", "技术直答",
     ["古希腊"], "通识拓展35"),
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
                               "level:L2", "status:verified", "batch:通识拓展35"],
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
    bank["version"] = "v1.27"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
