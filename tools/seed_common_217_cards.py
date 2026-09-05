# -*- coding: utf-8 -*-
"""seed_common_217_cards.py · 通识拓展批次217知识卡+题库（幂等·两卡精批次）

217：生活常识-喝酒脸红的遗传机制/趣味神经-为什么不能自己挠痒自己
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖（辣椒卡讲血管扩张
脸红、酒驾卡讲法律、蜂毒卡讲过敏——本卡为酒精代谢遗传机制与怕痒小脑预测，
均划界）。执行前外文长词检测（ALDH2/ADH 加白名单）。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_asianflush",
     "喝酒脸红的遗传机制",
     "基础科学知识点内容（人话接口）", "生物学",
     "喝酒脸红=**乙醛脱氢酶（ALDH2）基因变异**：①酒精（乙醇）代谢两步——先"
     "由 ADH 酶变成**乙醛**（有毒：扩张血管→脸红/心跳快/恶心；也是一级致癌"
     "物），再由 ALDH2 酶把乙醛变成无害的乙酸；②约 **30-50% 的东亚人**携带"
     "ALDH2 基因变异（酶活性大减）——乙醛堆积→**一喝就脸红**（欧美人极少此"
     "变异，所以「老外更能喝」是基因差异不是练出来的）；③**重要误区**——「脸"
     "红=能喝/代谢快」完全错误：脸红恰恰是**乙醛中毒信号**，这类人继续喝，"
     "食管癌风险显著升高；④「练酒量」练的是大脑耐受度，乙醛伤害一点没少。"
     "结论：喝酒脸红的人**最不该劝酒**。",
     ["喝酒为什么会脸红", "喝酒脸红的人能喝吗", "乙醛脱氢酶",
      "喝酒脸红是代谢好吗", "东亚人喝酒脸红", "一喝就脸红"],
     ["问酒驾法规（用酒驾卡）", "问酒精肝（就医）"],
     "atomic", "",
     "喝酒脸红=ALDH2 乙醛脱氢酶基因变异（东亚人 30-50% 携带）→有毒乙醛堆积扩张血管脸红心跳——是中毒信号非能喝；食管癌风险显著升高；「练酒量」练的是耐受伤害不减——脸红者最不该被劝酒。"),
    ("kp_card_ticklish",
     "为什么不能自己挠痒自己",
     "基础科学知识点内容（人话接口）", "生物学",
     "自己挠自己**不会痒**，别人一挠就痒到不行——秘密在**小脑的预测机制**："
     "①自己动作时，大脑运动系统同时向小脑发送「动作副本」，小脑**精准预测**"
     "这个动作会产生的皮肤触感并**提前抵消**（过滤掉自身动作的感觉——这样大"
     "脑才能专注于外界新刺激）；②**别人挠时无法预测**（时机力度都未知），触"
     "觉信号以全新刺激处理→痒感强烈；③实验证实：用机械装置**延迟**自己挠的"
     "动作，痒感会随延迟增强（预测失效）；④进化意义：区分「自我产生」与「外"
     "界产生」的触觉，是生存必需（迅速发现外界威胁如虫子）。精神分裂症患者"
     "常能自己挠痒自己——与「自我动作辨识」机制受损相关（研究线索）。",
     ["为什么自己挠痒自己不痒", "挠痒痒的原理", "小脑预测",
      "为什么别人挠痒痒更痒", "自我与他人的触觉区分"],
     ["问梦游与睡眠（用睡眠系列卡）", "问触觉感受器"],
     "atomic", "",
     "自己挠自己不痒=小脑接收「动作副本」精准预测自身触感并提前抵消（过滤自我信号专注外界）；别人挠无法预测痒感强；机械延迟自己挠动作痒感增强（预测失效实验）；进化=区分自我/外界触觉的生存机制；精神分裂者常可自挠——研究线索。"),
]

QUESTIONS = [
    ("QB-857", "为什么有些人一喝酒就脸红？「脸红代表酒量大」的说法对吗？", "生物学", "技术直答",
     ["乙醛", "ALDH2", "基因", "代谢", "中毒", "食管癌"], "通识拓展217"),
    ("QB-858", "为什么自己挠痒痒自己不会痒，别人挠就痒得不行？", "生物学", "技术直答",
     ["小脑", "预测", "动作副本", "抵消", "无法预测"], "通识拓展217"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    whitelist = {"ALDH2", "ADH"}
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{5,}", content):
            if word not in whitelist:
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
                               "level:L2", "status:verified", "batch:通识拓展217"],
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
    bank["version"] = "v4.88"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
