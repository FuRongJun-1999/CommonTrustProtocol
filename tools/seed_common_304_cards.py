# -*- coding: utf-8 -*-
"""seed_common_304_cards.py · 通识拓展批次304知识卡+题库（幂等）

304：历史-罗马斗兽场/历史-罗马法（古罗马文明新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1143/1144+双id可用）。
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
             "BCS", "B2H6", "borrow", "Rust"}


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
    ("kp_card_colosseum",
     "罗马斗兽场",
     "历史知识点内容（人话接口）", "历史",
     "罗马斗兽场（弗拉维圆形剧场）：①**规模**——公元 72-80 年建成，可容"
     "5 万观众，古罗马最大的圆形剧场（混凝土+火山灰建造——罗马混凝土"
     "耐久之谜至今在研究）；②**拱券技术**——80 个拱形入口让观众 15 分"
     "钟内疏散完毕（现代体育场疏散设计仍参考），拱券+混凝土是罗马建筑"
     "两大法宝；③**角斗表演**——角斗士（多为战俘/奴隶/罪犯，受过专门"
     "学校训练，明星级角斗士可获自由）、猛兽狩猎、海战重演（早期可注水"
     "），观众免费入场是政治收买手段（「面包与竞技场」）；④**庞贝**——"
     "公元 79 年维苏威火山喷发被火山灰掩埋的城市，凝固的罗马日常生活"
     "（面包房/广告涂鸦/狗的化石姿态），考古价值无可替代；⑤**万神殿**——"
     "直径 43 米世界最大无筋混凝土穹顶保持至今，顶部圆孔采光，揭示罗马"
     "工程巅峰；⑥**活化石**——斗兽场历经地震/石料盗取仍屹立，世界遗产。",
     ["罗马斗兽场是干什么的", "角斗士是什么人", "庞贝城怎么消失的",
      "罗马混凝土", "万神殿穹顶", "拱券技术"],
     ["问罗马输水道", "问角斗士制度细节"],
     "atomic", "",
     "罗马斗兽场=公元72-80年容5万人混凝土+火山灰建造+80拱券15分钟疏散"
     "+角斗士战俘奴隶明星可获自由+面包与竞技场政治收买+庞贝79年火山灰"
     "凝固日常+万神殿43米无筋穹顶至今+输水道工程。"),
    ("kp_card_romanlaw",
     "罗马法",
     "历史知识点内容（人话接口）", "历史",
     "罗马法为什么影响至今：①**脉络**——从《十二铜表法》（前 451 年，"
     "成文法开端，贵族不再随意解释习惯法）→公民法→万民法（帝国扩张后"
     "适用于所有自由民）→《民法大全》（查士丁尼 529-534 年汇编，集大成）；"
     "②**核心理念**——私有财产神圣不可侵犯+法律面前公民人人平等（限"
     "自由民）+「没有告诉就没有法官」（不告不理原则源头）；③**自然法"
     "思想**——西塞罗：法律是理性的体现，高于人定法（后世人权宪政思想"
     "源头之一）；④**陪审制度与律师辩护**——现代司法程序的雏形；⑤**"
     "影响**——大陆法系（法德中日等民法典）直接继承罗马法体系，《拿破"
     "仑法典》是其现代翻版；「法律是善良与公正的艺术」这句罗马法谚仍"
     "是法学院第一课。",
     ["罗马法是什么", "十二铜表法", "万民法和公民法",
      "罗马法的影响", "查士丁尼民法大全", "自然法思想"],
     ["问罗马政制", "问普通法系对比"],
     "atomic", "",
     "罗马法=十二铜表法成文开端(前451)→公民法→万民法→查士丁尼民法"
     "大全汇编+私有财产神圣+不告不理源头+西塞罗自然法理性高于人定法"
     "+陪审律师辩护雏形+大陆法系民法典直接继承(拿破仑法典现代翻版)。"),
]

QUESTIONS = [
    ("QB-1143", "罗马斗兽场是干什么用的？庞贝城是怎么消失的？", "历史", "技术直答",
     ["斗兽场", "角斗", "庞贝", "火山"], "通识拓展304"),
    ("QB-1144", "罗马法经历了怎样的发展脉络？它对现代法律有什么影响？",
     "历史", "技术直答",
     ["十二铜表法", "万民法", "民法大全", "影响"], "通识拓展304"),
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
                               "level:L2", "status:verified", "batch:通识拓展304"],
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
    bank["version"] = "v5.74"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
