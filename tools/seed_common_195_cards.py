# -*- coding: utf-8 -*-
"""seed_common_195_cards.py · 通识拓展批次195知识卡+题库（幂等·两卡精批次）

195：生物学-双胞胎的两种类型/生活常识-耳鸣
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖（耳鸣在睡眠瘫痪卡
仅幻觉一句提及；煤气开灯命中既有卡弃选）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_twins",
     "双胞胎的两种类型",
     "基础科学知识点内容（人话接口）", "生物学",
     "双胞胎分两种：①**同卵双胞胎**——**一个受精卵**早期分裂成两个胚胎：基因"
     "**几乎完全相同**（所以性别必同、长相极像、血型相同；连性格智商也高度相"
     "关——遗传学研究金样本），自然发生率约千分之四；②**异卵双胞胎**——**两"
     "个卵分别受精**：基因相似度与普通兄弟姐妹一样（约 50%），性别可不同，长"
     "相可差很大；与遗传（母亲家族促排卵倾向）、促排卵药物、高龄相关。**冷知"
     "识**：①同卵双胞胎的**指纹也不同**——指纹受胎儿期微环境（羊水压力/指"
     "尖位置）影响；②同卵中表观遗传（基因开关修饰）随年龄分化——老来差异越"
     "来越大；③鉴定：DNA 检测是唯一可靠区分法（异卵可测，同卵测不出差异）。",
     ["双胞胎是怎么形成的", "同卵和异卵的区别", "同卵双胞胎指纹相同吗",
      "双胞胎遗传吗", "龙凤胎是同卵还是异卵"],
     ["问基因与遗传（用基因卡）", "问多胞胎风险"],
     "atomic", "",
     "双胞胎=同卵（一个受精卵分裂：基因几乎相同性别必同·指纹仍不同[微环境]·自然率约千分之四）vs 异卵（两卵分别受精：基因如普通兄弟姐妹性别可不同·与母系遗传/促排/高龄相关）；DNA 检测可辨异卵，同卵难分。"),
    ("kp_card_tinnitus",
     "耳鸣",
     "生活常识知识点内容（人话接口）", "生活常识",
     "耳鸣=没有外界声源却**听到声音**（蝉鸣/嗡嗡/嘶嘶），是**听觉系统异常放电"
     "**的信号而非疾病本身。**常见诱因**：①**噪音暴露**（KTV/耳机音量过大/工"
     "地——毛细胞损伤不可再生，是最主要可防原因）；②耵聍（耳屎）栓塞、中耳"
     "炎；③压力大疲劳咖啡因；④某些药物（大剂量阿司匹林等）。**应对**：短时"
     "轻微耳鸣多可自行恢复——**远离噪音+规律作息**；**就医信号**：**单侧持"
     "续性耳鸣**、伴**听力下降/眩晕/耳闷**（排查听神经瘤/突发性耳聋——突发"
     "性耳聋是「耳科急症」，72 小时内治疗恢复率高）；搏动性耳鸣（与心跳同步）"
     "查血管。**预防**：耳机 60-60 原则（音量≤60%、每次≤60 分钟）、噪音环境"
     "戴耳塞。",
     ["耳鸣是什么原因", "耳鸣需要就医吗", "单侧耳鸣要警惕",
      "突发性耳聋", "耳机音量多大安全", "60-60原则"],
     ["问耳机听力保护", "问突发性耳聋治疗（就医）"],
     "atomic", "",
     "耳鸣=无外界声源却听到声音（听觉系统异常放电信号）：噪音暴露是首要可防原因（毛细胞不可再生）；就医信号=单侧持续/伴听力下降眩晕（突发性耳聋 72h 急症）/搏动性；预防=耳机 60-60 原则+噪音环境戴耳塞。"),
]

QUESTIONS = [
    ("QB-818", "同卵双胞胎和异卵双胞胎是怎么形成的？同卵双胞胎的指纹一样吗？", "生物学", "技术直答",
     ["一个受精卵", "分裂", "基因", "指纹", "不同", "异卵"], "通识拓展195"),
    ("QB-819", "耳鸣的常见原因有哪些？什么情况下耳鸣必须立即就医？", "生活常识", "技术直答",
     ["噪音", "单侧", "持续", "听力下降", "突发性耳聋", "72"], "通识拓展195"),
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
                               "level:L2", "status:verified", "batch:通识拓展195"],
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
    bank["version"] = "v4.68"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
