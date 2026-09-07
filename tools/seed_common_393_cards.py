# -*- coding: utf-8 -*-
"""seed_common_393_cards.py · 通识拓展批次393知识卡+题库（幂等）

393：2 张存量卡补题（中暑的处理与预防 kp_card_heatstroke /
    视疲劳的缓解 kp_card_eyefatigue2，均已在库）
    + 1 张新卡（密码与账户安全 kp_card_passwordsafe）。
KCCS 四要素+题干原句触发词。预检已过（QB-1417~1419 可用，
中暑/视疲劳题库 0 覆盖，密码安全题库卡库双零）。
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
             "MTBF", "SQA"}


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
    ("kp_card_passwordsafe",
     "密码与账户安全",
     "信息安全知识点内容（人话接口）", "生活常识",
     "密码与账户安全——数字生活的门锁：①**强密码三要素**——够长（12 位"
     "以上比复杂符号更有效）、不常见（别用生日/姓名拼音/123456）、唯一"
     "（重要账户一站一密，不重复使用）；②**密码管理**——记不住就用密码"
     "管理器；开启两步验证（短信/验证器），密码泄露了也多一道门；③**"
     "钓鱼防范**——不点陌生链接、不向「客服」透露验证码（验证码=第二把"
     "钥匙，谁要都不给）；④**泄露应对**——发现异常立即改密码、解绑支付"
     "方式、检查登录设备列表并踢掉陌生设备；⑤**公共场合**——免费公共"
     "网络不登录银行账户，公共电脑绝不勾选「记住密码」。",
     ["怎么设置强密码", "密码怎么管理", "两步验证是什么",
      "验证码能告诉别人吗", "账号被盗怎么办", "公共网络风险"],
     ["问手机防盗", "问防诈骗"],
     "atomic", "",
     "密码账户安全=强密码12位以上不常见一站一密+密码管理器加两步验证"
     "双保险+验证码是第二把钥匙谁要都不给+不点陌生链接防钓鱼+被盗立即"
     "改密解绑支付踢设备+公共网络不登录银行。"),
]

QUESTIONS = [
    ("QB-1417", "中暑了怎么处理？热射病为什么危险？",
     "健康与身体", "技术直答",
     ["中暑", "热射病", "降温", "急救"], "通识拓展393·存量卡补题"),
    ("QB-1418", "眼睛看屏幕久了疲劳怎么办？怎么科学用眼？",
     "健康与身体", "技术直答",
     ["视疲劳", "用眼", "干涩", "休息"], "通识拓展393·存量卡补题"),
    ("QB-1419", "怎么设置安全的密码？账号被盗了怎么办？",
     "生活常识", "技术直答",
     ["密码", "账户安全", "两步验证", "盗号"], "通识拓展393"),
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
                               "level:L2", "status:verified", "batch:通识拓展393"],
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
    bank["version"] = "v6.63"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
