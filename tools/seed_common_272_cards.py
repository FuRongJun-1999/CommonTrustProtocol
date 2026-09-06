# -*- coding: utf-8 -*-
"""seed_common_272_cards.py · 通识拓展批次272知识卡+题库（幂等）

272：物理-风筝为什么能飞/物理-陀螺为什么转着不倒（玩具物理新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1034/1035+双id可用）。
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
             "FADH2"}


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
    ("kp_card_kite",
     "风筝为什么能飞",
     "物理通识知识点内容（人话接口）", "基础科学",
     "风筝飞行的受力原理：①**升力来源**——风撞上倾斜的筝面：迎角使风筝下方"
     "气流受阻压强增大、上方流速快压强小——上下压差把风筝往上推（与飞机"
     "机翼同理的升力）；②**三力平衡**——升力（垂直筝面向上）+重力（向下）"
     "+线的拉力（沿线下斜），三力平衡时风筝稳定悬停；③**角度关键**——"
     "迎角太小升力不足栽头、迎角太大阻力剧增翻滚——提线（拴结点位置）决定"
     "筝面自动保持最佳迎角（自稳设计）；④**为什么要有尾巴**——长尾/飘带"
     "提供空气阻尼与配重，抑制筝面左右摇摆与打转（像船尾的稳定舵）；⑤"
     "**放线收线的门道**——风大时放线升更高，风小时快速收线增加相对风速"
     "拉起升力——收放的本质是控制空速；⑥**为何逆风放**——逆风跑动迅速"
     "建立相对风速，风筝才能「吃住」风起飞。",
     ["风筝为什么能飞", "风筝的原理", "风筝为什么要装尾巴",
      "风筝怎么放起来", "风筝迎角", "风筝受力分析"],
     ["问运动风筝特技", "问风筝历史民俗"],
     "atomic", "",
     "风筝=倾斜筝面迎角产生上下压差升力(机翼同理)+升力重力拉力三力平衡"
     "+提线自动保持最佳迎角自稳+尾巴阻尼配重防摇摆+收线加相对风速拉升"
     "+逆风放吃住风。"),
    ("kp_card_top",
     "陀螺为什么转着不倒",
     "物理通识知识点内容（人话接口）", "基础科学",
     "陀螺的定轴性与进动：①**定轴性（角动量守恒）**——高速旋转的物体有一"
     "股「倔劲」：角动量方向很难被外力改变——旋转越快越稳，这就是转着的"
     "陀螺不倒、自行车轮转起来更稳、子弹旋转飞行更准的共同原理；②**不倒的"
     "本质**——静止的陀螺受重力力矩一推就歪倒；旋转的陀螺重力矩不把它"
     "「按倒」，而是让它绕竖直轴慢悠悠打转——**进动**（自转轴绕另一轴的"
     "缓慢回旋）；③**转速衰减**——摩擦消耗能量转速下降，角动量小了压不住"
     "重力矩，进动圈变大晃动加剧最终倒下——倒下前的「醉步」；④**应用**——"
     "机械陀螺仪（飞机/导弹/舰船的姿态基准，转得越快指向越稳）、手机里的"
     "微型陀螺仪（感知旋转翻转屏幕）、陀螺稳定器（摄影云台）；⑤**指尖"
     "陀螺/空竹/悠悠球**——同一物理内核的玩具化。",
     ["陀螺为什么转着不倒", "陀螺原理", "什么是进动",
      "自行车骑起来为什么不倒", "陀螺仪是什么", "角动量守恒"],
     ["问傅科陀螺实验", "问微型陀螺工艺"],
     "atomic", "",
     "陀螺=高速旋转角动量定轴性难被外力改向(转快越稳)+重力矩不按倒而是"
     "引发进动(自转轴缓回旋)+转速摩擦衰减角动量压不住重力矩终倒+应用"
     "机械陀螺仪姿态基准/微型手机陀螺/云台稳定。"),
]

QUESTIONS = [
    ("QB-1034", "风筝为什么能飞起来？风筝的尾巴有什么用？", "基础科学", "技术直答",
     ["升力", "迎角", "平衡", "尾巴"], "通识拓展272"),
    ("QB-1035", "陀螺为什么转着的时候不倒？什么是进动？", "基础科学", "技术直答",
     ["角动量", "定轴", "进动", "转速"], "通识拓展272"),
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
                               "level:L2", "status:verified", "batch:通识拓展272"],
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
    bank["version"] = "v5.43"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
