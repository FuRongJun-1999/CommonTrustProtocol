# -*- coding: utf-8 -*-
"""seed_common_225_cards.py · 通识拓展批次225知识卡+题库（幂等·两卡精批次）

225：生物学-萤火虫为什么会发光/趣味遗传-为什么有人讨厌香菜
KCCS 四要素+题干原句触发词。三重预检：萤火虫（bionics 卡仅 LED 仿生一句
划界）与香菜基因双库零覆盖。执行前外文长词检测（OR6A2 加白名单）。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_fireflyglow",
     "萤火虫为什么会发光",
     "基础科学知识点内容（人话接口）", "生物学",
     "萤火虫发光=**生物冷光**：①**化学原理**——腹部发光器内的**荧光素**在**"
     "荧光素酶**催化下与氧气、ATP 反应，释放光子（能量几乎全部转化为光、几乎"
     "不发热——效率远超白炽灯的 10%，所以叫「冷光」，LED 的仿生目标之一）；"
     "②**为什么发光**——主要是**求偶信号**：不同种类有专属的闪烁频率与节律"
     "（像「光密码」），雌雄靠特定频率互相识别配对（频率不对不响应——防止杂"
     "交）；也有警戒天敌的作用；③**闪烁控制**——萤火虫通过**控制氧气进入发"
     "光器的通断**来「开关」灯；④**生态威胁**——光污染干扰求偶信号+栖息地破"
     "坏，萤火虫种群锐减，成为环境指示物种。",
     ["萤火虫为什么会发光", "萤火虫冷光", "荧光素荧光素酶",
      "萤火虫发光是求偶吗", "萤火虫为什么越来越少"],
     ["问LED仿生（用仿生卡）", "问其他生物发光（水母等）"],
     "atomic", "",
     "萤火虫发光=荧光素+荧光素酶+氧气+ATP 反应释放冷光（几乎无热，效率远超白炽灯）；主要=求偶信号（不同种类专属闪烁频率如光密码）；开关靠控制氧气通断；光污染干扰求偶+栖息地破坏=种群锐减环境指示物种。"),
    ("kp_card_cilantro",
     "为什么有人讨厌香菜",
     "基础科学知识点内容（人话接口）", "生物学",
     "讨厌香菜=**基因决定的嗅觉差异**，不是挑食：①香菜的特殊气味来自**醛类"
     "物质**；②**OR6A2 嗅觉受体基因**的变异让人对醛类**极度敏感**——闻到的"
     "是「肥皂味/臭虫味」（同样的醛类也是肥皂和臭虫的气味成分）；③**数据**——"
     "全球约 4-14% 的人讨厌香菜，**东亚比例更高**（研究提示相关基因变异频率"
     "更高）；twin 研究显示讨厌香菜约一半可由遗传解释；④**没有对错**——喜"
     "好由基因与成长环境共同塑造，互相尊重即可；「多吃就习惯」的机制是接触适应而非基因改变。"
     "适应而非基因改变。",
     ["为什么有人讨厌香菜", "香菜肥皂味", "香菜基因", "OR6A2",
      "讨厌香菜是挑食吗"],
     ["问狐臭基因（用狐臭卡）", "问味觉地图（用味觉卡）"],
     "atomic", "",
     "讨厌香菜=OR6A2 嗅觉受体基因变异对醛类极度敏感（闻到肥皂味/臭虫味——醛类同源）；全球 4-14% 讨厌、东亚比例更高；twin 研究约一半由遗传解释；没有对错互相尊重——多吃习惯是适应非基因改变。"),
]

QUESTIONS = [
    ("QB-874", "萤火虫为什么会发光？它的发光效率为什么比白炽灯高？", "生物学", "技术直答",
     ["荧光素", "荧光素酶", "冷光", "ATP", "求偶"], "通识拓展225"),
    ("QB-875", "为什么有人觉得香菜是「肥皂味」？这与基因有什么关系？", "生物学", "技术直答",
     ["OR6A2", "醛类", "基因", "嗅觉", "肥皂味"], "通识拓展225"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    whitelist = {"OR6A2"}
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{6,}", content):
            if word not in whitelist:
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
                               "level:L2", "status:verified", "batch:通识拓展225"],
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
                   "added": "2026-09-06"})
        added += 1
    bank["version"] = "v4.96"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
