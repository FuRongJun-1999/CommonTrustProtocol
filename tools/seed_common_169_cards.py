# -*- coding: utf-8 -*-
"""seed_common_169_cards.py · 通识拓展批次169知识卡+题库（幂等·两卡精批次）

169：生活常识-晒被子的正确方式/生活常识-口腔溃疡
KCCS 四要素+题干原句触发词。三重预检：晒被子/口腔溃疡双库零覆盖（勾股定理
命中已有覆盖弃选）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_sunquilt",
     "晒被子的正确方式",
     "生活常识知识点内容（人话接口）", "生活常识",
     "晒被子要点：①**为什么晒**——阳光中紫外线杀菌除螨（螨虫怕干燥高温），"
     "被窝的「太阳味」其实是轻微氧化产物的气味（不是螨虫尸体的味道——谣言）；"
     "②**分材质**：棉被可中午前后晒 **2-3 小时**；羊毛/蚕丝被**忌暴晒**（蛋白"
     "纤维高温脆化褪色，宜阴干或晨光晒 1 小时）；化纤被轻晒即可；羽绒被忌晒"
     "（晾通风处）；③**时间**——上午 10 点到下午 2-3 点最干爽，**傍晚收回**"
     "（夜间湿气回潮白晒）；④**「用力拍打更蓬松」是误区**——拍断纤维、粉尘"
     "螨虫排泄物扬起致过敏——用**床刷轻扫**或晾后自然蓬松；⑤收被前**轻拍抖"
     "落**表面浮尘，套被罩更卫生。频率：潮湿季两周一次、干燥季一月一次足够。",
     ["被子怎么晒", "晒被子要晒多久", "蚕丝被能晒吗", "拍打被子对不对",
      "太阳味是什么", "被子多久晒一次"],
     ["问除螨仪效果", "问被子选购材质"],
     "atomic", "",
     "晒被=紫外线杀菌除螨（太阳味=氧化产物非螨虫尸）；分材质=棉被午晒 2-3h/羊毛蚕丝忌暴晒宜阴干/羽绒晾通风；10-15 点最干爽傍晚收回；用力拍打=断纤扬尘致敏误区用床刷轻扫；潮湿季两周一次。"),
    ("kp_card_ulcer",
     "口腔溃疡",
     "生活常识知识点内容（人话接口）", "生活常识",
     "口腔溃疡（复发性阿弗他溃疡）=口腔黏膜小而痛的圆形溃烂：①**特点**——「"
     "黄红凹痛」（黄假膜/红晕/中央凹陷/剧痛），**自限性**：一般 1-2 周**自行愈"
     "合**不留疤；②**诱因**——压力熬夜免疫力波动、维生素B族与维生素C/锌/铁缺"
     "乏、机械创伤（咬伤/过硬食物/牙套磨蹭）、辛辣刺激；③**缓解**——淡盐水或"
     "漱口水漱口保持清洁、西瓜霜/口腔溃疡贴/凝胶隔离保护创面、多吃蔬果补维生"
     "素、避免辛辣烫硬食物；④**就医信号**（警惕「不好的溃疡」）：同一处**超过"
     "2 周不愈**、溃疡大而深呈菜花样、伴反复发热/眼部炎症/生殖器溃疡（排查白"
     "塞病）、无痛性快速增大（排查口腔癌——长期吸烟嚼槟榔者高风险）。",
     ["口腔溃疡怎么办", "口腔溃疡多久能好", "为什么会反复口腔溃疡",
      "口腔溃疡贴有用吗", "口腔溃疡长期不愈", "白塞病"],
     ["问牙膏选择", "问牙龈出血原因"],
     "atomic", "",
     "口腔溃疡=黄红凹痛自限性 1-2 周自愈；诱因=压力免疫/维生素BC锌铁缺乏/创伤；缓解=淡盐水漱口+溃疡贴凝胶+补蔬果忌辛辣；警觉=同一处超 2 周不愈/菜花样/伴眼生殖器炎症（白塞病）/无痛增大（烟酒槟榔者查口腔癌）。"),
]

QUESTIONS = [
    ("QB-759", "晒被子有什么作用？为什么说蚕丝被和羊毛被不能暴晒？", "生活常识", "技术直答",
     ["紫外线", "杀菌", "除螨", "纤维", "阴干", "脆化"], "通识拓展169"),
    ("QB-760", "口腔溃疡一般多久能自愈？出现哪些情况需要就医检查？", "生活常识", "技术直答",
     ["1-2周", "自愈", "2周不愈", "白塞", "就医"], "通识拓展169"),
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
                               "level:L2", "status:verified", "batch:通识拓展169"],
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
    bank["version"] = "v4.42"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
