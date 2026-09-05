# -*- coding: utf-8 -*-
"""seed_common_244_cards.py · 通识拓展批次244知识卡+题库（幂等）

244：物理-阿基米德原理（浮力定律）/地理-极昼极夜的成因
KCCS 四要素+题干原句触发词。预检已过（QB-923/924+双id可用）。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

WHITELIST = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
             "effect", "OR6A2", "ghrelin", "DOMS", "DHT", "frisson"}


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
    ("kp_card_archimedes2",
     "阿基米德原理（浮力定律）",
     "物理通识知识点内容（人话接口）", "基础科学",
     "阿基米德原理：①**定律内容**——浸在液体（或气体）中的物体受到向上的"
     "浮力，浮力大小等于物体**排开的液体所受的重力**（浮力=液体密度×g×排开"
     "体积，与物体自身密度/是否空心无关，只看排开多少液体）；②**传说背景**——"
     "国王怀疑金冠掺银，阿基米德泡澡时发现「排水量与体积对应」，兴奋裸奔喊"
     "「尤里卡」（我发现了）——纯金和掺银的皇冠重量相同但体积不同，排水"
     "量不同即可鉴别；③**浮沉判据**——物体密度<液体密度则漂浮（部分浸入，"
     "浮力=重力平衡），>则下沉（铁船能浮是因为船舱是空的，整体平均密度小于"
     "水），=则悬浮；④**应用**——排水量计算船舶载重/热气球（排开空气）/"
     "密度计/死海漂浮（盐水密度大）。",
     ["阿基米德原理是什么", "浮力大小等于什么", "浮力定律",
      "阿基米德鉴别皇冠", "铁船为什么能浮在水上", "死海为什么能漂浮"],
     ["问流体力学计算", "问船舶设计规范"],
     "atomic", "",
     "阿基米德原理=浮力=排开液体重(=液密度×g×排开体积,与自物密度无关)+"
     "皇冠传说(重量同体积异排水鉴别·尤里卡)+浮沉判据(密度小于液漂浮/铁船"
     "空心整体密度小)+应用船舶排水量热气球密度计死海。"),
    ("kp_card_polarday",
     "极昼极夜的成因",
     "地理通识知识点内容（人话接口）", "地理学",
     "极昼极夜的成因与规律：①**成因**——地轴倾斜约 23.5° 且倾斜方向恒指"
     "北极星附近——地球公转时，极圈内某些地区会出现太阳终日不落（极昼）或"
     "终日不出（极夜）；若地轴不倾斜，全球每天都昼夜平分；②**规律**——"
     "纬度越高极昼极夜越长：北极圈（66.5°N）上夏至日（6 月 22 日前后）恰"
     "好 1 天极昼，北极点极昼长达约半年；南极相反（12 月 22 日前后南极圈"
     "极昼）；③**对称性**——北半球夏至=北极极昼+南极极夜，冬至互换；春分"
     "秋分全球昼夜等长；④**极端体验**——中国境内漠河（约 53°N）无真正极昼"
     "但夏至「白夜」（天空不黑）；⑤**极圈内城市对策**——北欧夏季遮光窗帘+"
     "冬季补光治疗（缺乏日照影响情绪，季节性情感失调高发）。",
     ["极昼极夜是怎么形成的", "为什么极圈会有极昼", "北极夏至太阳落山吗",
      "极昼最长持续多久", "漠河有极昼吗", "地轴倾斜23.5度的影响"],
     ["问极地科考作息", "问黄赤交角天文测量"],
     "atomic", "",
     "极昼极夜=地轴倾斜23.5°恒定指向+公转→极圈内终日不落(昼)或不出(夜)+"
     "纬度越高越长(极圈1天/极点半年)+南北半球冬至夏至互换+漠河仅白夜+北欧"
     "冬季补光防情绪失调。"),
]

QUESTIONS = [
    ("QB-923", "阿基米德原理是什么？浮力大小等于什么？", "基础科学", "技术直答",
     ["排开", "浮力", "重力", "密度"], "通识拓展244"),
    ("QB-924", "极昼极夜是怎么形成的？极昼最长能持续多久？", "地理学", "技术直答",
     ["地轴", "倾斜", "极圈", "半年"], "通识拓展244"),
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
                               "level:L2", "status:verified", "batch:通识拓展244"],
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
    bank["version"] = "v5.15"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
