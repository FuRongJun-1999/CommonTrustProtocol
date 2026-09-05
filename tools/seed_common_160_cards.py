# -*- coding: utf-8 -*-
"""seed_common_160_cards.py · 通识拓展批次160知识卡+题库（幂等）

160：历史学-徐霞客/生活常识-空调26度/数学-数字黑洞（趣味数学）
KCCS 四要素+题干原句触发词。三重预检：徐霞客/空调温度/数字黑洞均双库零覆盖
（树叶变色命中 autumnleaf 卡弃选）。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_xuxiake",
     "徐霞客与《徐霞客游记》",
     "人文通识知识点内容（人话接口）", "历史学",
     "徐霞客（1587-1641，明代江苏江阴人，名弘祖）：伟大的旅行家、地理学家——"
     "22 岁起「**问奇于名山大川**」，34 年间足迹遍及今 **21 个省**（大半个中"
     "国），靠双腿+雇佣向导，历尽艰险（三次遭盗、绝粮仍坚持——「**达人所之未"
     "达，探人所之未探**」）。每日坚持写考察日记，后人整理为《**徐霞客游记**"
     "》（约 60 万字）：①对**喀斯特地貌（岩溶）**的考察记录**比欧洲人早一百多"
     "年**、系统描述峰林溶洞成因（与喀斯特卡联动——桂林七星岩曾亲自入洞考察"
     "）；②纠正「岷山导江」旧说，**考证金沙江是长江正源**；③记录地热蒸汽现"
     "象（腾冲火山）；④文笔优美，亦是文学名作。**5 月 19 日**（《游记》开篇「"
     "癸丑之三月晦」对应的现代日期）被定为「**中国旅游日**」。",
     ["徐霞客是哪个朝代的", "徐霞客游记写了什么", "中国旅游日为什么是5月19日",
      "谁第一个考察喀斯特", "长江正源考证", "达人所之未达"],
     ["问郑和下西洋（用郑和卡）", "问徐霞客线路攻略"],
     "atomic", "",
     "徐霞客(1587-1641 明·江阴)：34 年足迹 21 省「达人所之未达」；《徐霞客游记》60 万字——喀斯特考察比欧洲早百余年+考证金沙江为长江正源；游记开篇日 5.19=中国旅游日。"),
    ("kp_card_ac26",
     "空调温度与「空调病」",
     "生活常识知识点内容（人话接口）", "生活常识",
     "温度设定：夏季**26°C 左右**最宜（国家公共建筑节能标准亦推荐）——每调高"
     "1°C 约省电 **6-8%**；室内外温差最好 ≤8°C（温差过大血管急缩急张→头痛鼻"
     "塞乏力=「**空调病**」本质是干燥+温差+空气不流通的综合不适，不是「冻"
     "病」）。健康细节：①风口**勿对人直吹**（尤其头颈睡眠时——面瘫/落枕风"
     "险）；②长时间开空调放盆水/加湿器（湿度 40-60% 宜）+**每 2-3 小时开窗换"
     "气**；③大汗淋漓别立刻冲进冷房（毛孔骤闭+血管急缩）；④冬季制热 **20°C**"
     "为宜（每低 2°C 也省电不少）。省电技巧：睡眠模式（夜间自动升 1-2°C）+配"
     "合电扇（体感-2~3°C）+短时外出不必关机（频繁启动更耗电，>半小时再关）+"
     "定期洗滤网（脏堵多耗 15% 电——与家电保养卡联动）。",
     ["空调开多少度最合适", "空调病是什么", "空调调高1度省多少电",
      "空调直吹有什么危害", "空调怎么用省电", "睡眠模式"],
     ["问空调滤网清洗（用家电保养卡）", "问空调选购参数"],
     "atomic", "",
     "空调=夏 26°C(调高 1°C 省电 6-8%)冬 20°C；温差 ≤8°C 防「空调病」(干燥+温差+不流通)；风口勿直吹头颈+2-3h 换气+湿度 40-60%；省电=睡眠模式+配风扇+短外出不关机+滤网清洁。"),
    ("kp_card_blackhole6174",
     "数字黑洞（趣味数学）",
     "基础科学知识点内容（人话接口）", "数学",
     "数字黑洞=无论从什么数出发，按固定规则迭代**最终必落入同一个数**（像黑洞"
     "吸积一切）。**经典例：6174 卡普雷卡尔黑洞**——任取四位数字**不全相同**"
     "的数（如 5298），把数字从大到小排列（9852）减去从小到大排列（2589），对"
     "差重复操作：9852-2589=7263→7632-2367=5265→6552-2556=3996→9963-3699="
     "6264→6642-2466=4176→7641-1467=**6174**→7641-1467=6174（锁定）——**最多"
     "7 步必达 6174**；三位数版本则落入 **495**。**123 黑洞**（西绪福斯串）：数"
     "一个数中偶数个数、奇数个数、总位数，把三个数连写成新数再重复——最终必"
     "到 **123**（例：123456789→459→417→323→123）。**未解之谜：冰雹猜想（角"
     "谷猜想）**——任取正整数，奇数×3+1、偶数÷2，所有被试过的数最终都落回"
     "**1→4→2→1** 循环，但至今**无人能证明**对所有自然数成立（已验证到 2^68"
     " 以上）。趣味价值：简单规则+深刻原理=数学之美。",
     ["数字黑洞是什么", "6174怎么算", "卡普雷卡尔黑洞", "123黑洞",
      "冰雹猜想", "角谷猜想"],
     ["问哥德巴赫猜想", "问概率黑洞（用彩票卡）"],
     "atomic", "",
     "数字黑洞=固定规则迭代必落入同一数：四位 6174 卡普雷卡尔（大排-小排≤7 步必达）/三位 495/123 黑洞（偶数个+奇数个+位数迭代）；冰雹猜想 3n+1 落 1→4→2→1 已验证 2^68 但无人证明——简单规则藏深刻数学。"),
]

QUESTIONS = [
    ("QB-735", "徐霞客是哪个朝代的地理学家？「中国旅游日」和他有什么关系？", "历史学", "技术直答",
     ["明朝", "明代", "游记", "5月19日", "5.19"], "通识拓展160"),
    ("QB-736", "夏天空调开多少度最合适？每调高一度大约能省多少电？", "生活常识", "技术直答",
     ["26", "二十六", "6-8", "省电"], "通识拓展160"),
    ("QB-737", "任取一个四位数按「大排减小排」反复计算，最终都会落入哪个数字黑洞？", "数学", "技术直答",
     ["6174", "卡普雷卡尔"], "通识拓展160"),
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
                               "level:L2", "status:verified", "batch:通识拓展160"],
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
    bank["version"] = "v4.33"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
