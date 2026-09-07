# -*- coding: utf-8 -*-
"""seed_common_405_cards.py · 通识拓展批次405知识卡+题库（幂等）

405：3 张新卡求职主题三连（简历 kp_card_resume / 面试要点
    kp_card_interview / 求职渠道与流程 kp_card_jobhunt）。
KCCS 四要素+题干原句触发词。预检已过（QB-1453~1455 可用，
三主题题库卡库双零；试用期主题已有 QB-672 排除劳动合同卡）。
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
    ("kp_card_resume",
     "简历",
     "求职技能知识点内容（人话接口）", "职场咨询",
     "简历——求职的「第一印象」：①**一页原则**——HR 初筛一份简历平均"
     "只有 10-30 秒，应届生/十年内经验一页足够；②**标准结构**——基本"
     "信息、教育背景、工作/实习经历（倒序排列，最近的放最前）、技能与"
     "证书；③**经历用 STAR 法则写**——情境（背景）、任务（目标）、"
     "行动（你做了什么）、结果（量化成果：效率提升 30%/服务用户 1 万+"
     "），写「做了什么+带来什么」而不是岗位职责复述；④**针对性**——"
     "一岗一简历，对照岗位描述的关键词调整重点；⑤**细节**——零错别"
     "字、证件照正式、文件命名「姓名-岗位-简历」、发 PDF 不发 Word"
     "（防排版错乱）。",
     ["简历怎么写", "简历一页还是两页", "STAR法则",
      "简历经历怎么写", "简历注意事项", "应届生简历"],
     ["问面试", "问求职"],
     "atomic", "",
     "简历=一页原则HR初筛10到30秒+基本信息教育经历倒序技能证书+STAR"
     "法则情境任务行动结果量化成果+一岗一简历对JD调重点+零错别字正式"
     "照PDF命名规范。"),
    ("kp_card_interview",
     "面试要点",
     "求职技能知识点内容（人话接口）", "职场咨询",
     "面试——双向选择的深度对话：①**面试前**——查公司主营业务/近期"
     "动态/岗位要求，准备好 1 分钟自我介绍（我是谁+核心经历+为什么胜"
     "任），线上面试提前测设备网络；②**经历问答**——继续用 STAR 结构"
     "讲具体案例，用细节和数据支撑，不背模板话术；③**必考题**——「为"
     "什么离职」「为什么选我们」「缺点是什么」（讲一个真实但不致命的"
     "缺点+改进动作）；④**反问环节**——问成长路径/团队构成/业务方向"
     "（展示思考），薪资福利等 HR 谈（通常初面不主动提）；⑤**礼仪**——"
     "守时（提前 10 分钟）、着装符合行业、面试后 24 小时内发感谢信息。",
     ["面试怎么准备", "自我介绍怎么说", "为什么离职怎么答",
      "面试反问环节问什么", "面试礼仪", "线上面试"],
     ["问简历", "问谈薪"],
     "atomic", "",
     "面试=提前查公司岗位备1分钟自我介绍+STAR讲案例细节数据支撑+高频"
     "题离职原因选我们缺点+反问问成长团队业务薪资留给HR谈+提前10分钟"
     "着装得体24小时内感谢。"),
    ("kp_card_jobhunt",
     "求职渠道与流程",
     "求职技能知识点内容（人话接口）", "职场咨询",
     "求职渠道与完整流程：①**渠道效率排序**——内推（熟人推荐，成功率"
     "最高、简历必达）> 猎头（中高端岗位）> 招聘网站投递 > 官网直投；"
     "校招走校园渠道（秋招春招）；②**标准流程**——投递 → HR 初筛 →"
     "笔试 → 一面二面（业务面+主管面）→ HR 面 → offer → 背景调查 →"
     "入职体检 → 入职；③**offer 注意**——要书面 offer（口头不算数），"
     "看清薪资构成（底薪+绩效+补贴）、试用期条款、入职时间，可协商但"
     "别反复拉扯；④**防坑红线**——凡入职前收取「押金/培训费/服装费」"
     "的都是违规违法，任何单位不得扣押身份证原件；⑤**节奏建议**——"
     "骑驴找马优于裸辞，手里有 offer 谈判底气完全不同。",
     ["找工作渠道有哪些", "内推是什么", "求职流程",
      "offer要注意什么", "招聘收费是骗局吗", "裸辞还是骑驴找马"],
     ["问简历", "问面试"],
     "atomic", "",
     "求职=内推成功率最高猎头中高端校招走秋春招+投递初筛笔试一二面"
     "HR面offer背调入职+书面offer看清薪资构成试用期条款+入职前收费扣"
     "证件都是违法红线+骑驴找马手握offer有底气。"),
]

QUESTIONS = [
    ("QB-1453", "简历怎么写才能脱颖而出？工作经历用什么法则写？",
     "职场咨询", "技术直答",
     ["简历", "STAR", "经历", "求职"], "通识拓展405"),
    ("QB-1454", "面试前怎么准备？面试反问环节问什么好？",
     "职场咨询", "技术直答",
     ["面试", "准备", "自我介绍", "反问"], "通识拓展405"),
    ("QB-1455", "找工作的渠道有哪些？拿到 offer 要注意什么？",
     "职场咨询", "技术直答",
     ["求职", "渠道", "内推", "offer"], "通识拓展405"),
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
                               "level:L2", "status:verified", "batch:通识拓展405"],
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
    bank["version"] = "v6.75"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
