# -*- coding: utf-8 -*-
"""seed_common_19_cards.py · 通识拓展批次19知识卡+题库（幂等）

19：数学-负数比较/历史-第二次世界大战/语文-唐诗与诗人/体育学-篮球规则
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_negative",
     "负数与数轴比较大小",
     "基础科学知识点内容（人话接口）", "数学",
     "负数是小于零的数，在数轴上位于原点左侧；数轴上的点越往右表示的数越大。"
     "负数比较大小：两个负数比较，绝对值大的反而小——如 -5 < -2（|−5|=5 > "
     "|−2|=2，所以 -5 更小）；正数都大于 0，负数都小于 0。生活中的负数：零下"
     "温度（-3℃ 比零下 5℃ 即 -5℃ 要暖和）、海拔低于海平面（死海水面约 -430"
     " 米）、收支赤字。",
     ["负数怎么比较大小", "-5和-2哪个大", "两个负数怎么比",
      "数轴上怎么比较数的大小", "生活中哪些地方用到负数", "零下3度和零下5度哪个冷"],
     ["问负数乘法法则", "问绝对值方程"],
     "atomic", "",
     "负数<0<正数；数轴右大左小；两负比大小=绝对值大的反而小（-5<-2）；实例=零下温度/海拔负值。"),
    ("kp_card_ww2",
     "第二次世界大战概况",
     "人文通识知识点内容（人话接口）", "历史",
     "第二次世界大战（1939-1945）：1939 年 9 月 1 日德国闪击波兰，英法对德宣"
     "战，全面爆发（亚洲战争策源更早——1931 年九一八事变、1937 年七七事变日"
     "本全面侵华）；1942-1943 年斯大林格勒战役是苏德战场转折点；1945 年 5 月 "
     "8 日德国无条件投降（欧洲胜利日），9 月 2 日日本签署投降书，大战结束。中"
     "苏美英等 26 国组成世界反法西斯同盟；中国战场是世界反法西斯战争的东方主"
     "战场。",
     ["第二次世界大战是哪一年全面爆发的", "二战什么时候结束", "二战的转折点战役",
      "德国什么时候投降", "日本签署投降书是哪天", "什么是世界反法西斯同盟"],
     ["问一战详情", "问具体战役经过"],
     "atomic", "",
     "二战：1939.9.1 德国闪击波兰全面爆发；转折=斯大林格勒；1945.5.8 德降/9.2 日签降；中国=东方主战场。"),
    ("kp_card_tangpoetry",
     "唐诗与著名诗人",
     "人文通识知识点内容（人话接口）", "语文",
     "唐诗代表诗人：「床前明月光，疑是地上霜」出自李白《静夜思》——李白被称"
     "为「诗仙」，风格豪放飘逸，是浪漫主义代表；「诗圣」杜甫风格沉郁顿挫，现"
     "实主义代表，《春望》「国破山河在」写安史之乱，另有「三吏」「三别」；白"
     "居易诗风平易近人，《赋得古原草送别》「野火烧不尽」；王维善山水田园诗，"
     "被称为「诗佛」；合称「李杜」的即李白与杜甫。初唐四杰：王勃、杨炯、卢照"
     "邻、骆宾王。",
     ["床前明月光的作者是谁", "诗仙是谁", "诗圣是谁", "静夜思的作者是",
      "国破山河在是谁写的", "李杜指哪两位诗人"],
     ["问宋词元曲", "问具体诗篇赏析"],
     "atomic", "",
     "床前明月光=李白《静夜思》；诗仙=李白(浪漫)/诗圣=杜甫(现实)/诗佛=王维；李杜=李白+杜甫。"),
    ("kp_card_basketball",
     "篮球比赛基本规则",
     "人文通识知识点内容（人话接口）", "体育学",
     "篮球基本规则：每队同时上场 5 名队员；正式比赛分 4 节（NBA 每节 12 分钟，"
     "国际篮联 FIBA 每节 10 分钟）；得分——三分线外投中得 3 分、线内投中得 "
     "2 分、罚球得 1 分；主要违例：走步（持球移动超两步未运球）、二次运球（停"
     "球后再运）、24 秒进攻时限（一次进攻须 24 秒内出手）、回场；主要犯规：打"
     "手/推人/阻挡等，全队累计犯规达一定次数后对方获罚球。",
     ["篮球比赛每队上场几名队员", "篮球一场比赛打几节", "三分线外投中得几分",
      "什么是走步违例", "篮球的24秒规则", "罚球一次得几分"],
     ["问战术配合", "问足球排球规则"],
     "atomic", "",
     "篮球=每队5人上场/4节制(NBA12min·FIBA10min)；得分=三分线外3分线内2分罚球1分；违例=走步/二次运球/24秒。"),
]

QUESTIONS = [
    ("QB-209", "负数怎么比较大小", "数学", "技术直答",
     ["绝对值", "数轴"], "通识拓展19"),
    ("QB-210", "第二次世界大战是哪一年全面爆发的", "历史", "技术直答",
     ["1939", "波兰"], "通识拓展19"),
    ("QB-211", "床前明月光的作者是谁", "语文", "技术直答",
     ["李白", "静夜思"], "通识拓展19"),
    ("QB-212", "篮球比赛每队上场几名队员", "体育学", "技术直答",
     ["5名", "五名"], "通识拓展19"),
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
                               "level:L2", "status:verified", "batch:通识拓展19"],
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
    bank["version"] = "v1.11"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
