# -*- coding: utf-8 -*-
"""seed_common_170_cards.py · 通识拓展批次170知识卡+题库（幂等）

170：生活常识-晨练还是晚练/生活常识-洗头的正确频率/数学-质数
KCCS 四要素+题干原句触发词。三重预检：锻炼老卡仅习惯一句话列举（运动时间科
学未覆盖）、洗头/质数双库零覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_exercisetime",
     "晨练还是晚练",
     "生活常识知识点内容（人话接口）", "生活常识",
     "运动时间各有讲究：①**清晨的风险**——清晨血液黏稠、血压处于晨峰（6-10 "
     "点心脑血管事件高发时段），**中老年人/高血压者不宜剧烈晨练**；日出前植物"
     "尚未光合作用，林间二氧化碳浓度反而高，雾天污染物颗粒也多——**等太阳出"
     "来后再练**；②**傍晚 4-6 点**——体温最高、肌肉关节最柔韧、反应最快，"
     "**运动表现的黄金时段**（受伤风险也低）；③**晚上运动**——睡前 3 小时结"
     "束即可（运动后神经兴奋影响入睡）；④**通用原则**——饭后 1-1.5 小时内勿"
     "剧烈运动；运动前热身 5-10 分钟；每周 **150 分钟中等强度**（快走/慢跑/"
     "游泳）+两次力量训练是健康基线；「什么时候能坚持」比「什么时间最优」更重"
     "要——选自己能长期执行的时间段。",
     ["早上锻炼好还是晚上好", "晨练要注意什么", "饭后多久可以运动",
      "每周运动多少时间", "运动黄金时间", "空腹晨跑好吗"],
     ["问运动损伤处理（用 RICE 卡）", "问增肌训练计划"],
     "atomic", "",
     "运动时间=晨间血液黏稠血压晨峰（老人心脑血管高风险，日出后再练）；傍晚 4-6 点体温柔韧最佳=黄金时段；晚上运动睡前 3h 结束；饭后 1-1.5h 勿剧烈；每周 150 分钟中等强度+两次力量——能坚持的时间就是好时间。"),
    ("kp_card_hairwash",
     "洗头的正确频率与方法",
     "生活常识知识点内容（人话接口）", "生活常识",
     "洗头频率看发质：①**油性头皮**——可每天或隔天洗（出油多不洗反堵塞毛囊"
     "加重脱发观感）；②**干性/中性**——**2-3 天一次**（过度清洁破坏皮脂膜越"
     "洗越干）；③水温 **38°C 左右温水**（过烫刺激头皮出更多油+伤毛鳞片）；④"
     "**方法**：洗发水先在掌心搓出泡沫再上头、用**指腹按摩**而非指甲抓挠（抓"
     "伤头皮致感染）、护发素只涂**中段到发梢**（涂头皮致油腻扁平）；⑤**湿发"
     "毛鳞片张开最脆弱**——勿用力毛巾搓、勿湿发梳头紧扎、**勿湿发入睡**（潮"
     "湿摩擦伤发+头皮滋生微生物）；⑥吹风机保持 15cm 距离、先热风后冷风定型。"
     "掉发常识：每天掉 50-100 根属正常代谢（休止期脱落），洗头掉的多数是「本"
     "来就要掉」的头发——不是洗头导致脱发。",
     ["几天洗一次头最好", "洗头水温多少度", "护发素涂哪里",
      "湿发可以睡觉吗", "洗头掉头发多正常吗", "指甲抓头皮"],
     ["问脱发治疗（就医）", "问吹风机功率选择"],
     "atomic", "",
     "洗头频率=油性可每天/干性 2-3 天；38°C 温水+掌心搓泡+指腹按摩不抓挠；护发素只涂中段发梢；湿发毛鳞片张开勿搓扎入睡；吹风 15cm 先热后冷；日掉 50-100 根正常——掉的多是本来要掉的。"),
    ("kp_card_primes",
     "质数",
     "基础科学知识点内容（人话接口）", "数学",
     "**质数（素数）**=大于 1、且只能被 1 和自身整除的自然数：2, 3, 5, 7, "
     "11, 13, 17, 19, 23……①**2 是唯一的偶质数**（其他偶数都能被 2 整除）；"
     "②质数有无穷多个——**欧几里得**早在两千多年前就用反证法优雅证明（《几何"
     "原本》）；③**埃拉托斯特尼筛法**——把 2 的倍数、3 的倍数……依次划掉，"
     "剩下的就是质数，是初等高效的找质数方法；④**质数定理**——质数在数轴上"
     "越往后越稀疏，但永远不消失；⑤**现代应用**——RSA 加密算法依赖「大质数"
     "相乘容易、分解极难」的不对称性，网上支付/银行加密的安全基石；⑥未解之"
     "谜：**哥德巴赫猜想**（任一大于 2 的偶数=两个质数之和，目前验证到 4×"
     "10¹⁸ 仍未证明）与黎曼猜想。",
     ["质数是什么", "最小的质数", "质数有多少个", "埃氏筛法",
      "质数在密码学中的应用", "哥德巴赫猜想"],
     ["问数字黑洞（用数字黑洞卡）", "问最大质数纪录"],
     "atomic", "",
     "质数=大于 1 仅被 1 和自身整除（2 是唯一偶质数）；无穷多个（欧几里得反证）+埃氏筛找法+越往后越稀疏（质数定理）；RSA 加密=大质数乘易分解难的基石；哥德巴赫猜想验证至 4×10¹⁸ 未证。"),
]

QUESTIONS = [
    ("QB-761", "为什么中老年人不宜在清晨剧烈锻炼？一天中什么时段运动表现最好？", "生活常识", "技术直答",
     ["晨峰", "血液黏稠", "血压", "傍晚", "4-6点", "热身"], "通识拓展170"),
    ("QB-762", "油性头皮几天洗一次头合适？湿头发为什么不能马上睡觉？", "生活常识", "技术直答",
     ["每天", "隔天", "毛鳞片", "38", "温水", "指腹"], "通识拓展170"),
    ("QB-763", "质数的定义是什么？哪一个质数是唯一的偶数质数？", "数学", "技术直答",
     ["1和自身", "整除", "2", "二", "偶"], "通识拓展170"),
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
                               "level:L2", "status:verified", "batch:通识拓展170"],
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
    bank["version"] = "v4.43"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
