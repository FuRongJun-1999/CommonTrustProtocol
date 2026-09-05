# -*- coding: utf-8 -*-
"""seed_common_223_cards.py · 通识拓展批次223知识卡+题库（幂等·三卡精批次）

223：生物学-左撇子/地理学-海为什么是咸的/语言学-口音的成因
KCCS 四要素+题干原句触发词。三重预检：三主题双库零覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_lefthander",
     "左撇子",
     "基础科学知识点内容（人话接口）", "生物学",
     "左撇子（左利手）约占人口 **10%**：①**成因**——与大脑偏侧化相关（右脑"
     "控制左手），遗传有影响（左撇子父母孩子左撇子概率更高）但**具体机制尚未"
     "完全明确**——胎儿期的发育因素也有参与；②**不是病**，历史上左撇子曾被"
     "强迫「矫正」用右手（导致口吃/书写困难等副作用，现已不提倡）；③**左撇"
     "子的优势领域**——对抗性运动（击剑/拳击/乒乓球：对手习惯面对右利手，"
     "左撇子打法罕见难适应）；④**现实困扰**——剪刀/课桌/开门/圆珠笔多为右"
     "利手设计（左撇子写字易蹭花）；⑤左撇子与右撇子的智商无差异——「左撇"
     "子更聪明」是以偏概全。",
     ["左撇子是怎么回事", "左撇子更聪明吗", "左撇子比例",
      "左撇子要矫正吗", "左撇子运动员优势"],
     ["问大脑偏侧化", "问手性用品"],
     "atomic", "",
     "左撇子约占 10%：与大脑偏侧化相关遗传有影响但机制未完全明确；不是病勿强行矫正（副作用口吃书写困难）；优势领域=对抗性运动（对手不适应）；现实困扰=工具多为右利手设计；智商与右撇子无差异。"),
    ("kp_card_seasalt",
     "海为什么是咸的",
     "基础科学知识点内容（人话接口）", "地理学",
     "海水咸=**亿万年的盐分积累**：①**盐的来源**——岩石风化：雨水（含微量"
     "碳酸）冲刷岩石，溶解出钠、氯等矿物盐，经河流源源不断**汇入海洋**；海"
     "底火山与热液喷口也直接输送矿物质；②**为什么越来越咸**——水可以通过蒸"
     "发离开海洋（形成降雨），但**盐分留下来**——几十亿年的「只进不出」积累"
     "到现在约 **3.5% 的盐度**（每公斤海水约含 35 克盐）；③**动态平衡**——"
     "沉积、海底矿物反应也在移除盐分，海水盐度已趋于稳定；④**死海**是内流"
     "湖：只进不出蒸发极强，盐度约 30%——人可以轻松漂浮（但不是「海」）。",
     ["海为什么是咸的", "海水盐分从哪来", "死海为什么能漂浮",
      "海水盐度", "河流为什么不咸"],
     ["问水循环（用结露卡划界）", "问盐与健康"],
     "atomic", "",
     "海咸=岩石风化盐分经河流亿万年汇入+海底火山输送：水蒸发出去盐留下积累到 3.5% 盐度趋于平衡；死海是内流湖蒸发极强盐度约 30% 人可漂浮——不是海；河水不断更新所以不咸。"),
    ("kp_card_accent",
     "口音的成因",
     "基础科学知识点内容（人话接口）", "语言学",
     "口音=**语言习得关键期**留下的「发声肌肉记忆」：①**关键期**——12 岁前"
     "（尤其 7 岁前）是语音习得黄金期，此时大脑可塑性强，能精确分辨并模仿任"
     "何语言的音素；②**成年后学外语为什么有口音**——母语的发声习惯（口型/"
     "舌位/声调）已定型，母语中没有的音（如英语 th 咬舌音对中文使用者）难以"
     "精确发出；③**口音可以改善**——大量听说训练+刻意练习可接近母语水平（"
     "但几乎无法 100% 消除）；④**方言口音同理**——移居地多年的口音变化是发"
     "声习惯的缓慢重塑；⑤口音不是缺陷——它是身份与成长环境的印记，语言学的"
     "态度是「所有口音都平等」。",
     ["口音是怎么形成的", "为什么成年学外语有口音", "语言习得关键期",
      "口音可以改吗", "方言口音的形成"],
     ["问方言与普通话", "问外语学习方法"],
     "atomic", "",
     "口音=语言习得关键期（12 岁前尤其 7 岁前）定型的发声肌肉记忆：母语没有的音成年后难以精确发出；口音可大量听说训练改善但难 100% 消除；方言口音同理=发声习惯缓慢重塑；口音是身份印记语言学态度是所有口音平等。"),
]

QUESTIONS = [
    ("QB-869", "左撇子约占人口的比例是多少？左撇子应该被强行矫正吗？", "生物学", "技术直答",
     ["10%", "百分之十", "大脑", "偏侧化", "不提倡", "矫正"], "通识拓展223"),
    ("QB-870", "海水为什么是咸的？盐分是怎么来的？", "地理学", "技术直答",
     ["岩石风化", "河流", "汇入", "亿万年", "积累", "蒸发"], "通识拓展223"),
    ("QB-871", "为什么成年后学外语很难去掉口音？口音是怎么形成的？", "语言学", "技术直答",
     ["关键期", "12岁", "发声", "肌肉记忆", "母语"], "通识拓展223"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{6,}", content):
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
                               "level:L2", "status:verified", "batch:通识拓展223"],
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
    bank["version"] = "v4.94"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
