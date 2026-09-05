# -*- coding: utf-8 -*-
"""seed_common_228_cards.py · 通识拓展批次228知识卡+题库（幂等·两卡精批次）

228：历史学-五卅运动/生活常识-羽绒服的清洗
KCCS 四要素+题干原句触发词。三重预检：五卅双库零覆盖；羽绒服清洗（sunquilt
卡仅羽绒被晾晒划界）双库零覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_wusa",
     "五卅运动",
     "人文通识知识点内容（人话接口）", "历史学",
     "五卅运动=**1925 年 5 月 30 日**爆发的反帝爱国运动：①**导火索**——上海"
     "日本纱厂枪杀工人顾正红（共产党员）+英租界巡捕在南京路**枪杀游行群众**"
     "（五卅惨案，死伤数十人）；②**进程**——中共中央号召上海工人罢工/学生罢"
     "课/商人罢市（「三罢」斗争），迅速蔓延到全国各大城市，形成**全国规模的"
     "反帝浪潮**；③**意义**——掀起了**大革命高潮**（1924-1927 大革命），为"
     "后来的北伐战争准备了群众基础；④五卅惨案与省港大罢工（同期广州/香港工"
     "人，坚持 16 个月是世界工运史上最长）相互呼应。",
     ["五卅运动是哪一年", "五卅惨案", "顾正红", "三罢斗争",
      "五卅运动的意义", "省港大罢工"],
     ["问五四运动（用五四卡）", "问北伐战争"],
     "atomic", "",
     "五卅运动=1925.5.30 上海：导火索=日本纱厂枪杀顾正红+英租界巡捕枪杀游行群众[五卅惨案]；三罢斗争蔓延全国反帝浪潮→大革命高潮为北伐准备群众基础；与省港大罢工[16 个月世界工运史最长]呼应。"),
    ("kp_card_downjacket",
     "羽绒服的清洗",
     "生活常识知识点内容（人话接口）", "生活常识",
     "羽绒服清洗要点：①**局部优先**——只有袖口/领口脏就**局部擦洗**（减少整"
     "体水洗次数，保护涂层与羽绒油脂）；②**整体机洗要防「爆」**——羽绒不吸"
     "水高速甩干时**空气无法排出会撑破**面料：务必拉好拉链、扣好扣子、装洗"
     "衣袋、选**低速轻柔**模式（部分机型有羽绒专用档）；③**洗涤剂**——中性"
     "羽绒专用洗涤剂或少量中性洗衣液，**勿用洗衣粉碱性过强**（伤羽绒油脂）；"
     "④**干燥**——低温烘干+放几个烘干球（或干净网球）打松羽绒防结块，**彻"
     "底干透再收**（闷潮发霉发臭）；⑤**勿干洗**——干洗剂破坏羽绒天然油脂降"
     "低保暖性；⑥平铺或宽衣架晾，**勿暴晒**。",
     ["羽绒服怎么洗", "羽绒服能机洗吗", "羽绒服为什么甩干会爆",
      "羽绒服用什么洗涤剂", "羽绒服怎么晾干"],
     ["问烘干球原理", "问洗标符号（用标签卡）"],
     "atomic", "",
     "羽绒服清洗=局部优先+整体机洗拉链扣紧扣洗衣袋低速轻柔[羽绒不排气高速甩干会撑破]+中性羽绒洗涤剂勿碱性洗衣粉+低温烘干放烘干球打松防结块彻底干透+勿干洗[破坏油脂]+平铺晾勿暴晒。"),
]

QUESTIONS = [
    ("QB-882", "五卅运动发生在哪一年？它的导火索是什么事件？", "历史学", "技术直答",
     ["1925", "顾正红", "五卅惨案", "上海", "反帝"], "通识拓展228"),
    ("QB-883", "羽绒服为什么不能用普通模式甩干？正确的清洗方法是什么？", "生活常识", "技术直答",
     ["撑破", "洗衣袋", "低速", "中性", "烘干球", "彻底干透"], "通识拓展228"),
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
                               "level:L2", "status:verified", "batch:通识拓展228"],
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
                   "added": "2026-09-06"})
        added += 1
    bank["version"] = "v4.99"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
