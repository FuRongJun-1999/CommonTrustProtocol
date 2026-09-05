# -*- coding: utf-8 -*-
"""seed_common_183_cards.py · 通识拓展批次183知识卡+题库（幂等·两卡精批次）

183：生活常识-冬天窗户为什么「流泪」（结露）/生活常识-微波炉为什么不能加热带壳鸡蛋
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖（创可贴命中
safemed 卡弃选）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_condensation",
     "冬天窗户为什么会「流泪」（结露）",
     "生活常识知识点内容（人话接口）", "生活常识",
     "冬天窗玻璃内侧挂满水珠甚至淌水（结露）：室内**暖湿空气**遇到冰冷的**玻"
     "璃**，温度降到**露点**以下，空气中的水汽就凝结在玻璃上——「水」全部来"
     "自室内空气（做饭/洗澡/呼吸加湿）。**伴生问题**：窗框周边长期潮湿→发霉"
     "（黑斑）、墙皮起泡脱落。**缓解**：①**定期通风换气**降室内湿度（每天开"
     "窗 10-20 分钟）；②**双层中空玻璃**——两层玻璃间干燥空气/惰性气体隔热，"
     "内层玻璃温度接近室温不再结露（老式单层玻璃最严重）；③窗台放吸水材料/"
     "擦干；④加湿器别开太大（湿度 40-60% 合适）。判断：结露在内侧=室内湿气"
     "大+玻璃隔热差；若「水」出现在玻璃**夹层中间**=中空玻璃密封失效，该换"
     "窗了。",
     ["冬天窗户上有水珠怎么回事", "结露是什么", "窗户内侧结露怎么办",
      "双层玻璃为什么不起雾", "室内湿度多少合适"],
     ["问梅雨季防潮（回南天）", "问除湿机选购"],
     "atomic", "",
     "冬天窗流泪=室内暖湿空气遇冷玻璃降到露点凝结（水来自室内做饭洗澡呼吸）；缓解=每天通风+双层中空玻璃隔热+湿度 40-60%；夹层内水珠=中空玻璃密封失效该换；内侧结露长期致窗框发霉。"),
    ("kp_card_microwaveegg",
     "微波炉为什么不能加热带壳鸡蛋",
     "基础科学知识点内容（人话接口）", "物理学",
     "**带壳鸡蛋进微波炉=小炸弹**：①微波从**内部**加热——蛋内水分迅速变成高"
     "温蒸汽，但**蛋壳和内膜是密闭的**，蒸汽压力无处释放，压力积聚到临界就**"
     "爆炸**（开门瞬间或入口时爆开，高温蛋液烫伤）；②**去壳的完整蛋黄**也危"
     "险——蛋黄膜同样密闭，要戳破蛋黄膜再加热或切开；③同类原理——**带壳板"
     "栗/密封盒装牛奶/葡萄**（葡萄微波会等离子火花）都不宜直接微波。**过热液"
     "体突沸**：纯水在光滑杯中微波加热可能超过 100°C 仍不沸腾（缺乏汽化核），"
     "一旦被晃动/放入勺子/咖啡粉会**瞬间暴沸**喷溅烫伤——久加热的液体先放根"
     "搅拌棒或静置再取。安全守则：微波食物**留缝透气/戳破密闭结构**。",
     ["微波炉为什么不能热鸡蛋", "微波炉加热鸡蛋会爆炸吗",
      "微波炉过热液体突沸", "什么食物不能进微波炉", "葡萄微波"],

     ["问微波炉原理（用电磁波卡）", "问微波炉适用容器"],
     "atomic", "",
     "微波从内部加热：带壳蛋水汽压骤升爆炸（去壳蛋黄也要戳破）——板栗/密封盒/整粒葡萄同理；纯水过热突沸=光滑容器超 100°C 不沸遇扰动暴沸喷溅，久热液体先放搅拌棒；守则=留缝透气戳破密闭结构。"),
]

QUESTIONS = [
    ("QB-794", "冬天窗户玻璃内侧为什么会出现大量水珠？怎么缓解窗户结露？", "生活常识", "技术直答",
     ["水蒸气", "凝结", "露点", "通风", "双层", "中空玻璃", "湿度"], "通识拓展183"),
    ("QB-795", "为什么微波炉不能加热带壳鸡蛋？微波炉加热液体有什么安全隐患？", "物理学", "技术直答",
     ["水汽", "压力", "爆炸", "蛋黄", "突沸", "密闭"], "通识拓展183"),
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
                               "level:L2", "status:verified", "batch:通识拓展183"],
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
    bank["version"] = "v4.56"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
