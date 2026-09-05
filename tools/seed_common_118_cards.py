# -*- coding: utf-8 -*-
"""seed_common_118_cards.py · 通识拓展批次118知识卡+题库（幂等）

118：物理学-超声波测距原理/生物学-国际禁毒日/地理学-中国省级行政中心
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_ultrasonicdist",
     "超声波测距原理：s=vt/2",
     "基础科学知识点内容（人话接口）", "物理学",
     "超声波测距（回声测距）原理：发射超声波→声波遇到障碍物**反射**回来→接收"
     "回波→计算距离 s=vt/2（v=声速约 340m/s，t=往返总时间，除以 2 因为走了一去"
     "一回）。应用：①倒车雷达（汽车尾部的超声波探头，滴滴声越急越近）；②声呐"
     "（潜艇/轮船，用水下声速约 1500m/s）；③超声测厚（测钢板厚度）；④盲人超声"
     "导盲仪。限制：超声波无法在真空中传播（月球上不能用）。蝙蝠的回声定位就是"
     "天然超声波测距（每秒发射数百次超声，精度达毫米级）。",
     ["超声波测距的原理", "倒车雷达的原理", "声呐测距公式",
      "回声测距为什么要除以2", "月球上能用超声波测距吗", "蝙蝠回声定位"],
     ["问多普勒超声测速", "问激光测距对比"],
     "atomic", "",
     "超声测距 s=vt/2(往返减半)：倒车雷达(滴滴越急越近)/声呐(水中 1500m/s)/超声测厚/盲人导盲仪；真空不可用(月球失效)；蝙蝠回声定位精度毫米级。"),
    ("kp_card_drugday",
     "国际禁毒日：6 月 26 日",
     "基础科学知识点内容（人话接口）", "生物学",
     "国际禁毒日：每年 **6 月 26 日**（1987 年联合国设立，源于虎门销烟完成的日"
     "期纪念——清道光十九年即 1839 年 6 月 25 日销烟完成，次日正式结束）。主题："
     "「健康人生、绿色无毒」。毒品种类：传统毒品（鸦片/海洛因/大麻）+合成毒品"
     "（冰毒/摇头丸/K粉）+新精神活性物质（「上头电子烟」含合成大麻素）。青少年"
     "防毒：①不接受陌生人提供的饮料食品香烟（可能掺药）；②不因好奇尝试（一次"
     "成瘾风险）；③不去复杂娱乐场所；④遇到引诱立即告知家长老师或报警。禁毒法"
     "：《禁毒法》2008 年施行，走私贩卖运输制造毒品无论数量多少都追究刑责。",
     ["国际禁毒日是哪一天", "禁毒日为什么是6月26日", "新型毒品有哪些",
      "青少年怎么防毒", "上头电子烟是什么", "禁毒法什么时候施行"],
     ["问戒毒康复体系", "问合成大麻素列管"],
     "atomic", "",
     "国际禁毒日=6.26(1987 设立·呼应虎门销烟)：传统毒品(鸦片海洛因)+合成(冰毒 K粉)+新精活(上头电子烟)；青少年防毒=不接受不好奇不去不隐瞒即报警；禁毒法 2008。"),
    ("kp_card_provitals",
     "中国省级行政中心",
     "人文通识知识点内容（人话接口）", "地理学",
     "34 个省级行政区的行政中心（省会/首府）速记：华北——河北石家庄、山西太"
     "原、内蒙古呼和浩特；东北——辽宁沈阳、吉林长春、黑龙江哈尔滨；华东——山东"
     "济南、江苏南京、浙江杭州、安徽合肥、福建福州、江西南昌、台湾台北；华中——"
     "河南郑州、湖北武汉、湖南长沙；华南——广东广州、广西南宁、海南海口、香港、"
     "澳门；西南——重庆、四川成都、贵州贵阳、云南昆明、西藏拉萨；西北——陕西西"
     "安、甘肃兰州、青海西宁、宁夏银川、新疆乌鲁木齐。易混考点：河北→石家庄（不"
     "是保定）、江苏→南京（不是苏州）、福建→福州（不是厦门）、青海→西宁（不是"
     "兰州）、广西→南宁（不是桂林）。",
     ["中国各省的省会", "河北省会是哪个城市", "江苏省会是哪个城市",
      "青海省会是哪个城市", "广西的行政中心", "福州和厦门哪个是省会"],
     ["问省会简称对照", "问省会城市经济排名"],
     "atomic", "",
     "省会速记易错五组：河北石家庄(非保定)/江苏南京(非苏州)/福建福州(非厦门)/青海西宁(非兰州)/广西南宁(非桂林)；东北三省=沈长哈；西部=乌拉西宁兰银成。"),
]

QUESTIONS = [
    ("QB-608", "超声波测距的原理", "物理学", "技术直答",
     ["回声", "s=vt/2"], "通识拓展118"),
    ("QB-609", "国际禁毒日是哪一天", "生物学", "技术直答",
     ["6月26日"], "通识拓展118"),
    ("QB-610", "河北省会是哪个城市", "地理学", "技术直答",
     ["石家庄"], "通识拓展118"),
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
                               "level:L2", "status:verified", "batch:通识拓展118"],
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
    bank["version"] = "v3.2"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
