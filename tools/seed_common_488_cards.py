# -*- coding: utf-8 -*-
"""seed_common_488_cards.py · 通识拓展批次488知识卡+题库（幂等）

488：3 张新卡·传统美食三连（粽子 kp_card_zongzi / 糖葫芦
    kp_card_tanghulu / 小笼包 kp_card_xiaolongbao）。
预检已过（QB-1699~1701 可用，三主题题库卡库双零）。
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
    ("kp_card_zongzi",
     "粽子",
     "传统美食知识点内容（人话接口）", "传统文化",
     "粽子——端午节的传统美食：①**是什么**——用粽叶（箬叶/芦苇叶）"
     "包裹糯米蒸煮而成，叶香渗入米中；②**南北之争**——北方甜粽（红枣"
     "豆沙蘸糖）vs 南方咸粽（鲜肉蛋黄火腿），「甜咸之争」是每年端午的"
     "保留话题；③**由来**——与纪念屈原相关：相传百姓投粽入江保护屈原"
     "遗体不被鱼虾啃食；④**衍生**——粽子的雏形是「角黍」，用菰叶包"
     "黍米，先秦已有；广东裹蒸粽、嘉兴肉粽、北方小枣粽各具风味；⑤**"
     "文化**——粽子与龙舟竞渡、挂艾草菖蒲共同构成端午习俗体系。",
     ["粽子的由来", "粽子为什么用粽叶包", "南方粽子北方粽子区别",
      "嘉兴粽子", "角黍是什么", "端午节习俗"],
     ["问屈原", "问龙舟竞渡"],
     "atomic", "",
     "粽子=粽叶包糯米蒸煮叶香渗米+北方甜粽红枣豆沙南方咸粽鲜肉蛋黄甜"
     "咸之争+纪念屈原投粽入江保护遗体传说+雏形角黍先秦已有广东嘉兴北"
     "方各具风味+与龙舟竞渡挂艾草构成端午习俗体系。"),
    ("kp_card_tanghulu",
     "冰糖葫芦",
     "传统美食知识点内容（人话接口）", "传统文化",
     "冰糖葫芦——酸甜可口的传统小吃：①**是什么**——山楂等水果串成串"
     "，裹上熬化的冰糖壳，红彤彤一串酸甜开胃；②**历史**——起源于宋代"
     "，一说与贵妃治病偏方有关（冰糖熬山楂），清代在北京街头盛行至今；"
     "③**熬糖是灵魂**——冰糖加水熬到「拔丝」火候（约 150℃ 左右），"
     "温度不够糖挂不住、过了发苦——全凭经验；④**原料**——传统用山"
     "楂（开胃消食），现在也有草莓/葡萄/山药豆/圣女果等花样；⑤**文化"
     "符号**——「都说冰糖葫芦儿酸」一首歌让它成为老北京年味的代表。",
     ["冰糖葫芦的由来", "糖葫芦的糖怎么熬", "山楂的功效",
      "老北京小吃", "糖葫芦做法", "冰糖葫芦历史"],
     ["问炒栗子", "问老北京小吃"],
     "atomic", "",
     "冰糖葫芦=山楂串裹熬化冰糖壳红彤彤酸甜开胃+起源宋代清代北京街头"
     "盛行+熬糖是灵魂约150度拔丝火候不够挂不住过头发苦全凭经验+传统山"
     "楂开胃消食现在草莓葡萄山药豆花样+一首歌成老北京年味符号。"),
    ("kp_card_xiaolongbao",
     "小笼包",
     "传统美食知识点内容（人话接口）", "传统文化",
     "小笼包——皮薄汁多的蒸制面点：①**特色**——皮薄馅大、汁水丰盈："
     "秘诀是「皮冻」——馅料里拌入熬冷的肉皮冻，蒸时皮冻化开成汤汁；"
     "②**起源**——源于北宋「山洞梅花包子」，现代小笼以上海南翔小笼"
     "包和南翔馒头店闻名（注意：灌汤包与小笼包是近亲但工艺不同）；"
     "③**吃法讲究**——「轻轻提，慢慢移，先开窗，后喝汤」——先咬小口"
     "吸汤再蘸姜丝香醋，防烫嘴；④**工艺**——面要半烫面（皮薄透亮不破"
     "），褶子细密（十八褶以上是老师傅手艺）；⑤**地位**——江南点心"
     "代表，入选多项非遗名录。",
     ["小笼包为什么有汤", "小笼包是哪里的特产", "灌汤包和小笼包",
      "小笼包怎么吃", "南翔小笼", "皮冻的做法"],
     ["问灌汤包", "问江南点心"],
     "atomic", "",
     "小笼包=皮薄馅大汁水丰盈秘诀皮冻蒸时化汤+源于北宋山洞梅花包子上"
     "海南翔闻名灌汤包近亲工艺不同+吃法轻轻提慢慢移先开窗后喝汤蘸姜丝"
     "香醋防烫+半烫面褶子细密十八褶老师傅+江南点心代表多项非遗。"),
]

QUESTIONS = [
    ("QB-1699", "粽子的南北差异是什么？端午吃粽子有什么由来？",
     "传统文化", "技术直答",
     ["粽子", "端午", "甜咸", "屈原"], "通识拓展488·存量卡补题"),
    ("QB-1700", "冰糖葫芦的糖是怎么熬的？它有什么历史？",
     "传统文化", "技术直答",
     ["糖葫芦", "山楂", "熬糖", "历史"], "通识拓展488·存量卡补题"),
    ("QB-1701", "小笼包为什么汤汁丰富？吃小笼包有什么讲究？",
     "传统文化", "技术直答",
     ["小笼包", "皮冻", "汤汁", "吃法"], "通识拓展488·存量卡补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展488"],
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
    bank["version"] = "v7.54"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
