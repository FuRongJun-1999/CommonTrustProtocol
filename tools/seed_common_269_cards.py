# -*- coding: utf-8 -*-
"""seed_common_269_cards.py · 通识拓展批次269知识卡+题库（幂等）

269：生活-银行定期存款与利息/生活-汇率与换汇
KCCS 四要素+题干原句触发词。预检已过（QB-1024/1025+双id可用）。金融域延续。
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
             "CYP3A4", "ACID", "CNN", "RNN", "LSTM"}


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
    ("kp_card_deposit",
     "银行定期存款与利息",
     "生活常识知识点内容（人话接口）", "生活常识",
     "定期存款与利息常识：①**利息=本金×利率×期限**——年利率 2% 存 1 万一年"
     "到期利息 200 元（单利）；②**存款保险**——同一银行同一存款人本息 50 "
     "万元以内受《存款保险条例》全额保障（超出部分看银行经营状况），分散存"
     "大行更稳；③**提前支取按活期计息**——定期没到急用钱提前取，已存时间"
     "按活期利率（约 0.2%）算，利息大缩水——大额资金可拆几笔不同期限存；"
     "④**自动转存**——到期不取约转下期，按**转存日**新利率执行；⑤**利率"
     "下行环境**——长期限存款利率趋降，锁定利率与流动性需求要平衡；⑥**警惕"
     "「存款变保险/理财」**——银行网点推销的分红险/结构性存款不等于存款，"
     "收益不保证，签字前看清产品性质。",
     ["定期存款利息怎么算", "存款保险保多少", "定期提前支取利息",
      "自动转存是什么", "存款和理财的区别", "50万存款保险"],
     ["问大额存单细节", "问结构性存款机制"],
     "atomic", "",
     "定期利息=本金×利率×期限(单利)+存款保险同行同人50万内全额保障+提前"
     "支取按活期约0.2%大缩水(可拆单)+自动转存按转存日新利率+利率下行锁定"
     "与流动性平衡+警惕存款变保险理财(签字看清性质)。"),
    ("kp_card_fx",
     "汇率与换汇",
     "生活常识知识点内容（人话接口）", "生活常识",
     "汇率换汇常识：①**汇率是什么**——两种货币的兑换比价，人民币对美元 "
     "7.2 意思是 7.2 元换 1 美元；汇率贬值=本币购买力对外下降（进口商品"
     "变贵、出境游成本升）；②**买入价卖出价**——银行报价有差价（点差），"
     "换汇时银行低价收你高价卖你，点差是换汇成本，货比三家；③**额度**——"
     "个人每年 5 万美元便利化购汇额度（超额需材料申报用途）；④**现钞现汇**"
     "——现汇（账户数字）比现钞（纸币）点差小，跨境汇款优先现汇；⑤**时机**"
     "——短期波动难预测，刚需（留学缴费）分批换平摊成本优于赌方向；⑥"
     "**合规红线**——不得出借额度帮他人换汇（「蚂蚁搬家」式拆分购汇违法），"
     "地下钱庄换汇有法律与资金双风险。",
     ["汇率是什么意思", "人民币贬值有什么影响", "换汇额度是多少",
      "现汇和现钞的区别", "什么时候换外汇划算", "私人换汇违法吗"],
     ["问外汇投资渠道", "问跨境汇款手续费"],
     "atomic", "",
     "汇率=两币兑换比价(贬值=进口贵出境贵)+银行点差是成本货比三家+个人年"
     "5万美元便利化额度+现汇点差小于现钞优先汇款+刚需分批换平摊优于赌方向"
     "+不出借额度不找地下钱庄。"),
]

QUESTIONS = [
    ("QB-1024", "定期存款利息怎么算？提前支取会怎样？存款保险保多少？",
     "生活常识", "技术直答",
     ["利息", "活期", "50万", "保险"], "通识拓展269"),
    ("QB-1025", "汇率是什么？个人换汇有什么额度限制？现汇和现钞有什么区别？",
     "生活常识", "技术直答",
     ["汇率", "5万", "额度", "现汇"], "通识拓展269"),
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
                               "level:L2", "status:verified", "batch:通识拓展269"],
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
    bank["version"] = "v5.40"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
