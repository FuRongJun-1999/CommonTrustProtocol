# -*- coding: utf-8 -*-
"""seed_common_270_cards.py · 通识拓展批次270知识卡+题库（幂等）

270：安全-强密码与账号安全/安全-电信诈骗的识别与处置
KCCS 四要素+题干原句触发词。预检已过（QB-1026/1027+双id可用）。
注意：QB-606 已列常见网络诈骗类型，本批诈骗卡聚焦「处置流程」角度避让。
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
    ("kp_card_pwd",
     "强密码与账号安全",
     "生活常识知识点内容（人话接口）", "生活常识",
     "账号密码安全要点：①**强密码标准**——长度优先于复杂度：12 位以上优于"
     "8 位杂糅；大小写+数字+符号组合，避免生日/手机号/姓名拼音/键盘序列"
     "（键盘顺序键、123456 是黑客字典前几名）；②**一站一密**——多站复用同一"
     "密码是最大风险（一处泄露全线沦陷——撞库攻击），核心账号（支付/邮箱"
     "主号）必须独立密码；③**密码管理器**——用可靠的密码管理器生成+保管"
     "随机密码，人只记一个主密码；④**两步验证**——重要账号开启短信或动态"
     "验证码，密码泄露也有第二道门；⑤**泄露自查**——邮箱/手机号可在泄露"
     "查询服务检查是否已出现在泄露库，有则立即改密；⑥**恢复渠道**——"
     "绑定手机/邮箱保持有效，找回入口被抢注即失去账号。",
     ["怎么设置强密码", "密码怎么管理", "一个密码走天下行不行",
      "两步验证是什么", "密码泄露了怎么办", "撞库攻击"],
     ["问企业权限管理", "问生物识别安全"],
     "atomic", "",
     "强密码=长度优先12位+杂糅避生日键盘序列+一站一密防撞库+密码管理器"
     "只记主密码+重要账号两步验证+泄露库自查即改+恢复渠道保有效。"),
    ("kp_card_scam",
     "电信诈骗的识别与处置",
     "生活常识知识点内容（人话接口）", "生活常识",
     "遇到疑似电信诈骗怎么办：①**万能三问**——是否要求转账/垫付？是否"
     "要求共享屏幕、提供验证码？是否催促「马上办不许告诉别人」？三条任一"
     "命中即高度疑似诈骗；②**公检法不会电话办案**——所谓「涉案」「安全"
     "账户」「洗钱嫌疑」均为剧本，真公检法不设安全账户、不会要求转账自证"
     "清白；③**官方渠道反查**——挂断后用官方号码（银行"
     "不要求转账自证清白；③**官方渠道反查**——挂断后用官方号码（银行"
     "卡背面/95 客服/110）自行回拨核实，绝不使用对方提供的号码或链接；④"
     "**黄金止付**——已转账立即拨 110 或 96110 反诈专线报警，银行紧急"
     "止付越快追回概率越高；⑤**常见剧本特征**——刷单先给小额返利、"
     "「客服」主动退款理赔、网恋后引导投资（杀猪盘）、冒充领导熟人借钱"
     "——套路千变，最后一步永远是「转账」；⑥**国家反诈中心 App**——"
     "开启来电预警可拦截部分诈骗电话。",
     ["遇到电信诈骗怎么办", "被诈骗了钱还能追回吗",
      "96110是什么电话", "接到自称公检法的电话怎么办",
      "怎么识别诈骗电话", "国家反诈中心App"],
     ["问具体案卷判例", "问海外电诈园区"],
     "atomic", "",
     "电信诈骗处置=万能三问(要转账/要验证码共享屏/催促保密任一命中即疑)"
     "+公检法不电话办案无安全账户+官方渠道自行回拨核实+已转账立即110/"
     "96110黄金止付+剧本终局永远是转账+反诈App预警。"),
]

QUESTIONS = [
    ("QB-1026", "怎么设置强密码？一个密码走天下有什么风险？", "生活常识", "技术直答",
     ["强密码", "一站一密", "撞库", "两步验证"], "通识拓展270"),
    ("QB-1027", "接到自称公检法的电话要求转账怎么办？被骗后钱怎么追回？",
     "生活常识", "技术直答",
     ["公检法", "安全账户", "96110", "止付"], "通识拓展270"),
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
                               "level:L2", "status:verified", "batch:通识拓展270"],
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
    bank["version"] = "v5.41"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
