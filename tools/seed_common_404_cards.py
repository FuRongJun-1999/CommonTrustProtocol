# -*- coding: utf-8 -*-
"""seed_common_404_cards.py · 通识拓展批次404知识卡+题库（幂等）

404：2 张新卡（数独 kp_card_sudoku / 摄影入门 kp_card_photography）
    + 1 张存量卡补题（珠穆朗玛峰 kp_card_qomolangma，已在库）。
KCCS 四要素+题干原句触发词。预检已过（QB-1450~1452 可用，
数独/摄影/珠峰角度题库 0 覆盖，卡库无同名卡）。
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
             "MTBF", "SQA", "IMC", "HMO"}


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
    ("kp_card_sudoku",
     "数独",
     "益智游戏知识点内容（人话接口）", "文化娱乐",
     "数独——纯逻辑的数字填图游戏：①**规则**——9×9 棋盘分成九个 3×3"
     "小宫，要求每行、每列、每个小宫里数字 1-9 各出现一次；开局给若干"
     "提示数，全部填满且不重复即完成；②**来源**——规则雏形是欧拉的"
     "「拉丁方块」，现代数独 1979 年在美国刊出，后经日本出版社命名"
     "「数独」（意为「只出现一次的数字」）风靡全球；③**常用解法**——"
     "排除法（某格候选数被行列宫排到只剩一个）、唯一候选法；好题的"
     "标准是**有且只有一个解**；④**难度差异**——不在空格多少，而在"
     "解法链条的深度（高级技巧需要多步假设）；⑤**价值**——纯逻辑"
     "推理训练，不需要任何知识背景，老少皆宜。",
     ["数独的规则", "数独是怎么来的", "数独怎么入门",
      "数独解题技巧", "数独唯一解", "九宫格游戏"],
     ["问魔方", "问拼图"],
     "atomic", "",
     "数独=9×9每行列宫1到9不重复+拉丁方块雏形1979美国刊出日本命名风"
     "靡+排除法唯一候选法入门+好题有且只有一个解+难度在解法链深度+"
     "纯逻辑推理老少皆宜。"),
    ("kp_card_photography",
     "摄影入门",
     "生活技能知识点内容（人话接口）", "生活常识",
     "摄影入门——从「随手拍」到「有意识拍」：①**曝光三要素**——光圈"
     "（进光孔大小：越大进光越多、背景越虚化）、快门速度（曝光时间："
     "越快越能凝固运动）、感光度（对光越敏感噪点越多）——三者互相"
     "补偿共同决定明暗；②**构图**——三分法（主体放在井字线交叉点）、"
     "对称构图、引导线构图（用路/河把视线引向主体）；③**光线**——"
     "日出后与日落前一小时的「黄金时段」光线柔和色彩暖，正午顶光硬"
     "（拍人易出阴影）；④**手机摄影**——HDR 模式多帧合成兼顾明暗、"
     "人像模式模拟背景虚化、逆光对焦拉亮度；⑤**心法**——先想「拍什"
     "么、突出什么」再按快门，多拍选优。",
     ["摄影曝光三要素", "光圈快门感光度", "摄影构图技巧",
      "什么是黄金时段", "手机HDR是什么", "摄影入门"],
     ["问视频剪辑", "问修图"],
     "atomic", "",
     "摄影=曝光三要素光圈快门感光度互相补偿+光圈大背景虚快门快凝固动"
     "ISO高噪点多+三分法对称引导线构图+日出日落黄金时段光柔和+手机HDR"
     "多帧合成人像模式虚化+先想拍什么多拍选优。"),
]

QUESTIONS = [
    ("QB-1450", "数独的规则是什么？怎么入门数独？",
     "文化娱乐", "技术直答",
     ["数独", "规则", "九宫格", "推理"], "通识拓展404"),
    ("QB-1451", "摄影的曝光三要素是什么？怎么构图好看？",
     "生活常识", "技术直答",
     ["摄影", "曝光", "光圈", "构图"], "通识拓展404"),
    ("QB-1452", "珠穆朗玛峰有多高？为什么说它还在长高？",
     "地理常识", "技术直答",
     ["珠穆朗玛", "8848", "长高", "板块"], "通识拓展404·存量卡补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展404"],
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
    bank["version"] = "v6.74"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
