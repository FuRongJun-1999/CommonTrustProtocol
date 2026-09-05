# -*- coding: utf-8 -*-
"""seed_common_203_cards.py · 通识拓展批次203知识卡+题库（幂等·两卡精批次）

203：地理学-回南天/生活常识-口苦的成因
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖（回南天与结露卡
[冬季窗内侧]季节场景划界）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_returnsouth",
     "回南天",
     "人文通识知识点内容（人话接口）", "地理学",
     "回南天=华南（广东/广西/福建/海南）**春季（2-4 月）**的特殊天气：冷空气"
     "撤退后，**暖湿空气**迅速回流，碰到**刚刚变冷的墙面、地板、镜子**（物体"
     "温度低于露点），水汽大量凝结——墙壁「冒水」、地板湿滑、衣物晾三天不干"
     "发馊。**反直觉要点：越开窗越潮**——正确应对=①**紧闭朝南/东南窗**（湿"
     "气来源方向），只在中午短暂开北窗透气；②**除湿机/空调除湿模式**为主力；"
     "③报纸/吸水垫铺地板、衣柜放除湿盒；④电器每天开机使用（发热驱潮防短路）。"
     "结束标志：冷空气再来气温下降。原理与冬季窗结露同源（暖湿气遇冷表面凝"
     "结），只是尺度更大、持续数天到两周。",
     ["回南天是什么", "回南天怎么防潮", "回南天为什么开窗更潮",
      "墙壁出水怎么办", "除湿机空调除湿", "回南天什么时候结束"],
     ["问结露原理（用结露卡）", "问梅雨季节（用梅雨卡）"],
     "atomic", "",
     "回南天=华南 2-4 月暖湿空气回流遇冷物体表面大量凝结（墙壁冒水地板滑衣物馊）；反直觉=紧闭朝南窗阻湿气、除湿机为主力（越开窗越潮）；电器每天开机驱潮防短路；冷空气再来即结束——与结露同源尺度更大。"),
    ("kp_card_bittermouth",
     "为什么会口苦",
     "生活常识知识点内容（人话接口）", "生活常识",
     "口苦的常见来源：①**晨起口苦**——睡眠中唾液少+细菌繁殖，多正常；②**口"
     "腔问题**——牙周炎/舌苔厚/干口（与口臭同源）；③**胆汁相关**——胆囊炎/"
     "胆结石/胆汁反流（胆汁味苦反流入口——常伴右上腹不适/饭后加重）；④**药物"
     "与饮食**——某些抗生素、维生素、咖啡浓茶遗留味；⑤持续严重的口苦伴**皮"
     "肤发黄（黄疸）**、右上腹痛——需查肝胆（B 超/肝功能）。**应对**：口腔清"
     "洁（刷牙+刷舌苔）、多喝水、规律作息；持续超过一周或伴上述症状就医。孕"
     "期激素变化也会口苦（常见且多暂性）。",
     ["为什么会口苦", "口苦是什么原因", "晨起口苦", "口苦和胆囊",
      "口苦要检查什么", "孕期口苦"],
     ["问口臭（用口臭卡）", "问胆囊炎症状（就医）"],
     "atomic", "",
     "口苦来源=晨起正常（唾液少菌多）+口腔问题（同口臭源）+胆汁反流（胆囊炎结石·伴右上腹痛）/药物遗留；持续超一周或伴黄疸右上腹痛→查肝胆（B 超/肝功能）；孕期激素性多暂性。"),
]

QUESTIONS = [
    ("QB-833", "「回南天」是怎么形成的？为什么说回南天越开窗通风反而越潮？", "地理学", "技术直答",
     ["暖湿", "回流", "凝结", "关窗", "朝南", "除湿"], "通识拓展203"),
    ("QB-834", "经常会口苦是什么原因？什么样的口苦需要去医院检查？", "生活常识", "技术直答",
     ["胆汁", "反流", "胆囊", "黄疸", "右上腹", "持续"], "通识拓展203"),
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
                               "level:L2", "status:verified", "batch:通识拓展203"],
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
                   "added": "2026-09-05"})
        added += 1
    bank["version"] = "v4.76"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
