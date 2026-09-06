# -*- coding: utf-8 -*-
"""seed_common_316_cards.py · 通识拓展批次316知识卡+题库（幂等）

316：生物-朱鹮保护（7只到万只）/生物-藏羚羊可可西里守护（保护动物新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1187/1188+双id可用）。
注：大熊猫国宝已有 QB-359，本批避让。
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
    ("kp_card_crestedibis",
     "朱鹮保护：从7只到万只",
     "生物保护知识点内容（人话接口）", "基础科学",
     "朱鹮——「东方宝石」的拯救奇迹：①**濒临灭绝**——20 世纪中期因农药"
     "（DDT 富集）、湿地围垦、猎杀，朱鹮从东亚常见鸟骤减，1970 年代日本"
     "仅剩数只（最后本土个体老死），全球目光转向中国；②**7 只奇迹**——"
     "1981 年中科院刘荫增团队历经三年跋涉 5 万公里，在陕西洋县找到世界"
     "仅存的 7 只野生朱鹮（姚家沟巢区）；③**保护组合拳**——就地保护"
     "（洋县划保护区+禁伐禁猎+不施农药的水田）+人工繁育突破（攻克育雏"
     "难关）+野化放归（董寨/湿地重建种群）；④**成果**——从 7 只恢复到"
     "万余只（野外+人工），受威胁等级从「极危」降为「濒危」——世界濒危"
     "物种保护最成功案例之一；⑤**为什么脆弱**——湿地依赖+食谱单一"
     "（泥鳅小鱼）+繁殖率低（一窝 2-4 枚）；⑥**启示**——单一物种拯救"
     "带动整片湿地生态恢复（伴生物种同步受益）。",
     ["朱鹮为什么濒危", "朱鹮是怎么被拯救的", "洋县朱鹮",
      "朱鹮现在有多少只", "东方宝石", "濒危物种保护"],
     ["问朱鹮习性与形态", "问其他极危鸟类"],
     "atomic", "",
     "朱鹮=东方宝石因农药湿地围垦骤减+1981刘荫增陕西洋县寻获仅存7只野生"
     "+就地保护区+人工繁育野化放归组合拳+恢复至万余只极危降濒危+湿地"
     "依赖繁殖率低脆弱+单一物种拯救带动湿地生态。"),
    ("kp_card_antelope",
     "藏羚羊与可可西里守护",
     "生物保护知识点内容（人话接口）", "基础科学",
     "藏羚羊——高原精灵的守护战：①**悲剧起源**——藏羚羊底绒（沙图什）"
     "制成的披风极轻极暖，一条需猎杀 3-5 只，80-90 年代盗猎猖獗，种群从"
     "百万级跌至不足 7 万只；②**可可西里**——青海无人区是主要产羔迁徙地"
     "，90 年代治多县委杰桑·索南达杰组建武装反盗猎队伍，1994 年单枪匹马"
     "押运盗猎者时牺牲（电影《可可西里》原型），引发全国关注；③**志愿者"
     "与保护站**——索南达杰保护站等陆续建立，巡山反盗猎持续至今；④**"
     "成效**——2008 年起种群回升至 30 万只以上，2016 年国际自然保护联盟从「濒危」"
     "降为「近危」；⑤**制度升级**——可可西里 2017 年列入世界自然遗产，"
     "三江源国家公园整体保护；⑥**迁徙之谜**——每年雌羊集群迁往卓乃湖"
     "集中产羔（数百公里迁徙原因至今仍是研究课题）。",
     ["藏羚羊为什么濒危", "可可西里守护者", "索南达杰",
      "沙图什披风", "藏羚羊现在有多少只", "可可西里申遗"],
     ["问三江源国家公园", "问其他高原动物"],
     "atomic", "",
     "藏羚羊=沙图什底绒披风盗猎百万级跌至7万+可可西里产羔迁徙地+索南"
     "达杰1994牺牲电影可可西里原型+保护站巡山至今+回升30万只以上国际自然保护联盟"
     "降近危+2017世界自然遗产三江源整体保护+雌羊卓乃湖集中产羔迁徙谜。"),
]

QUESTIONS = [
    ("QB-1187", "朱鹮是怎么从濒临灭绝被拯救回来的？现在有多少只？", "基础科学", "技术直答",
     ["朱鹮", "洋县", "7只", "人工繁育"], "通识拓展316"),
    ("QB-1188", "藏羚羊为什么曾被大量猎杀？可可西里的守护者是谁？", "基础科学", "技术直答",
     ["藏羚羊", "沙图什", "索南达杰", "可可西里"], "通识拓展316"),
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
                               "level:L2", "status:verified", "batch:通识拓展316"],
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
    bank["version"] = "v5.86"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
