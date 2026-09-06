# -*- coding: utf-8 -*-
"""seed_common_320_cards.py · 通识拓展批次320知识卡+题库（幂等）

320：生物-麋鹿「四不像」的漂泊与回归/生物-丹顶鹤湿地仙鹤
KCCS 四要素+题干原句触发词。预检已过（QB-1199/1200+双id可用）。
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
    ("kp_card_elk2",
     "麋鹿「四不像」的漂泊与回归",
     "生物保护知识点内容（人话接口）", "基础科学",
     "麋鹿（四不像）——中国特有鹿科的重引入传奇：①**「四不像」**——角似"
     "鹿非鹿、脸似马非马、蹄似牛非牛、尾似驴非驴；②**原产地中国**——"
     "曾遍布东部沼泽（湿地取食水草），因围垦与猎杀至清末野外灭绝，仅剩"
     "北京南海子皇家猎苑一群（300 头）；③**流落海外**——1900 年八国联军"
     "战乱中南海子鹿群被劫掠殆尽，全靠 1894-1902 年间英国十一世贝福特公"
     "爵重金收购散落欧洲各园的 18 头圈养保种——全世界现存麋鹿都是这 18 "
     "头的后代；④**回归**——1985-1986 年中英合作 38 头（后 39 头）重引入"
     "南海子与江苏大丰，现有南海子/大丰/石首三大种群，总数破万（大丰世界"
     "最大麋鹿保护区）；⑤**保护启示**——迁地保种救了种，栖息地重建才让"
     "种群真正回归野外（重引入=圈养保种+野放+栖息地修复三步走范本）。",
     ["麋鹿为什么叫四不像", "麋鹿回归", "麋鹿曾经灭绝吗",
      "南海子麋鹿", "大丰麋鹿保护区", "重引入"],
     ["问麋鹿习性", "问其他重引入物种"],
     "atomic", "",
     "麋鹿=四不像(角鹿脸马蹄牛尾驴)中国特有湿地鹿科+清末野外灭绝仅剩南海"
     "子300头+1900劫掠殆尽靠贝福特公爵18头圈养保种全球后代+1985中英合作"
     "38头重引入南海子大丰+现破万三大种群+迁地保种栖息地重建重引入范本。"),
    ("kp_card_redcrowned",
     "丹顶鹤湿地仙鹤",
     "生物保护知识点内容（人话接口）", "基础科学",
     "丹顶鹤——湿地之神的现实与象征：①**识别**——体羽白头顶红（「丹顶」"
     "其实是裸露皮肤不是羽毛），颈腿细长，体态优雅；②**婚配忠贞**——"
     "一夫一妻终身配对，求偶时雌雄对鸣（“鹤鸣于九皋，声闻于天”）、对舞；"
     "③**湿地旗舰**——栖息于浅水沼泽，食鱼虾嫩草，湿地退化为最大威胁"
     "（保护丹顶鹤=保护整片湿地）；④**迁徙**——在东北繁殖（扎龙保护区"
     "是重要繁殖地）、江苏盐城越冬（世界最大越冬种群），迁徙通道上湿地"
     "一站都不能少；⑤**文化与濒危并存**——中华文化仙鹤=长寿吉祥（松鹤"
     "延年，虽现实中鹤不栖树），但全球野生仅数千只，国家一级保护；⑥"
     "**国鸟争议**——丹顶鹤多次票选居首（拉丁学名意即“日本鹤”引发的"
     "国际命名历史纠葛曾影响评选）。",
     ["丹顶鹤头顶红色是什么", "丹顶鹤为什么象征长寿",
      "丹顶鹤栖息地在哪", "扎龙保护区", "盐城丹顶鹤", "中国国鸟"],
     ["问湿地保护", "问鹤类家族"],
     "atomic", "",
     "丹顶鹤=白羽红顶(裸皮非羽)细长优雅+终身配对对鸣对舞+浅水沼泽旗舰种"
     "(保鹤=保湿地)+扎龙繁殖盐城越冬迁徙通道+文化仙鹤长寿(鹤不栖树)但"
     "野生仅数千只国家一级+拉丁学名日本鹤纠葛影响国鸟评选。"),
]

QUESTIONS = [
    ("QB-1199", "麋鹿为什么叫「四不像」？它经历过怎样的灭绝与回归？", "基础科学", "技术直答",
     ["四不像", "麋鹿", "灭绝", "重引入"], "通识拓展320"),
    ("QB-1200", "丹顶鹤头顶的红色是什么？它为什么是湿地保护的旗舰？", "基础科学", "技术直答",
     ["丹顶", "湿地", "迁徙", "盐城"], "通识拓展320"),
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
                               "level:L2", "status:verified", "batch:通识拓展320"],
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
    bank["version"] = "v5.90"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
