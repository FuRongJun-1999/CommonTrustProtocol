# -*- coding: utf-8 -*-
"""seed_common_427_cards.py · 通识拓展批次427知识卡+题库（幂等）

427：3 张新卡·著名定律效应三连（墨菲定律 kp_card_murphy /
    蝴蝶效应 kp_card_butterflyfx / 二八定律 kp_card_pareto）。
KCCS 四要素+题干原句触发词。预检已过（QB-1519~1521 可用，
三主题题库 0 覆盖、卡库无同名卡）。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

WHITELIST = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
             "effect", "OR6A2", "ghrelin", "DOMS", "DHT", "frisson",
             "AlphaGo", "CFOP", "Transformer", "LLM", "GPT", "BERT",
             "CYP3A4", "ACID", "CNN", "RNN", "LSTM", "Krebs", "NADH",
             "FADH2", "Vmax", "Km", "RNA", "DNA", "mRNA", "KCL", "KVL",
             "BCS", "B2H6", "borrow", "Rust", "sin", "cos", "tan",
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO", "SVM",
             "MTBF", "SQA", "IMC", "HMO", "JD", "STAR", "Word", "offer",
             "XMind"}


def foreign_word_check(text: str) -> list:
    """西里尔字符一律报警；长英文词(≥4)非白名单报警。只扫中文内容字段。"""
    bad = []
    if re.search(r"[\u0400-\u04FF]", text):
        bad.append("cyrillic:" + re.search(r"[\u0400-\u04FF]+", text).group())
    for w in re.findall(r"[A-Za-z]{4,}", text):
        if w not in WHITELIST:
            bad.append("latin:" + w)
    return bad


NODES = [
    ("kp_card_murphy",
     "墨菲定律",
     "思维定律知识点内容（人话接口）", "思维方法",
     "墨菲定律——「只要有可能出错，就一定会出错」：①**来源**——1949 年"
     "美国空军工程师爱德华·墨菲在火箭滑车实验中，发现仪器竟被安装成"
     "「恰好装反也能装上」的方式，由此总结出这句名言；②**本质**——"
     "不是悲观宿命论，而是概率思维：只要样本够多、时间够长，概率再小"
     "的坏事也必然发生；③**工程启示**——关键系统必须做**冗余与防呆**"
     "设计：备份电源、双卡双待、检查清单（航空业的起飞检查单就是"
     "对抗墨菲定律的经典手段）；④**生活应用**——出门前「伸手要钱」"
     "口诀（身份证/手机/钥匙/钱包）、重要文件多备份、赶时间的日子"
     "更要提前出门；⑤**辨析**——「怕什么来什么」部分是心理效应："
     "坏事发生了印象深（幸存者偏差式记忆），不代表墨菲定律「显灵」。",
     ["墨菲定律是什么", "墨菲定律的由来", "为什么怕什么来什么",
      "墨菲定律怎么应对", "冗余设计", "防呆设计"],
     ["问幸存者偏差", "问安全检查清单"],
     "atomic", "",
     "墨菲定律=只要有可能出错就一定会出错+1949爱德华墨菲火箭滑车实验"
     "仪器装反总结+本质概率思维时间够长小概率坏事必发生+工程启示冗余"
     "防呆设计备份检查清单航空起飞单+生活口诀伸手要钱多备份提前出门+"
     "怕什么来什么是记忆偏差不是显灵。"),
    ("kp_card_butterflyfx",
     "蝴蝶效应",
     "思维定律知识点内容（人话接口）", "思维方法",
     "蝴蝶效应——「巴西的蝴蝶扇动翅膀，可能在德州引起一场龙卷风」："
     "①**来源**——气象学家洛伦兹 1963 年用计算机模拟天气时发现：初始"
     "数据的小数点后微小改动，一段时间后的天气模拟结果天差地别；②**"
     "本质**——混沌系统的「对初始条件敏感依赖」：初始的微小差异经过"
     "非线性过程不断放大，最终结果大相径庭；③**启示一（预测）**——"
     "天气、股市等复杂系统难以长期精确预测（差之毫厘，谬以千里）；"
     "④**启示二（行动）**——小事不可轻视：好习惯、小改进会复利式放大"
     "（每天进步 1%，一年约 37 倍）；坏的开端也会滚雪球（防微杜渐）；"
     "⑤**辨析**——蝴蝶效应≠「蝴蝶引起龙卷风」的因果断言，而是敏感"
     "依赖性的形象比喻。",
     ["蝴蝶效应是什么", "蝴蝶效应的由来", "洛伦兹",
      "混沌理论", "差之毫厘谬以千里", "蝴蝶效应的启示"],
     ["问混沌系统", "问墨菲定律"],
     "atomic", "",
     "蝴蝶效应=巴西蝴蝶扇翅德州龙卷风比喻+洛伦兹1963计算机模拟天气初"
     "值微改结果天差地别+本质混沌系统对初始条件敏感依赖非线性放大+启"
     "示复杂系统难长期精确预测+小事不可轻视好习惯复利放大防微杜渐+"
     "比喻敏感依赖非因果断言。"),
    ("kp_card_pareto",
     "二八定律",
     "思维定律知识点内容（人话接口）", "思维方法",
     "二八定律（帕累托法则）——「关键的少数，次要的多数」：①**来源**"
     "——意大利经济学家帕累托 1897 年观察到：约 80% 的土地掌握在 20%"
     "的人口手中；后来管理学家朱兰把它推广为普遍规律；②**表述**——"
     "在很多系统中，约 80% 的结果来自 20% 的关键因素（公司 80% 利润"
     "常来自 20% 客户、APP 80% 使用时长集中在 20% 功能）；③**应用**"
     "——时间管理：找出产出最大的 20% 核心任务优先做；库存与客服："
     "优先解决投诉最多的 20% 问题；④**注意**——80/20 是象征性数字"
     "（实际可能是 70/30 或 90/10），核心是「结果分布不均匀」这个洞见；"
     "⑤**边界**——并非处处成立：安全、健康等领域小概率事件也可能"
     "致命（「墨菲定律」式的场景不能只抓 20%）。",
     ["二八定律是什么", "帕累托法则", "80/20法则",
      "二八定律的应用", "关键的少数", "二八定律的局限"],
     ["问时间管理", "问马太效应"],
     "atomic", "",
     "二八定律=帕累托法则关键的少数次要的多数+1897帕累托80%土地20%人"
     "口朱兰推广普遍化+约80%结果来自20%关键因素利润客户功能+应用时间"
     "管理抓核心20%任务优先+数字象征核心是分布不均匀+安全健康领域不"
     "适用小概率也致命。"),
]

QUESTIONS = [
    ("QB-1519", "墨菲定律是什么？它对我们做事有什么提醒？",
     "思维方法", "技术直答",
     ["墨菲定律", "出错", "概率", "防范"], "通识拓展427"),
    ("QB-1520", "什么是蝴蝶效应？它说明了什么道理？",
     "思维方法", "技术直答",
     ["蝴蝶效应", "洛伦兹", "混沌", "初始条件"], "通识拓展427"),
    ("QB-1521", "什么是二八定律？它在时间管理中怎么应用？",
     "思维方法", "技术直答",
     ["二八定律", "帕累托", "关键少数", "应用"], "通识拓展427"),
]


def ensure_seed() -> dict:
    for nid, *_ in NODES:
        conn = sqlite3.connect(DB)
        row = conn.execute("SELECT id FROM nodes WHERE id=?", (nid,)).fetchone()
        conn.close()
        assert not row, f"id 撞车：{nid} 已存在"
    bank = json.load(open(BANK, encoding="utf-8"))
    have = {q["id"] for q in bank["questions"]}
    for qid, *_ in QUESTIONS:
        assert qid not in have, f"QB 撞车：{qid} 已存在"

    all_text = ""
    for n in NODES:
        all_text += n[1] + " " + n[4] + " " + " ".join(n[5]) + " " \
            + " ".join(n[6]) + " " + n[9] + " "
    for q in QUESTIONS:
        all_text += q[1] + " " + " ".join(q[4]) + " "
    bad = foreign_word_check(all_text)
    assert not bad, f"外文词混入：{bad}"

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
                               "level:L2", "status:verified", "batch:通识拓展427"],
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

    qs = bank["questions"]
    added = 0
    for qid, question, domain, qtype, keywords, source in QUESTIONS:
        if qid in have:
            continue
        qs.append({"id": qid, "question": question, "domain": domain,
                   "type": qtype, "keywords": keywords, "source": source,
                   "added": "2026-09-07"})
        added += 1
    bank["version"] = "v6.98"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
