# -*- coding: utf-8 -*-
"""seed_common_186_cards.py · 通识拓展批次186知识卡+题库（幂等·两卡精批次）

186：生活常识-跑步岔气/生活常识-挑草莓的技巧
KCCS 四要素+题干原句触发词。三重预检：岔气双库零覆盖；草莓挑选技巧与
fruitform 卡（果实结构角度）划界。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_stitch",
     "跑步为什么会岔气",
     "生活常识知识点内容（人话接口）", "生活常识",
     "岔气（运动相关短暂性腹痛，ETAP）=运动中肋下/侧腹的**锐痛或抽痛**：①**"
     "成因主流假说**——膈肌（呼吸肌）供血不足**痉挛缺血**+内脏韧带被上下震"
     "动牵拉；②**诱因**：**饭后过早运动**（胃里食物震动牵拉+血液分流）、呼"
     "吸**浅快无节奏**、突然加大强度、核心肌群弱、跑前热身不足。**发生了怎么"
     "办**：①减速或改为步行；②**深慢呼吸**——深吸一口气，憋住的同时向痛侧"
     "弯腰挤压，再缓慢呼出（重复几次多能缓解）；③用手**按压痛点**随呼吸按"
     "压。**预防**：餐后 1-2 小时再运动；跑前热身+动态拉伸；建立**节律呼吸**"
     "（如两步一吸两步一呼）；平时加强核心训练。持续剧烈疼痛（尤其按压有固定"
     "锐痛点）要排除其他急腹症，勿硬撑。",
     ["跑步为什么会岔气", "岔气了怎么办", "岔气的处理方法",
      "怎么预防岔气", "膈肌痉挛"],
     ["问运动损伤RICE（用RICE卡）", "问运动呼吸节奏训练"],
     "atomic", "",
     "岔气=膈肌痉挛缺血+内脏韧带震动牵拉：诱因=餐后过早运动/呼吸浅快无节奏/突然加量/核心弱；处理=减速+深慢呼吸向痛侧弯腰憋气+按压痛点；预防=餐后 1-2h 运动+节律呼吸+核心训练；持续剧痛排除急腹症。"),
    ("kp_card_pickstrawberry",
     "挑草莓的技巧",
     "生活常识知识点内容（人话接口）", "生活常识",
     "挑草莓四看一闻：①**看果蒂**——蒂叶**鲜绿挺立**=新鲜（发黄蔫软=放了多"
     "日）；②**看颜色**——整体**均匀红透**（红中带黄绿的是没熟透，酸性大）；"
     "③**看表面**——果面干燥无碰伤水渍（碰伤处易霉烂）；④**闻香气**——熟透"
     "的草莓有**明显甜香**，没香味的多为催熟或未熟；⑤**看大小与形状**——中"
     "等大小、形状自然圆锥形风味佳（超大畸形的未必更好，可能是激素或品种特性"
     "——外观只是一方面）。**清洗**：草莓**吃前再洗**（洗后存放易霉），用流"
     "动水轻冲+淡盐水/小苏打水浸泡几分钟再冲净，**去蒂洗**（去蒂泡洗会让污水"
     "倒渗进果肉）。保存：不洗直接铺开冷藏，2-3 天内吃完。",
     ["怎么挑草莓", "草莓蒂新鲜", "草莓怎么清洗", "大草莓好还是小草莓好",
      "草莓怎么保存"],
     ["问挑西瓜（用挑西瓜卡）", "问草莓酱做法"],
     "atomic", "",
     "挑草莓=果蒂鲜绿挺立+颜色均匀红透+表面无碰伤+浓香=熟透；清洗=吃前再洗、流动水冲+淡盐水浸泡、去蒂洗会让污水倒渗；不洗铺开冷藏 2-3 天。"),
]

QUESTIONS = [
    ("QB-800", "跑步时为什么会岔气？岔气了应该怎么快速缓解？", "生活常识", "技术直答",
     ["膈肌", "痉挛", "深呼吸", "按压", "餐后", "节律"], "通识拓展186"),
    ("QB-801", "怎么挑新鲜好吃的草莓？草莓应该怎么清洗才正确？", "生活常识", "技术直答",
     ["果蒂", "鲜绿", "红透", "甜香", "去蒂洗", "倒渗"], "通识拓展186"),
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
                               "level:L2", "status:verified", "batch:通识拓展186"],
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
    bank["version"] = "v4.59"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
