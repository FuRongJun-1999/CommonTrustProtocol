# -*- coding: utf-8 -*-
"""seed_common_264_cards.py · 通识拓展批次264知识卡+题库（幂等）

264：非遗-皮影戏/非遗-剪纸
KCCS 四要素+题干原句触发词。预检已过（QB-983/984+双id可用）。非遗艺术新域。
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
    ("kp_card_pshadow",
     "皮影戏",
     "非遗艺术知识点内容（人话接口）", "文化",
     "皮影戏——光影间的千年艺术：①**是什么**——艺人幕后操纵兽皮/纸板雕制"
     "的平面偶人，借灯光把影像投在白色幕布上，配唱腔与打击乐讲故事，"
     "「一口叙说千古事，双手对舞百万兵」；②**起源**——西汉已有雏形，传说"
     "汉武帝思念李夫人，方士以皮偶映灯影解相思——被视为最早「电影」的"
     "远祖；唐宋兴盛，元代随军事远播波斯与南洋；③**制作**——选牛皮/驴皮"
     "（「驴皮影」）经刮毛浆皮→描样雕刻（千余刀镂空）→敷彩→缀结三至五根"
     "操纵杆，工序复杂成品半透明可透光显色；④**流派**——陕西华县皮影、"
     "唐山皮影、湖北江汉平原皮影等各具唱腔；⑤**地位**——2011 年入选"
     "联合国教科文组织人类非遗代表作名录；⑥**现状**——观众老龄化挑战下"
     "通过进校园/文创联名/短视频传播续命。",
     ["皮影戏是什么", "皮影戏的起源", "皮影用什么做的",
      "皮影戏怎么表演", "皮影戏非遗", "驴皮影"],
     ["问木偶戏对比", "问戏曲脸谱"],
     "atomic", "",
     "皮影戏=幕后操纵兽皮偶人灯光投影白幕配唱乐讲故事+西汉雏形汉武帝思"
     "李夫人传说=电影远祖+牛皮驴皮千刀镂刻敷彩缀杆+华县唐山流派+2011"
     "年联合国非遗+进校园短视频续命。"),
    ("kp_card_papercut",
     "剪纸",
     "非遗艺术知识点内容（人话接口）", "文化",
     "中国剪纸：①**是什么**——剪刀/刻刀在纸上剪刻花纹的民间艺术，贴于"
     "窗棂（窗花）、门楣、喜庆礼俗用品；②**象征语言**——谐音与寓意：鱼="
     "「余」年年有余、蝙蝠=「福」、石榴=多子、喜鹊登梅=喜上眉梢——民俗"
     "吉祥图式高度程式化；③**技法**——阳刻（留线去面，线线相连）与阴刻"
     "（去线留面，面面相连）之分，阴刻厚重阳刻纤细，优秀作品二者结合；④"
     "**地域**——北方（陕北安塞/蔚县点彩）粗犷浑厚，南方（扬州/佛山）"
     "细腻精巧，蔚县剪纸以刻代剪+染彩独树一帜；⑤**历史**——新疆出土"
     "北朝团花剪纸为现存最早实物（1500 年前）；⑥**地位**——2009 年入选"
     "联合国人类非遗名录；春节窗花是承载年俗最广的非遗形态。",
     ["剪纸是什么艺术", "剪纸的寓意", "阳刻和阴刻区别",
      "窗花是什么", "剪纸是哪里发明的", "剪纸非遗"],
     ["问年画对比", "问其他非遗手工艺"],
     "atomic", "",
     "剪纸=刀剪纸上剪刻花纹贴窗棂礼俗+谐音寓意(鱼=余/蝠=福/石榴多子/"
     "喜鹊登梅)+阳刻留线阴刻留面+北方粗犷南方细腻蔚县刻染+北朝团花"
     "1500年最早实物+2009年联合国非遗。"),
]

QUESTIONS = [
    ("QB-983", "皮影戏是怎么表演的？它有多久历史？", "文化", "技术直答",
     ["皮影", "投影", "兽皮", "非遗"], "通识拓展264"),
    ("QB-984", "剪纸的阳刻和阴刻有什么区别？剪纸图案有什么寓意？", "文化", "技术直答",
     ["阳刻", "阴刻", "寓意", "窗花"], "通识拓展264"),
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
                               "level:L2", "status:verified", "batch:通识拓展264"],
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
    bank["version"] = "v5.35"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
