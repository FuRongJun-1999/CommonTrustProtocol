# -*- coding: utf-8 -*-
"""seed_common_25_cards.py · 通识拓展批次25知识卡+题库（幂等）

25：生活常识-高压锅/历史-甲骨文/生物学-昆虫特征/计算机科学-HTTPS
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_pressurecooker",
     "高压锅为什么煮饭快",
     "生活常识知识点内容（人话接口）", "生活常识",
     "液体的沸点随气压增大而升高：平地标准大气压下水约 100℃ 沸腾，高压锅密封"
     "后锅内气压可达约 2 个大气压，水的沸点升到约 120℃——更高的炖煮温度让食"
     "物熟得更快更烂（高原上水约 80 多度就沸腾煮不熟饭，高压锅正是解药）。锅盖"
     "上的限压阀控制最高气压，保证安全——使用前要检查排气孔畅通、密封圈老化要"
     "更换，开盖前必须等锅内降压（自然冷却或手动放气），带压强开盖会喷溅伤人。",
     ["高压锅为什么煮饭快", "高压锅的原理", "气压和沸点有什么关系",
      "高原上用高压锅有什么用", "高压锅怎么用才安全", "水的沸点是多少"],
     ["问压力容器规范", "问海拔与气压换算"],
     "atomic", "",
     "沸点随气压升高：高压锅≈2atm→水约120℃沸腾→炖煮更快；高原沸点低用高压锅补；开盖前必须降压。"),
    ("kp_card_oracle",
     "甲骨文",
     "人文通识知识点内容（人话接口）", "历史",
     "甲骨文是中国目前已知最早、最成熟的成体系文字：商朝晚期（约公元前14—前"
     "11世纪）刻在龟甲与兽骨上，主要用于王室占卜记事（「卜辞」），1899 年由金"
     "石学家王懿荣首先识别确认，出土于河南安阳殷墟。甲骨文已发现单字约 4500 "
     "个，其中可释读的约 1500-2000 个；它与金文、小篆、隶书、楷书一脉相承，"
     "现代汉字由它演变而来——汉字是世界上唯一沿用至今的自源古典文字体系。2017"
     " 年甲骨文入选联合国「世界记忆名录」。",
     ["我国最早的成熟文字是什么", "甲骨文是哪个朝代的", "甲骨文刻在哪里",
      "甲骨文是谁发现的", "殷墟在哪里", "甲骨文有多少个字"],
     ["问金文小篆演变细节", "问其他古文明文字对比"],
     "atomic", "",
     "甲骨文=商晚期刻龟甲兽骨的占卜文字，最早成熟汉字体系；1899王懿荣识别·安阳殷墟出土；单字约4500可释约半。"),
    ("kp_card_insect",
     "昆虫的基本特征",
     "基础科学知识点内容（人话接口）", "生物学",
     "昆虫的判定口诀：身体分头、胸、腹三部分，胸部有三对足（6 条腿）、通常有"
     "两对翅，头部一对触角。蜘蛛有 8 条腿、身体分两部分，属于蛛形纲不是昆虫；"
     "蜈蚣蚰蜒多足属多足纲；虾蟹属甲壳纲——「虫子」不都是昆虫。数量上昆虫是动"
     "物界最繁盛的类群，已知超 100 万种（占动物种类一半以上）：蜜蜂蝴蝶（完全变"
     "态：卵→幼虫→蛹→成虫）、蝗虫蟋蟀（不完全变态：卵→若虫→成虫）。",
     ["昆虫有几条腿", "蜘蛛是昆虫吗", "昆虫有什么特征", "蜈蚣是昆虫吗",
      "什么是完全变态发育", "蝴蝶和蛾子怎么区分"],
     ["问昆虫翅膀演化", "问社会性昆虫分工"],
     "atomic", "",
     "昆虫=头胸腹三部+3对足(6腿)+2对翅+1对触角；蜘蛛8腿=蛛形纲非昆虫；完全变态=卵幼虫蛹成虫。"),
    ("kp_card_https",
     "网址里的 HTTP 与 HTTPS",
     "基础科学知识点内容（人话接口）", "计算机科学",
     "HTTP 是浏览器与网站服务器之间传输网页数据的协议；HTTPS = HTTP + 加密"
     "（SSL/TLS）：数据在传输前被加密，即使被中间人截获也读不到、篡改不了，同"
     "时网站证书由权威机构签发、可验证网站真实身份——地址栏的「小锁」标志就是"
     "这个意思。网银、登录密码等敏感操作必须走 HTTPS。HTTP 默认端口 80，HTTPS"
     " 默认端口 443。现在全网主流浏览器对纯 HTTP 网站会标注「不安全」。",
     ["网址开头的https是什么意思", "HTTPS和HTTP有什么区别", "地址栏的小锁是什么",
      "为什么网银要用https", "HTTPS的默认端口是多少", "什么是SSL证书"],
     ["问TLS握手细节", "问证书链验证"],
     "atomic", "",
     "HTTPS=HTTP+TLS加密：防窃听/防篡改/验身份（小锁标志）；敏感操作必须走 HTTPS；默认端口 443(HTTP=80)。"),
]

QUESTIONS = [
    ("QB-233", "高压锅为什么煮饭快", "生活常识", "技术直答",
     ["气压", "沸点"], "通识拓展25"),
    ("QB-234", "我国最早的成熟文字是什么", "历史", "技术直答",
     ["甲骨文"], "通识拓展25"),
    ("QB-235", "蜘蛛是昆虫吗", "生物学", "技术直答",
     ["8条腿", "蛛形纲", "不是"], "通识拓展25"),
    ("QB-236", "网址开头的https是什么意思", "计算机科学", "技术直答",
     ["加密", "SSL", "TLS"], "通识拓展25"),
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
                               "level:L2", "status:verified", "batch:通识拓展25"],
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
    bank["version"] = "v1.17"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
