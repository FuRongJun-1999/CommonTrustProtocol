# -*- coding: utf-8 -*-
"""seed_common_256_cards.py · 通识拓展批次256知识卡+题库（幂等）

256：文化-围棋的基本规则与气/益智-魔方的结构与复原
KCCS 四要素+题干原句触发词。预检已过（QB-959/960+双id可用）。
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
    ("kp_card_weiqi",
     "围棋的基本规则与气",
     "文化通识知识点内容（人话接口）", "文化",
     "围棋入门核心概念：①**棋盘与目标**——19 路纵横线交点共 361 个落子点，"
     "黑白轮流落子，目标是**围地**（终局占地多者胜，黑先行需贴目补偿白棋"
     "约 7.5 目）；②**气的概念（核心）**——棋子在纵横线上紧邻的空点叫"
     "「气」，一块棋的气被对方全部占满就会被「提」离棋盘（吃子）；③**禁"
     "着与打劫**——自杀点不可落；刚被提一子不能立即回提（打劫规则，须先"
     "在别处落一手找「劫材」），防止无限循环；④**眼与活棋**——一块棋拥有"
     "两个真眼（对方无法同时填死的内部空间）即无法被杀；⑤**地位**——起源"
     "中国传说尧造围棋教子，日语囲碁/英语 Go；状态数超宇宙原子数（约 10^170"
     "量级），2016 年 AlphaGo 4:1 胜李世石、2017 年胜柯洁，成为 AI 里程碑；"
     "⑥段位体系——业余级位→业余段位→职业初段至九段。",
     ["围棋怎么下", "围棋的气是什么", "围棋怎么算赢", "打劫是什么",
      "什么是活棋真眼", "AlphaGo战胜李世石"],
     ["问中盘战术", "问定式记忆"],
     "atomic", "",
     "围棋=19路361点围地多者胜(黑贴7.5目)+气=纵横紧邻空点被占满即提子+"
     "打劫禁立即回提防循环+两真眼活棋+状态数10^170超宇宙原子+2016"
     "AlphaGo胜李世石AI里程碑。"),
    ("kp_card_cube3",
     "魔方的结构与复原",
     "益智通识知识点内容（人话接口）", "生活常识",
     "三阶魔方常识：①**状态数惊人**——约 4325 亿亿种（4.3×10^19），但任意"
     "状态最少 20 步内必可复原（「上帝之数」=20，2010 年借助计算机穷举"
     "证明）；②**结构真相=中心块定色**——六个中心块相对位置永远不变"
     "（白对黄、红对橙、蓝对绿），魔方「转动」的只是棱块（12 个）与角块"
     "（8 个），看中心块就知道哪面该是什么色；③**复原思路（层先法入门）**"
     "——底面十字→底角→中层棱→顶面十字→顶面朝向→顶层角棱归位，七八个"
     "公式分步解决，新手 2-3 分钟能复原；④**竞速**——CFOP 法（公式 119 个）"
     "高手 10 秒内复原，世界纪录 3 秒级；⑤**奇偶陷阱**——只把一个棱块"
     "「翻方向」或单换两块角是不可能的（受群论约束），暴力拆装装错方向"
     "会导致「永远差一步」复原不了。",
     ["魔方有多少种变化", "魔方怎么复原", "上帝之数是什么",
      "魔方中心块能动吗", "层先法", "魔方拆了装回去为什么复原不了"],
     ["问高阶魔方", "问盲拧技巧"],
     "atomic", "",
     "魔方=4.3×10^19状态+任意状态≤20步可复原(上帝之数2010证明)+六中心块"
     "相对位置恒定定色+12棱8角转动+层先法入门CFOP竞速+单翻一棱/单换两角"
     "不可能(群论约束)拆装错方向永不复原。"),
]

QUESTIONS = [
    ("QB-959", "围棋的「气」是什么？怎么算输赢？", "文化", "技术直答",
     ["气", "提子", "围地", "贴目"], "通识拓展256"),
    ("QB-960", "魔方有多少种变化状态？为什么拆开乱装可能复原不了？",
     "生活常识", "技术直答",
     ["状态", "20步", "中心块", "棱块"], "通识拓展256"),
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
                               "level:L2", "status:verified", "batch:通识拓展256"],
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
    bank["version"] = "v5.27"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
