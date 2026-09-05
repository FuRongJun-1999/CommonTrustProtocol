# -*- coding: utf-8 -*-
"""seed_common_188_cards.py · 通识拓展批次188知识卡+题库（幂等·两卡精批次）

188：生活常识-「脚气」与「脚气病」混淆辨析/生物学-斑马为什么有条纹
KCCS 四要素+题干原句触发词。三重预检：脚气辨析与 vitamins 卡（B1 缺乏医学
角度）互补；斑马条纹双库零覆盖（trafficsign 仅斑马线一词）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_athletesfoot",
     "「脚气」和「脚气病」是两种病",
     "生活常识知识点内容（人话接口）", "生活常识",
     "日常说的「脚气」和医学的「脚气病」**完全是两种病**，极易混淆：①**俗称"
     "的脚气=足癣（香港脚）**——**真菌感染**（皮肤癣菌），症状=脚趾缝脱皮、"
     "水疱、瘙痒、异味，**传染**（共用拖鞋/毛巾/脚盆传播）；治疗=**抗真菌药"
     "膏/喷剂**（联苯苄唑/特比萘芬，症状消失后再用 1-2 周防复发），鞋袜消毒"
     "暴晒；②**医学的脚气病=维生素 B1（硫胺素）缺乏症**——表现为**周围神经"
     "炎（手脚麻木无力）+水肿甚至心脏损害**，不痒不传染，治疗=补充维生素 B1"
     "（长期吃精白米/酗酒者风险高——米不要过度淘洗）。一句话：**痒的用抗真菌"
     "药，麻的补 B1**——把足癣当脚气病补 B1 完全无效，反之亦然。",
     ["脚气和脚气病的区别", "脚气是真菌感染吗", "脚气病是缺什么",
      "足癣怎么治", "维生素B1缺乏", "脚气传染吗"],
     ["问维生素 B 族（用维生素卡）", "问灰指甲（同真菌）"],
     "atomic", "",
     "「脚气」=足癣=真菌感染（脱皮水疱痒·传染·抗真菌药膏治）≠「脚气病」=维生素 B1 缺乏症（手脚麻木无力水肿·不痒不传染·补 B1）——痒的用抗真菌药、麻的补 B1；长期精白米/酗酒者防 B1 缺乏。"),
    ("kp_card_zebrastripe",
     "斑马为什么有条纹",
     "基础科学知识点内容（人话接口）", "生物学",
     "斑马条纹的进化意义至今众说纷纭，目前**证据最强的假说=防蚊蝇叮咬**：①"
     "**防蝇说（主流）**——野外实验显示**条纹表面落下的吸血蝇（采采蝇/马蝇）"
     "明显更少**：条纹干扰蝇类的视觉系统，让它们无法准确判断减速着陆的距离与"
     "方向（高速影像显示它们会「撞上」或直接飞过）；②其他假说（各有证据但不"
     "足）：体温调节（黑白条纹形成微气流）、社会识别（每只斑马条纹独一无二，"
     "像「条形码身份证」）、伪装（狮子是色盲，条纹在草丛中模糊轮廓的作用存"
     "疑）、防捕食者的「运动眩晕」效应；③趣闻：条纹还让狮子难以在斑马群中"
     "「锁定」单只目标（群体逃散时目标混淆）。**为什么斑马有而马没有**——与"
     "斑马分布在采采蝇肆虐的非洲有相关，但演化细节仍是活跃研究领域。",
     ["斑马为什么有条纹", "斑马条纹的作用", "防蝇假说", "斑马条纹身份证",
      "条纹防蚊"],
     ["问动物保护色（用变色卡）", "问其他动物趣闻"],
     "atomic", "",
     "斑马条纹证据最强假说=防吸血蝇叮咬（条纹干扰蝇类视觉定位着陆，野外实验蝇落更少）；其他假说=体温调节/个体识别（条纹如条形码）/群体混淆；为什么马没有仍待研究——演化活跃领域。"),
]

QUESTIONS = [
    ("QB-804", "日常说的「脚气」和医学上的「脚气病」是一种病吗？分别怎么治？", "生活常识", "技术直答",
     ["真菌", "足癣", "维生素B1", "传染", "抗真菌", "两种病"], "通识拓展188"),
    ("QB-805", "关于斑马为什么有条纹，目前证据最强的假说是什么？", "生物学", "技术直答",
     ["防蝇", "蚊蝇", "叮咬", "视觉", "干扰"], "通识拓展188"),
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
                               "level:L2", "status:verified", "batch:通识拓展188"],
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
    bank["version"] = "v4.61"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
