# -*- coding: utf-8 -*-
"""seed_common_179_cards.py · 通识拓展批次179知识卡+题库（幂等·两卡精批次）

179：生活常识-指纹解锁的三种技术/生活常识-淀粉回生（馒头面包变硬）
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖（bakingsoda 卡讲
产气蓬松、OTC 命中安全用药卡弃选）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_fingerunlock",
     "指纹解锁的三种技术",
     "生活常识知识点内容（人话接口）", "生活常识",
     "手机指纹识别三代技术：①**电容式**——传统 Home 键方案：指纹的**嵴（凸）"
     "与谷（凹）**接触传感器形成不同电容，拼出指纹图像（缺点：湿手/汗手易失"
     "灵）；②**光学屏下**——屏下摄像头/短焦镜头**给指纹拍照**比对（屏下指纹"
     "解锁常见方案；注意：强光下或假指纹膜有被欺骗的历史风险，靠算法活体检测"
     "补强）；③**超声波**——声波扫描指纹的**三维嵴谷结构**（甚至汗湿手指也"
     "能识别，穿透性最好，旗舰机配置）。**安全性**：指纹≠密码——指纹无法修改"
     "（泄露了改不了），所以重要支付应**指纹+密码/验证码双因素**；贴膜过厚会"
     "影响屏下识别。冷知识：指纹的用途最初被认为是抓握防滑（与手指泡水起皱同"
     "理）。",
     ["屏幕指纹解锁原理", "电容式指纹和超声波指纹", "指纹解锁安全吗",
      "湿手为什么解锁不了", "光学屏下指纹"],
     ["问人脸识别原理", "问手机支付安全（用防诈骗卡）"],
     "atomic", "",
     "指纹解锁三代=电容式(嵴谷电容差·湿手失灵)/光学屏下(给指纹拍照)/超声波(三维扫描·湿手可用)；指纹不可修改→重要支付用双因素；贴膜过厚影响屏下识别。"),
    ("kp_card_staleretro",
     "馒头面包为什么会变硬（淀粉回生）",
     "基础科学知识点内容（人话接口）", "化学",
     "馒头/面包放几天变硬变干，不只是「水蒸发了」——主因是**淀粉回生（老化）"
     "**：①淀粉分**直链**与**支链**两种分子；刚蒸熟的淀粉是糊化的「乱序舒展"
     "」状态（柔软），放凉后分子**重新排列、紧密结晶**——挤出水分、变硬变"
     "干（即使密封保湿也会变硬，水只是搬不搬得回来的问题）；②**回蒸可部分逆"
     "转**：重新加热让淀粉再「糊化」回柔软（但反复回蒸品质下降）；③**冷藏（"
     "4°C）恰是淀粉回生最快的温度带**——面包馒头**别冷藏，要冷冻**（-18°C "
     "锁住状态，吃前回蒸或烤箱复热几乎如新）；④Additives 工业上用抗老化剂（酶制"
     "剂/单甘酯）延缓面包回生。相关：米饭放凉变硬同理；抗性淀粉（回生的淀粉"
     "消化慢升糖慢）对控糖人群反而有利。",
     ["馒头面包为什么变硬", "淀粉回生是什么", "面包为什么不能冷藏",
      "馒头变硬怎么变软", "抗性淀粉"],
     ["问酵母发酵（用发酵卡）", "问米饭储存"],
     "atomic", "",
     "馒头面包变硬主因=淀粉回生：糊化淀粉放凉后分子重排结晶挤水分（密封也变硬）；回蒸再糊化可部分逆转；4°C 冷藏恰是回生最快温度带——面包馒头要冷冻别冷藏；回生淀粉=抗性淀粉消化慢升糖慢。"),
]

QUESTIONS = [
    ("QB-785", "屏下指纹解锁有光学式和超声波式两种，它们分别是怎么识别指纹的？", "生活常识", "技术直答",
     ["光学", "拍照", "超声波", "三维", "湿手"], "通识拓展179"),
    ("QB-786", "馒头放凉变硬的主要原因是什么？为什么面包不适合放在冷藏室保存？", "化学", "技术直答",
     ["淀粉回生", "老化", "结晶", "冷藏", "回生快", "冷冻"], "通识拓展179"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    whitelist = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
                 "effect", "Additives"}
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{6,}", content):
            if word not in whitelist:
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
                               "level:L2", "status:verified", "batch:通识拓展179"],
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
    bank["version"] = "v4.52"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
