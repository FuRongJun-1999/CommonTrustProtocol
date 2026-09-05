# -*- coding: utf-8 -*-
"""seed_common_216_cards.py · 通识拓展批次216知识卡+题库（幂等·两卡精批次）

216：生物学-梦游/生活常识-掰手指的关节响
KCCS 四要素+题干原句触发词。三重预检：梦游双库零覆盖（与鬼压床卡 REM 期
划界——梦游是深睡期）；关节响气泡题为化学溶解不同主题。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_sleepwalk",
     "梦游",
     "基础科学知识点内容（人话接口）", "生物学",
     "梦游（睡行症）=**深睡眠期（非 REM）运动控制未完全关闭**的睡眠异常——"
     "与「鬼压床」（REM 期意识醒肌肉麻痹）**正好相反**：梦游是「身体醒着、"
     "大脑还在睡」。①**表现**——坐起/走动/开门甚至穿衣说话，眼神空洞动作笨"
     "拙，**次日无记忆**；②**多发人群**——儿童（神经系统未成熟，青春期多自"
     "愈）、遗传倾向明显、成人发作与睡眠不足/压力/饮酒相关；③**安全处理**——"
     "**温和引导回床**（牵着手低声安抚），**勿强行摇醒**（会惊吓困惑甚至攻"
     "击，但叫醒本身无害——只是会很迷糊）；④**预防**——充足睡眠+规律作息+"
     "睡前排尿、锁好门窗收好危险品（车钥匙/刀具）；频繁发作或成人新发梦游就"
     "医（排除睡眠癫痫等）。",
     ["梦游是怎么回事", "梦游的人知道自己在做什么吗", "梦游能叫醒吗",
      "梦游的危险", "为什么小孩容易梦游", "睡行症"],
     ["问鬼压床（用睡眠瘫痪卡）", "问梦的机制"],
     "atomic", "",
     "梦游（睡行症）=深睡眠期运动控制未关闭——「身体醒大脑睡」与鬼压床[REM 意识醒肌肉麻痹]相反；表现=走动做事次日无记忆；儿童多见青春期自愈+遗传+睡眠不足诱因；处理=温和引导回床勿强摇醒（惊吓但叫醒无害）；锁窗收危险品。"),
    ("kp_card_knucklecrack",
     "掰手指为什么会响",
     "基础科学知识点内容（人话接口）", "生物学",
     "掰手指「咔咔」响=**关节滑液中的气泡空化**：①指关节腔内有滑液（润滑+营"
     "养软骨），滑液中溶解着气体；②快速拉伸关节时**腔内压强骤降**，溶解的气"
     "体瞬间析出形成**空腔**（「牵引空化说」——2015 年 MRI 实时影像支持「爆"
     "裂声就是空腔形成的瞬间」）；③**响后约 20 分钟内无法再响**——气泡重新"
     "溶解回滑液需要时间（这也是「空化说」的证据）。**健康真相**——长期大规模"
     "研究（数十年的对比）显示**掰手指与关节炎发生率无关联**；但**暴力掰/过"
     "度掰**确实可能拉伤韧带关节囊——响不响无所谓，别用力。偶尔弹响无疼痛="
     "正常生理现象。",
     ["掰手指为什么会响", "掰手指会得关节炎吗", "关节响的原理",
      "空化说", "指关节咔咔响", "关节响还能掰吗"],
     ["问关节结构（用骨骼卡）", "问其他人体系列"],
     "atomic", "",
     "掰手指响=关节滑液溶解气体在拉伸降压瞬间空化成腔（2015 MRI 支持；响后 20 分钟无法再响=气泡回溶证据）；数十年研究掰手指与关节炎无关联——响无害暴力掰有风险；偶弹无痛=正常。"),
]

QUESTIONS = [
    ("QB-855", "梦游发生在睡眠的哪个阶段？发现有人梦游应该怎么处理？", "生物学", "技术直答",
     ["深睡眠", "非REM", "引导", "回床", "勿强摇醒", "儿童"], "通识拓展216"),
    ("QB-856", "掰手指关节为什么会「咔咔」响？经常掰手指会导致关节炎吗？", "生物学", "技术直答",
     ["滑液", "气泡", "空化", "关节炎", "无关联", "暴力"], "通识拓展216"),
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
                               "level:L2", "status:verified", "batch:通识拓展216"],
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
                   "added": "2026-09-06"})
        added += 1
    bank["version"] = "v4.87"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
