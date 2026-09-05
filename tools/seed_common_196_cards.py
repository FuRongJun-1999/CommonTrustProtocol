# -*- coding: utf-8 -*-
"""seed_common_196_cards.py · 通识拓展批次196知识卡+题库（幂等·两卡精批次）

196：自然科普-树的年轮/生活常识-味觉地图辟谣
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖（辣=痛觉与辣椒卡
划界）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_treering",
     "树的年轮",
     "基础科学知识点内容（人话接口）", "生物学",
     "年轮=树干横切面上一圈圈的环：①**成因**——树皮内侧的**形成层**每年春"
     "夏生长快、细胞大壁薄（色浅=**早材**），夏末秋初生长慢、细胞小壁厚（色"
     "深=**晚材**）——一浅一深构成一圈，**一圈≈一年**；②**用途**——数年轮"
     "断树龄；**年轮气候学**：宽窄记录当年的水热条件（宽=风调雨顺、窄=干旱"
     "寒冷），可重建数百年至上千年的古气候（火山爆发/干旱史都有「记录」）；"
     "③**特殊情况**：热带四季不分明的地区年轮不明显；被压枝条可能「丢轮」，"
     "极端气候可能「双轮」——精确测年需交叉比对。碳十四测年与年轮校准曲线配"
     "合，是考古定年的重要校准来源。",
     ["年轮是怎么形成的", "年轮为什么一圈深一圈浅", "数年轮能知道树龄吗",
      "年轮能记录气候吗", "形成层是什么"],
     ["问碳十四测年", "问古气候重建"],
     "atomic", "",
     "年轮=形成层春夏早材色浅+秋末晚材色深，一圈约一年；宽窄记录当年水热=年轮气候学重建古气候；热带四季不明年轮不明显、丢轮双轮需交叉比对；碳十四曲线靠年轮校准。"),
    ("kp_card_tastemap",
     "味觉地图是误传",
     "基础科学知识点内容（人话接口）", "生物学",
     "教科书与网络流传的「**味觉地图**」（舌尖尝甜、舌根尝苦、两侧尝酸咸）是"
     "**误传**：①源于 1901 年德国一篇论文的示意图，被后来的教科书**误读夸"
     "大**（原论文只显示各区域敏感度有细微差异，并非「只能尝某味」）；②**真"
     "相**——**全舌所有区域都能感受全部基本味**（酸甜苦咸鲜），只是敏感度略"
     "有差异（差异小到日常尝不出）；味蕾不仅分布在舌，还遍布软腭、咽喉；③基"
     "本味=**酸甜苦咸鲜**（鲜味=谷氨酸，1960s 后才被确认为独立味觉）；「"
     "辣」是痛觉、「麻」是触觉振动感——都不算味觉；④更正：味蕾约每 10 天更新"
     "一次，老年人味觉迟钝是味蕾更新变慢+嗅觉退化（风味感知 70% 靠嗅觉）。",
     ["味觉地图是真的吗", "舌尖尝甜舌根尝苦", "味蕾分布在哪里",
      "基本味觉有哪几种", "鲜味是什么味觉"],
     ["问辣椒为什么辣（用辣椒卡）", "问嗅觉如何工作"],
     "atomic", "",
     "味觉地图误传：全舌所有区域都能尝酸甜苦咸鲜（敏感度差异小到日常无感），源于 1901 论文示意图被教科书误读；味蕾遍布舌+软腭咽喉约 10 天更新；基本味=酸甜苦咸鲜，辣麻是痛触觉；风味 70% 靠嗅觉。"),
]

QUESTIONS = [
    ("QB-820", "树的年轮是怎么形成的？为什么说年轮能记录古代气候？", "生物学", "技术直答",
     ["形成层", "季节", "早材", "晚材", "气候", "一圈"], "通识拓展196"),
    ("QB-821", "「舌尖尝甜、舌根尝苦」的味觉地图说法对吗？基本味觉有哪几种？", "生物学", "技术直答",
     ["误传", "全舌", "酸甜苦咸鲜", "鲜味", "味蕾"], "通识拓展196"),
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
                               "level:L2", "status:verified", "batch:通识拓展196"],
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
    bank["version"] = "v4.69"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
