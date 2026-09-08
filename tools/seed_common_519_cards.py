# -*- coding: utf-8 -*-
"""seed_common_519_cards.py · 通识拓展批次519知识卡+题库（幂等）

519：2 张新卡·通信金融域（烽火与长城通信 kp_card_fengsui /
    镖局与票号 kp_card_biaoju——id 与语义等价卡名双重确认双零；
    科场案留待下批）。
预检已过（QB-1789~1791 可用）。
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
             "MTBF", "SQA", "IMC", "HMO", "JD", "STAR", "Word", "offer",
             "XMind", "HDR", "Robotaxi"}


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
    ("kp_card_fengsui",
     "烽火与长城通信",
     "军事史知识点内容（人话接口）", "历史与文明",
     "烽火与长城通信——没有电报时代的最快消息：①**烽燧制度**——白天"
     "燃烟称「燧」（俗称狼烟，传说狼粪烟直不易散，实际多为柴草加狼粪"
     "），夜间举火称「烽」；②**信号约定**——烽燧台上按敌人数量、方向"
     "规定举烽数目与组合，像一套「光学密码」，邻台依次接力，千里军情"
     "数时可达；③**经典典故**——周幽王烽火戏诸侯博褒姒一笑，终致犬戎"
     "攻破镐京（《史记》所载，钱穆等学者疑其为后世编造）；④**实证**"
     "——汉代河西走廊烽燧遗址密布，居延汉简出土《塞上烽火品约》，是"
     "当时的烽火操作规程；⑤**与长城一体**——烽燧沿长城与丝路分布，"
     "戍卒瞭望兼护邮路，是长城防御体系的神经末梢。",
     ["烽火台是干什么的", "狼烟是什么烟", "烽火戏诸侯",
      "烽燧", "长城怎么传递军情", "居延汉简"],
     ["问古代驿站", "问长城"],
     "atomic", "",
     "烽火长城通信=白天燃烟燧夜间举火烽狼烟传说狼粪烟直实多柴草+举烽"
     "数目组合如光学密码邻台接力千里数时可达+周幽王烽火戏诸侯史记载钱"
     "穆疑虚构+居延汉简塞上烽火品约实证操作规程+沿长城丝路是防御体系"
     "神经末梢。"),
    ("kp_card_biaoju",
     "镖局与票号",
     "经济史知识点内容（人话接口）", "历史与文明",
     "镖局与票号——旧中国的物流与金融：①**镖局**——武装护送机构：走"
     "镖护送银两贵重货物、看家护院、坐店守夜；镖车插镖旗，镖师佩刀械"
     "会武艺与江湖「春典」切口；②**走镖规矩**——「镖不喊沧」：沧州是"
     "武术之乡，过境不喊镖号以示敬意，免生切磋是非；③**票号**——山西"
     "平遥日升昌（1823 年创立，大掌柜雷履泰）首创异地汇兑：在甲地交银"
     "，持汇票到乙地支取，「一纸汇票汇通天下」；④**密押防伪**——汇票"
     "用诗句式暗号编码日期金额，专人书写加印章，防伪堪比密码学；⑤**"
     "兴衰**——晋商票号执全国金融牛耳近百年，清末银行兴起加之时局动"
     "荡而集体衰落——信用是票号的命根子，乱世信用最脆弱。",
     ["镖局是干什么的", "镖不喊沧", "日升昌", "票号怎么汇兑",
      "晋商", "汇通天下"],
     ["问漕运与盐政", "问李自成"],
     "atomic", "",
     "镖局票号=镖局武装护送走镖护院坐店镖旗春典切口+镖不喊沧沧州武术"
     "乡过境示敬+日升昌1823平遥雷履泰首创异地汇兑一纸汇票汇通天下+汇"
     "票诗句暗号密押防伪+晋商执金融牛耳近百年清末银行兴时局乱集体衰落"
     "信用是命根。"),
]

QUESTIONS = [
    ("QB-1789", "「狼烟」是什么烟？烽火台怎么传递军情？",
     "历史常识", "技术直答",
     ["狼烟", "烽火台", "烽燧", "军情"], "通识拓展519·新卡"),
    ("QB-1790", "镖局是做什么的？「镖不喊沧」是什么规矩？",
     "历史常识", "技术直答",
     ["镖局", "走镖", "镖不喊沧", "沧州"], "通识拓展519·新卡"),
    ("QB-1791", "票号是怎么汇兑银两的？「汇通天下」说的是哪家？",
     "历史常识", "技术直答",
     ["票号", "日升昌", "汇兑", "晋商"], "通识拓展519·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展519"],
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
    bank["version"] = "v7.84"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
