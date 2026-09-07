# -*- coding: utf-8 -*-
"""seed_common_377_cards.py · 通识拓展批次377知识卡+题库（幂等）

377：3 张新卡（蝴蝶完全变态发育/交子纸币起源/古筝）+ 3 题（QB-1369~1371）。
KCCS 四要素+题干原句触发词。预检已过（QB-1369~1371 可用，三主题
题库 0 覆盖，卡库无同名卡）。
（本批次号曾被困倦睡眠重复题占用，2026-09-07 重写为真实新题。）
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
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO"}


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
    ("kp_card_butterfly",
     "蝴蝶的完全变态发育",
     "昆虫常识知识点内容（人话接口）", "自然与生物",
     "蝴蝶的一生——完全变态发育四阶段：①**卵**——雌蝶把卵产在寄主植物"
     "（幼虫将来的食物）叶背上；②**幼虫**——孵化出来就是「毛毛虫」，"
     "任务就是吃（多为啃食植物叶片）和长大，几次蜕皮；③**蛹**——末龄"
     "幼虫吐丝做蛹台化蛹，蛹期内幼虫身体组织大部分溶解重组，改建为成虫"
     "器官（翅膀/长口器/生殖器官）——「里外换新」；④**成虫**——破蛹"
     "而出，翅膀展开变硬后飞行，改吸食花蜜/果汁（口器从咀嚼式变成虹吸式"
     "的「卷起的吸管」）。完全变态 = 幼虫与成虫形态、食性、生活方式完全"
     "不同；对比不完全变态（如蝗虫：卵→若虫→成虫，无蛹期，若虫像缩小版"
     "成虫）。",
     ["毛毛虫怎么变成蝴蝶", "完全变态发育是什么", "蝴蝶的一生四个阶段",
      "蛹里面发生了什么", "不完全变态和完全变态区别", "蝴蝶吃什么"],
     ["问蚕的生命周期", "问蝗虫"],
     "atomic", "",
     "蝴蝶完全变态发育=卵幼虫蛹成虫四阶段+幼虫毛毛虫啃叶吃和长大+蛹内"
     "组织溶解重组成成虫器官+成虫口器变虹吸式吸花蜜+幼虫成虫形态食性完"
     "全不同+对比不完全变态如蝗虫无蛹期若虫像小成虫。"),
    ("kp_card_jiaozi",
     "交子（世界最早的纸币）",
     "货币史知识点内容（人话接口）", "历史与文明",
     "交子——世界上最早的纸币，诞生于北宋四川：①**为什么诞生**——四川"
     "通行铁钱，太重（买一匹布要背几十斤铁钱），大额交易极不方便；②**"
     "民间起源**——成都商户先自发发行「交子铺」开具的存款凭证，可兑现"
     "可流通，成了事实上的纸币；③**官办定型**——北宋天圣元年（1023 年）"
     "朝廷设「益州交子务」，发行官方交子，有界（分期发行）有准备金；"
     "④**世界意义**——比欧洲最早的纸币（1661 年瑞典）早六百多年；⑤**"
     "后续教训**——宋金元各代都发纸币，但战争财政压力下滥发导致贬值"
     "（元代交钞恶性通胀），说明纸币信用必须有约束。",
     ["世界上最早的纸币是什么", "交子是哪个朝代发明的", "交子为什么出现在四川",
      "纸币是怎么来的", "益州交子务", "纸币的历史"],
     ["问会子", "问元代交钞"],
     "atomic", "",
     "交子=世界最早纸币北宋四川诞生+铁钱太重大额交易不便催生+成都商户"
     "交子铺存款凭证民间起源+1023年益州交子务官办发行有界有准备金+比"
     "瑞典1661年早六百多年+滥发导致贬值纸币信用需约束。"),
    ("kp_card_guzheng",
     "古筝",
     "传统乐器知识点内容（人话接口）", "传统文化",
     "古筝——中国传统弹拨乐器：①**来历**——因战国时代在秦国流行又称"
     "「秦筝」，两千五百年以上历史；②**形制**——长条形木质共鸣箱，"
     "弦下有可移动的「雁柱」（码子）支撑定音，现代标准 21 弦（传统 13/16"
     " 弦），五声音阶定弦（宫商角徵羽，一弦多音靠按弦变音）；③**技法**——"
     "右手托劈勾剔摇指刮奏负责发声，左手揉按滑颤「以韵补声」——古筝的"
     "「韵味」主要在左手按滑；④**名曲**——《渔舟唱晚》《高山流水》《"
     "汉宫秋月》《寒鸦戏水》；⑤**辨析**——古筝与古琴不同：筝 21 弦有"
     "雁柱、音色明亮，琴 7 弦无柱、音色低沉内敛，「琴棋书画」里的琴指"
     "古琴不是筝。",
     ["古筝有多少根弦", "古筝和古琴的区别", "古筝名曲有哪些",
      "秦筝是什么", "雁柱是什么", "古筝怎么发韵"],
     ["问琵琶", "问二胡"],
     "atomic", "",
     "古筝=战国秦地流行称秦筝两千五百年+木共鸣箱雁柱支撑现代标准21弦"
     "五声音阶定弦+右手托劈勾剔摇指左手揉按滑颤以韵补声+名曲渔舟唱晚高"
     "山流水汉宫秋月+与古琴区别筝21弦有柱音亮琴7弦无柱音沉琴棋书画指"
     "古琴。"),
]

QUESTIONS = [
    ("QB-1369", "毛毛虫是怎么变成蝴蝶的？蛹里面发生了什么？",
     "自然与生物", "技术直答",
     ["蝴蝶", "毛毛虫", "蛹", "变态发育"], "通识拓展377"),
    ("QB-1370", "世界上最早的纸币是什么？它是怎么诞生的？",
     "历史与文明", "技术直答",
     ["交子", "纸币", "北宋", "四川"], "通识拓展377"),
    ("QB-1371", "古筝有多少根弦？它和古琴有什么区别？",
     "传统文化", "技术直答",
     ["古筝", "弦", "古琴", "雁柱"], "通识拓展377"),
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
                               "level:L2", "status:verified", "batch:通识拓展377"],
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
    bank["version"] = "v6.47"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
