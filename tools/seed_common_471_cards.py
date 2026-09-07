# -*- coding: utf-8 -*-
"""seed_common_471_cards.py · 通识拓展批次471知识卡+题库（幂等）

471：3 张新卡·饮食文化三连（筷子文化 kp_card_chopsticks /
    早餐的重要性 kp_card_breakfastimp / 食物相克辟谣 kp_card_foodcombo）。
预检已过（QB-1648~1650 可用，三主题题库卡库双零）。
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
             "XMind", "HDR", "Robotaxi"}


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
    ("kp_card_breakfastimp",
     "早餐的重要性",
     "健康常识知识点内容（人话接口）", "健康与身体",
     "早餐——唤醒身体的「第一餐」：①**为什么重要**——一夜空腹后血糖"
     "偏低，大脑主要靠葡萄糖供能，不吃早餐上午注意力、记忆力下降；②**"
     "长期危害**——饥一顿饱一顿易午餐暴食（增加肥胖风险）、胆汁浓缩"
     "堆积增加胆结石风险、影响胃酸规律伤胃；③**好早餐标准**——谷物"
     "（包子/燕麦/全麦面包）+蛋白质（鸡蛋/牛奶/豆浆）+果蔬，三类齐全"
     "为佳；④**时间建议**——起床后半小时内、上午 7-9 点之间吃完为宜；"
     "⑤**常见误区**——油条+咸菜高油高盐、只喝咖啡当早餐、饼干零食"
     "充数营养价值低。",
     ["早餐为什么重要", "不吃早餐的危害", "早餐吃什么好",
      "早餐时间", "胆结石和不吃早餐", "营养早餐搭配"],
     ["问午餐", "问饮食规律"],
     "atomic", "",
     "早餐=一夜空腹血糖低大脑靠葡萄糖供能不吃上午注意力下降+长期危害"
     "午餐暴食肥胖胆汁浓缩胆结石伤胃+好早餐谷物加蛋白质加果蔬三类齐"
     "全+起床半小时内7到9点吃完+误区油条咸菜高油高盐只喝咖啡饼干凑"
     "数。"),
    ("kp_card_foodcombo",
     "食物相克辟谣",
     "营养科学知识点内容（人话接口）", "健康与身体",
     "「食物相克」——流传最广的饮食谣言之一：①**常见说法**——「螃蟹"
     "加柿子中毒」「豆腐加菠菜结石」「虾加维C等于砒霜」……都没有可靠"
     "科学依据；②**科学验证**——营养学界做过多次人体试食实验（如兰州"
     "大学、哈尔滨医科大学的实验），受试者无异常反应；③**为什么会「中"
     "招」**——真正原因往往是：食物不洁（细菌性肠胃炎）、个人过敏/不"
     "耐受（乳糖、海鲜）、吃太多（任何食物过量都不适）——被错误归因"
     "到「相克」上；④**真正该注意的**——食物卫生、新鲜度、个人过敏"
     "原，以及均衡多样（没有一种食物含全部营养）；⑤**态度**——对"
     "「养生传言」多一分查证，少一分转发。",
     ["食物相克是真的吗", "螃蟹柿子能一起吃吗", "菠菜豆腐结石",
      "虾和维C冲突吗", "食物相克实验", "饮食谣言"],
     ["问营养均衡", "问食品安全"],
     "atomic", "",
     "食物相克辟谣=螃蟹柿子豆腐菠菜虾维C相克说法均无科学依据+兰州大学"
     "哈尔滨医科大人体试食实验无异常+真因多为不洁过敏不耐受过量被误归"
     "因+该注意的是卫生新鲜过敏原均衡多样+养生传言多查证少转发。"),
]

QUESTIONS = [
    ("QB-1648", "筷子是怎么来的？使用筷子有哪些礼仪禁忌？",
     "传统文化", "技术直答",
     ["筷子", "礼仪", "禁忌", "文化"], "通识拓展471·存量卡补题"),
    ("QB-1649", "为什么不吃早餐危害大？好的早餐标准是什么？",
     "健康与身体", "技术直答",
     ["早餐", "血糖", "胆结石", "营养"], "通识拓展471"),
    ("QB-1650", "「食物相克」有科学依据吗？",
     "健康与身体", "技术直答",
     ["食物相克", "谣言", "科学", "实验"], "通识拓展471"),
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
                               "level:L2", "status:verified", "batch:通识拓展471"],
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
    bank["version"] = "v7.39"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
