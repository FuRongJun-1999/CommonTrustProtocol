# -*- coding: utf-8 -*-
"""seed_common_23_cards.py · 通识拓展批次23知识卡+题库（幂等）

23：物理学-回声与声呐/历史-郑和下西洋/生活常识-灭火原理/音乐-贝多芬
KCCS 四要素+题干原句触发词。（本批起出卡前先按 id 查库防撞——通识拓展22教训）
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_echo",
     "回声与回声测距",
     "基础科学知识点内容（人话接口）", "物理学",
     "回声是声音遇到障碍物被反射回来的现象。人耳要把回声与原声区分开，两次声"
     "音间隔须超过 0.1 秒——对应障碍物至少离你约 17 米（340米/秒 ÷ 10），否则"
     "回声与原声混在一起只觉声音加强。回声测距应用：声呐（潜艇探测/轮船测海"
     "深）、B超（超声波检查身体）、蝙蝠的回声定位（夜间飞行避障捕虫）。对着山"
     "谷大喊听到多重回声，是声音被多处障碍物多次反射的结果。",
     ["回声是怎么回事", "为什么离墙17米才能听到回声", "回声测距的公式",
      "声呐的工作原理", "蝙蝠是怎么避开障碍物的", "B超用什么声波"],
     ["问噪音控制", "问多普勒效应"],
     "atomic", "",
     "回声=声遇障碍物反射；区分回声需≥0.1s(距障碍物≥17m)；应用=声呐/B超/蝙蝠回声定位。"),
    ("kp_card_zhenghe",
     "郑和下西洋",
     "人文通识知识点内容（人话接口）", "历史",
     "郑和下西洋：明朝永乐至宣德年间（1405-1433），郑和奉命率庞大船队七下西"
     "洋，从江苏太仓刘家港出发，遍访亚非三十多个国家和地区，最远到达非洲东海"
     "岸和红海沿岸——比哥伦布首航美洲（1492）早近 90 年，是世界航海史上的壮"
     "举。宝船是当时世界上最大的海船。目的主要是宣扬国威、发展朝贡贸易与海"
     "上交往；比郑和船队规模小得多的欧洲船队却带回了「地理大发现」，两种航行"
     "的历史结局对比耐人寻味。",
     ["郑和下西洋发生在哪个朝代", "郑和下西洋最远到哪里", "郑和几次下西洋",
      "郑和下西洋和哥伦布谁早", "宝船是什么", "郑和从哪里出发"],
     ["问大航海时代对比细节", "问明代海禁"],
     "atomic", "",
     "郑和=明代1405-1433七下西洋(太仓刘家港出发·最远非洲东海岸红海)；比哥伦布早约90年；宝船=当时世界最大海船。"),
    ("kp_card_firefight",
     "燃烧三要素与灭火原理",
     "生活常识知识点内容（人话接口）", "生活常识",
     "燃烧需要三要素同时具备：可燃物、助燃物（氧气）、达到着火点温度——灭火"
     "就是破坏任意一环：①隔绝氧气：油锅起火盖锅盖/二氧化碳灭火器；②降温到着"
     "火点以下：用水浇（水汽化大量吸热）；③移走可燃物：森林火灾砍出隔离带。"
     "重要安全常识：油锅起火千万不能用水浇——油比水轻，水沉底汽化把燃油溅出，"
     "火势会爆燃扩大，正确做法是盖锅盖或倒入大量青菜；电器起火先断电，不能直"
     "接用水（触电风险）。",
     ["油锅起火为什么不能用水浇", "灭火的原理是什么", "燃烧需要哪三个条件",
      "油锅起火怎么办", "电器起火第一步做什么", "二氧化碳灭火器原理"],
     ["问各型灭火器适用场景", "问消防疏散规范"],
     "atomic", "",
     "燃烧三要素=可燃物+氧气+着火点；灭火=隔氧(盖锅盖)/降温(水)/移可燃物(隔离带)；油锅火禁水——盖锅盖。"),
    ("kp_card_beethoven",
     "贝多芬与命运交响曲",
     "人文通识知识点内容（人话接口）", "音乐",
     "贝多芬（1770-1827）：德国作曲家，维也纳古典乐派代表人物之一，被尊称为"
     "「乐圣」。《命运交响曲》即第五交响曲，开头「当当当当——」的四音符动机"
     "被贝多芬解释为「命运在敲门」，是古典音乐中最著名的开头。《月光奏鸣曲》"
     "《献给爱丽丝》脍炙人口；《欢乐颂》（第九交响曲终章，取席勒诗）歌颂人类"
     "团结。最令人敬佩的是他中年起听力衰退直至全聋，仍在无声世界中写出《第九"
     "交响曲》——「我要扼住命运的咽喉」是他一生的写照。",
     ["命运交响曲的作者是谁", "第五交响曲是谁写的", "欢乐颂的作者是",
      "贝多芬是哪国人", "乐圣指谁", "月光奏鸣曲的作者"],
     ["问莫扎特海顿生平", "问交响曲结构分析"],
     "atomic", "",
     "贝多芬(德·乐圣)=命运交响曲(第五·命运敲门)/月光奏鸣曲/欢乐颂(第九)；全聋后仍作第九交响曲。"),
]

QUESTIONS = [
    ("QB-225", "回声是怎么回事", "物理学", "技术直答",
     ["反射", "障碍物"], "通识拓展23"),
    ("QB-226", "郑和下西洋发生在哪个朝代", "历史", "技术直答",
     ["明朝", "明代"], "通识拓展23"),
    ("QB-227", "油锅起火为什么不能用水浇", "生活常识", "技术直答",
     ["油比水轻", "溅出", "盖锅盖"], "通识拓展23"),
    ("QB-228", "命运交响曲的作者是谁", "音乐", "技术直答",
     ["贝多芬", "第五交响曲"], "通识拓展23"),
]


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
                               "level:L2", "status:verified", "batch:通识拓展23"],
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
                   "added": "2026-09-04"})
        added += 1
    bank["version"] = "v1.15"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
