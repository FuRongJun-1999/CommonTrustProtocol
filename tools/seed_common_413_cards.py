# -*- coding: utf-8 -*-
"""seed_common_413_cards.py · 通识拓展批次413知识卡+题库（幂等）

413：3 张新卡·数字生活三连（信息茧房与算法推荐 kp_card_finfood /
    短视频与直播 kp_card_shortvideo / 在线学习与网课 kp_card_elearn）。
KCCS 四要素+题干原句触发词。预检已过（QB-1477~1479 可用，三主题
题库 0 覆盖、卡库无同名卡；皮影戏/网络暴力候选已有题被排除）。
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
             "BCS", "B2H6", "borrow", "Rust", "sin", "cos", "tan",
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO", "SVM",
             "MTBF", "SQA", "IMC", "HMO", "JD", "STAR", "Word", "offer"}


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
    ("kp_card_finfood",
     "信息茧房与算法推荐",
     "数字素养知识点内容（人话接口）", "生活常识",
     "算法推荐——「你看到什么」由谁决定：①**推荐原理**——系统根据你的"
     "点击、停留时长、点赞完播等行为给内容打分，再匹配相似内容持续推送"
     "（协同过滤：和你兴趣相似的人喜欢什么就推什么）；②**信息茧房**——"
     "只接收同类观点会让视野越来越窄（学者桑斯坦提出），伴随「回音室"
     "效应」——相似声音反复回响强化偏见；③**破茧方法**——主动关注"
     "不同领域与对立观点、重要信息交叉验证多来源、定期清理和重置兴趣"
     "标签、多用主动搜索少刷被动推荐；④**平台责任**——推荐多样性设计"
     "与青少年模式正在成为监管要求；⑤**清醒认知**——算法没有恶意，"
     "它只是高效放大了你的偏好，破茧的钥匙始终在自己手里。",
     ["什么是信息茧房", "算法推荐原理", "为什么刷到的都相似",
      "怎么打破信息茧房", "回音室效应", "推荐系统"],
     ["问网络暴力", "问隐私保护"],
     "atomic", "",
     "信息茧房=算法按点击时长完播打分协同过滤推送相似内容+只看同类观"
     "点视野窄化桑斯坦提出回音室强化偏见+破茧主动多元关注交叉验证清理"
     "标签主动搜索+平台多样性设计青少年模式+算法无恶意破茧钥匙在自己"
     "手里。"),
    ("kp_card_shortvideo",
     "短视频与直播",
     "数字素养知识点内容（人话接口）", "生活常识",
     "短视频与直播——移动互联网时代的主流内容形态：①**短视频**——"
     "15 秒到几分钟的竖屏内容，靠算法分发，「沉浸式上滑」设计让人容易"
     "一刷就停不下来（即时反馈+无限供给）；②**直播**——实时互动+打赏"
     "与带货：电商直播把「逛」和「买」压缩到一起，但冲动消费多，大额"
     "下单前先给自己 24 小时冷静期；③**健康使用**——设定使用时长（许"
     "多手机有屏幕时间管理）、睡前一小时少刷（蓝光与兴奋内容影响入睡"
     "）、关注创作者而非刷不完的信息流；④**创作侧**——拍摄门槛低人人"
     "可创作，但优质内容依然需要选题、脚本与剪辑功底；⑤**辨别力**——"
     "「眼见」未必为实：摆拍、剧本、断章取义在短视频里很常见，转发前"
     "先求证。",
     ["短视频为什么让人上瘾", "直播带货注意什么",
      "短视频时间管理", "青少年模式", "短视频摆拍辨别", "沉浸式滑动"],
     ["问信息茧房", "问防诈骗"],
     "atomic", "",
     "短视频直播=15秒竖屏算法分发沉浸上滑即时反馈无限供给易沉迷+直播"
     "实时互动打赏带货冲动消费给24小时冷静期+屏幕时间管理睡前一小时"
     "少刷+创作门槛低优质内容仍需选题脚本剪辑+摆拍剧本断章取义转发先"
     "求证。"),
    ("kp_card_elearn",
     "在线学习与网课",
     "学习方法知识点内容（人话接口）", "学习成长",
     "在线学习——数字时代的学习方式：①**优势**——随时回放暂停（难点"
     "可反复看）、打破地域限制接触优质师资、进度自主掌控；②**效率陷阱"
     "——「看过了」不等于「学会了」：被动观看容易产生掌握幻觉，必须"
     "配合主动回忆（合上视频复述要点）和练习输出；③**防分心**——网课"
     "期间手机静音放远处、单次学习 25-45 分钟后休息（番茄工作法）、做"
     "笔记的手比划水的脑子更活跃；④**选课原则**——先看大纲和试听，"
     "警惕「速成」「包过」营销话术，学习没有捷径；⑤**混合式学习**——"
     "线上学概念+线下练习讨论答疑，效果优于纯线上或纯线下。",
     ["网课怎么学效率高", "在线学习走神怎么办", "什么是掌握幻觉",
      "番茄工作法", "怎么选网课", "混合式学习"],
     ["问记忆方法", "问笔记方法"],
     "atomic", "",
     "在线学习=回放暂停打破地域进度自主+看过了不等于学会主动回忆练习"
     "输出防掌握幻觉+手机静音25-45分钟番茄工作法动手笔记+选课看大纲试"
     "听警惕速成包过+线上概念线下练习混合式效果最好。"),
]

QUESTIONS = [
    ("QB-1477", "什么是信息茧房？怎么打破算法推荐造成的视野窄化？",
     "生活常识", "技术直答",
     ["信息茧房", "算法推荐", "回音室", "多元"], "通识拓展413"),
    ("QB-1478", "短视频为什么让人停不下来？怎么健康使用？",
     "生活常识", "技术直答",
     ["短视频", "上瘾", "时间管理", "辨别"], "通识拓展413"),
    ("QB-1479", "上网课怎么学效率更高？怎么避免走神？",
     "学习成长", "技术直答",
     ["网课", "在线学习", "效率", "笔记"], "通识拓展413"),
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
                               "level:L2", "status:verified", "batch:通识拓展413"],
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
                   "added": "2026-09-07"})
        added += 1
    bank["version"] = "v6.84"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
