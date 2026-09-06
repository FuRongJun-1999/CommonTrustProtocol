# -*- coding: utf-8 -*-
"""seed_common_296_cards.py · 通识拓展批次296知识卡+题库（幂等）

296：食品-罐头保存原理/食品-蜂蜜结晶与保存
KCCS 四要素+题干原句触发词。预检已过（QB-1118/1119+双id可用）。
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
             "BCS"}


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
    ("kp_card_canned",
     "罐头保存原理",
     "食品科学知识点内容（人话接口）", "生活常识",
     "罐头为什么能放几年：①**三步锁鲜**——高温彻底灭菌（高压釜 121°C 灭"
     "芽孢）+真空密封隔绝外界菌源+耐热无菌包装——三者缺一不可；②**防腐剂"
     "误会**——正规罐头靠「热杀菌+密封」无需防腐剂（防腐剂反而多数不合规），"
     "与泡面面饼同理是工艺而非添加剂；③**营养流失有限**——瞬间高温灭菌"
     "营养损失比家庭反复加热烹饪还小，维生素 C 损失约 10-20%（冷冻也是"
     "即时锁鲜好手段）；④**胀罐即弃**——罐盖/罐身鼓起=内部微生物产气"
     "（密封失败被污染），肉毒杆菌芽孢风险，**绝对不可食用**哪怕看着正常；"
     "⑤**开口后**——失去密封环境按普通食物对待，冷藏并尽快吃完；⑥"
     "**轻伤罐**——轻微凹陷无漏液无胀气可尽快食用，锈穿或渗漏弃。",
     ["罐头为什么能保存很久", "罐头有防腐剂吗", "罐头营养流失吗",
      "胀罐的罐头能吃吗", "罐头打开后能放多久", "肉毒杆菌"],
     ["问罐藏工艺细节", "问军粮设计"],
     "atomic", "",
     "罐头=121°C高压灭菌+真空密封无菌包装三步锁鲜无需防腐剂+瞬时高温营养"
     "损失小于家庭烹饪+胀罐=微生物产气密封失败绝不可食(肉毒风险)+开口后"
     "冷藏速食+轻凹陷可快食锈穿弃。"),
    ("kp_card_honey",
     "蜂蜜结晶与保存",
     "食品科学知识点内容（人话接口）", "生活常识",
     "蜂蜜常识：①**为什么几乎不变质**——含水量低（<20%）+高糖高渗透压"
     "（微生物被「腌」脱水）+天然酸性 pH3.5-4.5+葡萄糖氧化酶产过氧化氢——"
     "四重屏障（古墓千年蜂蜜可食的传说有科学基础）；②**结晶是正常现象**"
     "——葡萄糖过饱和析出（低温加速），不是掺糖不是变质，35-40°C 温水"
     "缓慢加热可复原（**勿沸水/微波高温**——破坏活性酶与风味）；③**"
     "变质信号**——表面起泡发酵酸酒味（耐渗透压酵母在含水量高时才发作"
     "——说明掺水或吸潮）；④**保存**——密封避光（吸潮会降浓度+光破坏"
     "成分）、金属勺长期存取微弱反应宜用木勺陶瓷勺；⑤**一岁以下婴儿"
     "禁食**——可能含肉毒杆菌芽孢（婴儿肠道菌群未建立无法抑制）；⑥**"
     "「土蜂蜜更营养」有限**——成分差异主要在风味与微量物质，糖分主体"
     "无本质差别，购买正规渠道防掺假才是关键。",
     ["蜂蜜结晶了还能吃吗", "蜂蜜为什么不变质", "蜂蜜怎么保存",
      "蜂蜜不能用什么冲", "婴儿为什么不能吃蜂蜜", "土蜂蜜更好吗"],
     ["问蜂蜜掺假鉴别", "问蜂产品家族"],
     "atomic", "",
     "蜂蜜=低水量高渗透压酸性产过氧化氢四重抑菌(千年可食有据)+结晶=葡萄"
     "糖析出正常35-40°C温水复原勿高温+起泡酒酸味=发酵变质+密封避光木勺"
     "+一岁以下婴儿禁食(肉毒芽孢)+土蜂蜜差异在风味防掺假是关键。"),
]

QUESTIONS = [
    ("QB-1118", "罐头为什么能保存很久？胀罐的罐头还能吃吗？", "生活常识", "技术直答",
     ["灭菌", "密封", "防腐剂", "胀罐"], "通识拓展296"),
    ("QB-1119", "蜂蜜结晶了还能吃吗？为什么婴儿不能吃蜂蜜？", "生活常识", "技术直答",
     ["结晶", "正常", "婴儿", "肉毒"], "通识拓展296"),
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
                               "level:L2", "status:verified", "batch:通识拓展296"],
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
                   "added": "2026-09-06"})
        added += 1
    bank["version"] = "v5.67"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
