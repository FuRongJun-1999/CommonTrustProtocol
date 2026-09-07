# -*- coding: utf-8 -*-
"""seed_common_514_cards.py · 通识拓展批次514知识卡+题库（幂等）

514：2 张新卡·明清小说补位（聊斋志异 kp_card_liaozhai /
    儒林外史 kp_card_rulin——id 与语义等价卡名双重确认零覆盖）。
预检已过（QB-1774~1776 可用）。
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
             "MTBF", "SQA", "IMC", "HMO", "JD", "STAR", "Word", "offer",
             "XMind", "HDR", "Robotaxi"}


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
    ("kp_card_liaozhai",
     "聊斋志异",
     "古典文学知识点内容（人话接口）", "艺术学堂",
     "《聊斋志异》——文言短篇小说的巅峰：①**作者**——蒲松龄（1640-"
     "1715），字留仙，号柳泉居士，山东淄川人，一生科举失意，71 岁才援"
     "例成岁贡生；②**内容**——近五百篇文言短篇，花妖狐魅、幽冥世界"
     "多具人情，和易可亲；③**名篇**——《画皮》（恶鬼披人皮）、《聂小"
     "倩》（书生宁采臣与女鬼）、《婴宁》（爱笑的狐女）、《促织》（一只"
     "蟋蟀写尽苛政害人）；④**评价**——郭沫若题联「写鬼写妖高人一等，"
     "刺贪刺虐入骨三分」，借鬼狐讽现实；⑤**传说**——相传蒲松龄在柳"
     "泉边设茶待客，请人讲奇闻换素材；⑥**影响**——影视改编无数，"
     "「聊斋」成为志怪传奇的代名词。",
     ["聊斋志异是谁写的", "蒲松龄", "画皮", "聂小倩",
      "写鬼写妖高人一等", "聊斋讲什么"],
     ["问西游记", "问儒林外史"],
     "atomic", "",
     "聊斋志异=蒲松龄柳泉居士山东淄川科举失意71岁岁贡生+近五百篇文言"
     "短篇花妖狐魅多具人情+画皮聂小倩婴宁促织+郭沫若写鬼写妖高人一等"
     "刺贪刺虐入骨三分借鬼狐讽现实+柳泉设茶换故事传说+志怪传奇代名词"
     "。"),
    ("kp_card_rulin",
     "儒林外史",
     "古典文学知识点内容（人话接口）", "艺术学堂",
     "《儒林外史》——古典讽刺小说的高峰：①**作者**——吴敬梓（1701-"
     "1754），安徽全椒人，家道中落移居南京，亲见科场冷暖；②**结构**——"
     "五十余回，「虽云长篇，颇同短制」：连环短章、人物轮替出场，无贯穿"
     "始终的主角；③**名场面**——范进中举：54 岁中举喜极而疯，胡屠户"
     "前倨后恭一巴掌打醒；严监生临终伸两根指头——只为灯盏里点了两茎"
     "灯草费油，吝啬鬼典型；周进六十多岁撞号板痛哭；④**主题**——揭露"
     "科举制度对士人灵魂的腐蚀，「一代文人有厄」；开篇王冕是淡泊功名的"
     "理想人物参照；⑤**地位**——与《红楼梦》同为清代小说双璧，直接启"
     "迪近代讽刺文学（鲁迅盛赞）。",
     ["儒林外史是谁写的", "范进中举", "严监生", "吴敬梓",
      "讽刺小说", "儒林外史讲什么"],
     ["问聊斋志异", "问科举制度"],
     "atomic", "",
     "儒林外史=吴敬梓安徽全椒家道中落移居南京+五十余回虽云长篇颇同短"
     "制连环短章无贯穿主角+范进中举喜极而疯胡屠户前倨后恭+严监生两茎"
     "灯草吝啬鬼+周进撞号板+科举腐蚀士人王冕理想人物+清代小说双璧启"
     "迪鲁迅讽刺文学。"),
]

QUESTIONS = [
    ("QB-1774", "《聊斋志异》的作者是谁？这部书有什么特点？",
     "文学常识", "技术直答",
     ["聊斋志异", "蒲松龄", "文言", "狐鬼"], "通识拓展514·新卡"),
    ("QB-1775", "「范进中举」讲的是什么故事？讽刺了什么现象？",
     "文学常识", "技术直答",
     ["范进中举", "儒林外史", "科举", "讽刺"], "通识拓展514·新卡"),
    ("QB-1776", "严监生临死前伸两根指头是什么典故？出自哪部书？",
     "文学常识", "技术直答",
     ["严监生", "两茎灯草", "儒林外史", "吝啬"], "通识拓展514·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展514"],
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
    bank["version"] = "v7.79"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
