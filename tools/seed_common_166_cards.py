# -*- coding: utf-8 -*-
"""seed_common_166_cards.py · 通识拓展批次166知识卡+题库（幂等·两卡精批次）

166：化学-啤酒瓶为什么是棕色的/生活常识-冰箱储存的误区
KCCS 四要素+题干原句触发词。三重预检：啤酒瓶颜色（发酵卡仅列举「啤酒」
词）与冰箱储存误区双库主题未覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_beerbottle",
     "啤酒瓶为什么是棕色或绿色的",
     "基础科学知识点内容（人话接口）", "化学",
     "啤酒「怕光」：啤酒花中的**异 α 酸**（苦味来源）在**紫外线**照射下发生"
     "光化学反应，生成微量 **3-甲基-2-丁烯-1-硫醇**——和臭鼬喷雾同类的含硫"
     "物质，产生「**日光臭**」（又称「臭鼬味」，几小时暴晒即可产生且不可逆）。"
     "**瓶色=滤光策略**：①**棕色瓶**——滤除紫外线效果最好，是最优解；②**绿"
     "色瓶**——滤一部分紫外线，效果中等（欧洲传统工艺加「反异构化酒花」抗光"
     "苦味物质来补偿）；③**透明瓶**——最差，必须全程避光保存或用抗光酒花。"
     "所以「绿瓶是低档」是误解——是抗光工艺路线不同。日常生活同理：橄榄油（"
     "光氧化酸败）也用深色瓶；牛奶过去用透明玻璃袋装易产生「日晒味」——现利"
     "乐包避光。结论：啤酒买回来**放阴凉避光处**，别放窗台。",
     ["啤酒瓶为什么是棕色的", "啤酒为什么会日光臭", "绿瓶和棕瓶啤酒的区别",
      "啤酒为什么要避光", "臭鼬味啤酒"],
     ["问啤酒酿造工艺", "问玻璃着色原理"],
     "atomic", "",
     "啤酒瓶棕/绿=防光化学臭味：UV 使酒花异 α 酸光解生成含硫「日光臭」（臭鼬味不可逆）；棕瓶滤 UV 最优>绿瓶>透明（需抗光酒花或避光）；绿瓶低档是误解；橄榄油深色瓶同理——啤酒放阴凉避光处。"),
    ("kp_card_fridgestore",
     "冰箱储存的误区",
     "生活常识知识点内容（人话接口）", "生活常识",
     "「冰箱不是保险箱」——4°C 只能**减缓**细菌繁殖（李斯特菌等嗜冷菌照长）"
     "不杀菌。**不适合放冰箱的**：①热带水果（香蕉/芒果/荔枝）——低温**冻伤**"
     "发黑变质更快，阴凉处放；②土豆红薯——低温把淀粉**转成糖**（口感发甜+"
     "油炸时更易产生丙烯酰胺），阴凉避光即可；③蜂蜜——会结晶（虽不影响品质"
     "但口感差）且吸潮发酵，密封阴凉放；④番茄——低温破坏风味酶，「没小时候"
     "味」的一部分原因；⑤洋葱大蒜——潮湿环境反易发霉。**正确姿势**：生熟分"
     "层（熟上生下防滴漏交叉污染）、剩菜覆膜 24 小时内吃完且**吃前彻底热透"
     "**、冰箱每月擦洗、温度冷藏 4°C 冷冻 -18°C。方向对了再谈保鲜。",
     ["哪些食物不能放冰箱", "香蕉芒果要冷藏吗", "蜂蜜要不要放冰箱",
      "土豆放冰箱发芽吗", "冰箱温度多少合适", "剩菜能放几天"],
     ["问食品标签（用食品标签卡）", "问冰箱除味方法"],
     "atomic", "",
     "冰箱 4°C 只减缓细菌不杀菌（李斯特菌照长）；不宜冷藏=热带水果冻伤/土豆红薯转糖/蜂蜜结晶吸潮/番茄失风味/洋葱大蒜发霉；正确=生熟分层熟上生下+剩菜 24h 内热透+冷藏 4°C 冷冻 -18°C+每月擦洗。"),
]

QUESTIONS = [
    ("QB-753", "啤酒瓶为什么大多是棕色或绿色的？「日光臭」是怎么产生的？", "化学", "技术直答",
     ["紫外线", "UV", "光化学", "日光臭", "避光", "酒花"], "通识拓展166"),
    ("QB-754", "哪些食物不适合放冰箱储存？为什么说冰箱不是「保险箱」？", "生活常识", "技术直答",
     ["热带水果", "香蕉", "土豆", "蜂蜜", "减缓", "李斯特"], "通识拓展166"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{6,}", content):
            problems.append((node[0], f"长英文词: {word}"))
    if problems:
        raise SystemExit(f"外文长词检测报警: {problems}")


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
                               "level:L2", "status:verified", "batch:通识拓展166"],
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
    bank["version"] = "v4.39"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
