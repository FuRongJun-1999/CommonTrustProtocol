# -*- coding: utf-8 -*-
"""seed_common_258_cards.py · 通识拓展批次258知识卡+题库（幂等）

258：生活-信用卡与个人征信/生活-五险一金（社保公积金）
KCCS 四要素+题干原句触发词。预检已过（QB-965/966+双id可用）。金融生活新域。
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
             "AlphaGo", "CFOP"}


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
    ("kp_card_creditcard",
     "信用卡与个人征信",
     "生活常识知识点内容（人话接口）", "生活常识",
     "信用卡使用的信用规则：①**免息期**——账单日后刷卡享最长约 50 天免息"
     "（各银行 20-56 天不等），前提是**全额还款**；②**最低还款的陷阱**——"
     "只还最低还款额不算逾期，但**未还部分从消费日起全额计息**（日息万分之"
     "五≈年化 18%），且不是只对差额计息；③**分期手续费真实利率**——分期"
     "「月手续费 0.6%」听着低，实际资金逐月减少而手续费按全额算，真实年化"
     "约 13-15%；④**逾期上征信**——逾期记录进入央行征信报告，还清后仍"
     "展示 5 年才消除，直接影响房贷/车贷审批（「连三累六」——连续 3 个月"
     "或累计 6 次逾期属严重不良）；⑤**征信自查**——每人每年 2 次免费查询"
     "本人征信报告（央行征信中心官网/线下网点），频繁「硬查询」（贷款审批"
     "类）也会轻微影响评分；⑥**安全底线**——不外借信用卡、不帮人「跑分」"
     "套现（涉嫌违法）。",
     ["信用卡免息期怎么算", "最低还款有什么后果", "信用卡分期划算吗",
      "征信逾期记录多久消除", "征信报告怎么查", "连三累六是什么"],
     ["问房贷利率政策", "问信用卡盗刷处理"],
     "atomic", "",
     "信用卡=全额还款享最长50天免息+最低还款不算逾期但全额计息日息万五"
     "年化18%+分期真实年化13-15%+逾期上征信还清后展示5年[连三累六严重]"
     "+每年2次免费查征信+硬查询多影响评分+不外借不套现。"),
    ("kp_card_shebao",
     "五险一金（社保公积金）",
     "生活常识知识点内容（人话接口）", "生活常识",
     "五险一金快速理解：①**五险**——养老（累计缴满 15 年到龄领养老金，"
     "多缴多得）、医疗（报销门诊住院，断缴次月停报）、失业（缴费满 1 年"
     "非本人意愿失业可领失业金）、工伤（工作中受伤不分责任赔付）、生育"
     "（产检生产报销+生育津贴，多地已并入医疗）；②**一金=住房公积金**——"
     "单位和个人各缴一部分全归个人，用途：低利率公积金贷款买房（利率显著"
     "低于商贷）/租房提取/装修提取（部分地区）；③**缴费基数**——按上年度"
     "月均工资在上下限内核定，基数高缴得多未来待遇也高；④**断缴影响**——"
     "医疗断缴次月起不能报销（补缴后恢复），购房/落户/买车摇号等资格常与"
     "**连续**缴纳月数挂钩，换工作尽量无缝衔接；⑤**跨省转移**——养老和"
     "医保可跨省转移接续，缴费年限累计计算。",
     ["五险一金包括什么", "社保断缴有什么影响", "公积金有什么用",
      "养老金要交多少年", "医保断缴还能报销吗", "公积金贷款利率"],
     ["问商业保险对比", "问灵活就业参保"],
     "atomic", "",
     "五险一金=养老(满15年多缴多得)+医疗(断缴次月停报)+失业+工伤(不分"
     "责任)+生育(并入医疗)+公积金(个人单位共缴低息贷款/租房提取)+基数"
     "上下限+断缴影响购房落户连续资格+跨省转移年限累计。"),
]

QUESTIONS = [
    ("QB-965", "信用卡最低还款有什么后果？征信逾期记录多久能消除？",
     "生活常识", "技术直答",
     ["免息", "计息", "征信", "5年"], "通识拓展258"),
    ("QB-966", "五险一金包括什么？社保断缴有什么影响？公积金有什么用？",
     "生活常识", "技术直答",
     ["养老", "医疗", "断缴", "公积金"], "通识拓展258"),
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
                               "level:L2", "status:verified", "batch:通识拓展258"],
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
    bank["version"] = "v5.29"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
