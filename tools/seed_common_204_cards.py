# -*- coding: utf-8 -*-
"""seed_common_204_cards.py · 通识拓展批次204知识卡+题库（幂等·两卡精批次）

204：生活常识-正确剪趾甲防嵌甲/生活常识-头皮屑与去屑
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_ingrownnail",
     "正确剪趾甲防嵌甲",
     "生活常识知识点内容（人话接口）", "生活常识",
     "嵌甲=趾甲边缘**长进旁边肉里**（大脚趾最常见），红肿疼痛甚至化脓——主因"
     "是**剪法错误+鞋太紧**。**正确剪法**：①**平剪**——趾甲剪成平的，前端保"
     "留一点长度盖住趾尖（**勿剪成弧形/圆角**，勿往两侧角落深挖剪）；②长度="
     "趾甲尖端与趾尖平齐或略长 1-2mm；③工具干净、脚干燥时剪。**已嵌甲处理**"
     "：轻度=垫小棉条引导趾甲长出、温水泡脚软化；化脓/肉芽增生=就医（拔甲或"
     "矫正，勿去不消毒的修脚店——工具共用可传染真菌/病毒）。**预防**：鞋头宽"
     "松（尖头高跟鞋是重灾区）、运动量大的留意趾甲受压。",
     ["趾甲怎么剪才正确", "嵌甲是怎么回事", "脚趾甲往肉里长怎么办",
      "大脚趾疼是嵌甲吗", "修脚店安全吗"],
     ["问甲沟炎治疗（就医）", "问糖尿病足护理"],
     "atomic", "",
     "嵌甲=趾甲边缘长进肉里（大脚趾常见）：主因剪成弧形深挖+鞋紧；正确=平剪留 1-2mm 盖趾尖；轻度垫棉条引导、化脓就医拔甲矫正；修脚店工具共用有感染风险；鞋头宽松防复发。"),
    ("kp_card_dandruff",
     "头皮屑与去屑",
     "生活常识知识点内容（人话接口）", "生活常识",
     "头皮屑=头皮角质代谢**过快+成片脱落**：①**成因**——头皮油脂多时，**马拉"
     "色菌**（一种以油脂为食的真菌）过度繁殖，其代谢产物刺激头皮加速脱屑（"
     "轻微头皮屑人人都有，片状大量=脂溢性皮炎倾向）；②**去屑成分**（认准洗"
     "发水活性成分）：**酮康唑**（抗真菌，药房有售，严重时用）、**二硫"
     "化硒**、**吡啶硫酮锌（ZPT）**、水杨酸（去角质）——去屑洗发水**在头皮"
     "停留 3-5 分钟**才起效，抓揉起泡就冲等于白洗；③**习惯**：水温温和、少"
     "抓挠、少熬夜少吃油腻辛辣；④**就医线**：屑大片红痒渗液、常规去屑无效"
     "（可能是脂溢性皮炎/银屑病/真菌感染）。",
     ["头皮屑怎么来的", "头皮屑多怎么办", "去屑洗发水哪个成分好",
      "酮康唑洗剂", "头皮屑是真菌吗", "脂溢性皮炎"],
     ["问洗头频率（用洗头卡）", "问银屑病（就医）"],
     "atomic", "",
     "头皮屑=油脂多+马拉色菌过度繁殖刺激头皮加速脱屑；去屑认活性成分=酮康唑/二硫化硒/ZPT/水杨酸，头皮停留 3-5 分钟才起效；温和水温少抓挠少油腻；大片红痒渗液或常规无效=脂溢性皮炎等就医。"),
]

QUESTIONS = [
    ("QB-835", "趾甲怎么剪才不会长成嵌甲？嵌甲化脓了应该怎么办？", "生活常识", "技术直答",
     ["平剪", "弧形", "太深", "鞋", "化脓", "就医"], "通识拓展204"),
    ("QB-836", "头皮屑是怎么产生的？去屑洗发水的哪些成分真正有效？", "生活常识", "技术直答",
     ["马拉色菌", "真菌", "酮康唑", "二硫化硒", "ZPT", "停留"], "通识拓展204"),
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
                               "level:L2", "status:verified", "batch:通识拓展204"],
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
    bank["version"] = "v4.77"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
