# -*- coding: utf-8 -*-
"""seed_common_90_cards.py · 通识拓展批次90知识卡+题库（幂等）

90：物理学-厨房里的物理/化学-空气污染与防治/生物学-近视的成因与预防/地理学-中国气温分布
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_kitchenphys",
     "厨房里的物理现象",
     "基础科学知识点内容（人话接口）", "物理学",
     "厨房是物理课堂：①抽油烟机——流体流速大压强小（伯努利），把油烟「吸」走"
     "（其实是压出去）；②菜刀磨得锋利——减小受力面积增大压强；③高压锅——增"
     "大气压提高沸点（ cook 呼应）；④炒菜闻到香味——分子扩散（温度高扩散快）；"
     "⑤汤面冒白气——水蒸气液化；⑥冻肉用冷水解冻更快（水比热容大传热效率高）；"
     "⑦铲勺木柄——热的不良导体防烫；⑧电饭煲跳闸——磁钢限温器（103℃ 磁性消"
     "失弹起）；⑨掂勺——惯性；⑩鸡蛋在盐水里浮——阿基米德浮力（盐水密度大于清"
     "水）。跨学科综合题最爱从厨房出题，因为处处是原理。",
     ["厨房里的物理现象", "抽油烟机的原理", "炒菜为什么能闻到香味",
      "电饭煲为什么会跳闸", "冻肉怎么解冻快", "刀刃磨锋利的物理原理"],
     ["问伯努利应用复习", "问磁钢限温器细节"],
     "atomic", "",
     "厨房物理：油烟机(流速大压强小)+锋利刀刃(减面积增 p)+香味(分子扩散)+白气(液化)+盐水浮蛋(浮力)+木柄(热不良导体)+电饭煲磁钢 103℃ 跳闸——多原理集成。"),
    ("kp_card_airpoll",
     "空气污染与防治",
     "基础科学知识点内容（人话接口）", "化学",
     "计入空气质量评价的主要污染物六项：二氧化硫（SO₂）、二氧化氮（NO₂）、一氧"
     "化碳（CO）、臭氧（O₃）、PM10 与 PM2.5（可吸入颗粒物）。典型污染问题：①酸"
     "雨——SO₂ 和氮氧化物溶于雨水（pH<5.6），腐蚀建筑毁森林（硫酸型为主，燃煤"
     "所致）；②光化学烟雾——汽车尾气氮氧化物+碳氢化合物在阳光下发生活化反应"
     "（洛杉矶事件）；③雾霾——PM2.5 积累（haze 呼应）。防治：源头=能源结构转型"
     "（煤改气/煤改电）、尾气治理（催化净化装置）、工业脱硫脱硝；监测=空气质量"
     "指数 AQI（六项污染物浓度评优）；个人=绿色出行、不放烟花（PM2.5 爆表）、"
     "举报露天焚烧。",
     ["空气污染物有哪些", "酸雨是怎么形成的", "什么是光化学烟雾",
      "AQI包括哪六项", "如何防治空气污染", "燃煤排放什么污染物"],
     ["问 SO₂ 性质复习", "问环境标准体系"],
     "atomic", "",
     "空气污染物六项=SO₂/NO₂/CO/O₃/PM10/PM2.5；酸雨=SO₂+氮氧物 pH<5.6 燃煤致；光化学烟雾=尾气+阳光；防治=能源转型+尾气净化+AQI 监测+绿色出行。"),
    ("kp_card_myopia",
     "近视的成因与预防",
     "基础科学知识点内容（人话接口）", "生物学",
     "近视成因：长时间近距离用眼→睫状肌持续紧张→晶状体过度变凸不能恢复（调节"
     "痉挛）→久之眼轴变长——远处物体成像落在视网膜**前方**，看远模糊（真性近视"
     "眼轴变长不可逆）。矫正：佩戴凹透镜（发散光线，让像后移回视网膜）；远视则"
     "相反（凸透镜矫正）。预防「三要四不要」：要读写姿势正确（一尺一拳一寸）、"
     "要远眺放松（每 40 分钟看远 5 分钟）、要认真做眼保健操；不要躺卧/走路/直射"
     "光下看书、不要长时间看电子屏。户外活动是关键护眼手段：每天 2 小时以上自然"
     "光下活动，多巴胺分泌抑制眼轴增长——研究表明户外时间与近视率强负相关（东"
     "亚近视率高的原因之一是户外不足）。高度近视（>600 度）有视网膜脱落风险，要"
     "避免剧烈运动。",
     ["近视的成因是什么", "近视为什么用凹透镜矫正", "怎样预防近视",
      "户外活动为什么能防近视", "高度近视有什么风险", "假性近视和真性近视的区别"],
     ["问角膜激光手术原理", "问远视成因对比"],
     "atomic", "",
     "近视=晶状体过凸+眼轴变长→像成视网膜前(不可逆)：凹透镜矫正；预防=读写一尺一拳一寸+远眺+每天 2h 户外(自然光抑眼轴)；高度近视防视网膜脱落。"),
    ("kp_card_tempdist",
     "中国气温的分布",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国气温分布规律：①**冬季南北温差大**（漠河约 -30℃ 与海南约 20℃ 相差 50"
     "℃+）——原因：纬度因素（北方太阳高度低白昼短）+冬季风加剧北方寒冷（南下"
     "无阻）；越往北越冷。②**夏季普遍高温、南北温差小**（除青藏高原——地势高）"
     "——最热在新疆吐鲁番（「火洲」，约 48℃ 极值）；夏季最低温在青藏高原（因"
     "海拔）。温度带划分（活动积温）：寒温带/中温带/暖温带/亚热带/热带+青藏高寒"
     "区——决定作物熟制（东北一年一熟、华北两年三熟、南方一年两熟到三熟）。1 月"
     "0℃ 等温线=秦岭淮河（南河不冻北河冻、南无暖气北有暖气的分界）。",
     ["中国冬季南北温差大的原因", "中国夏季气温分布特点", "吐鲁番为什么最热",
      "温度带怎么划分", "秦岭淮河与1月等温线", "青藏高原夏季气温低的原因"],
     ["问积温与农业熟制", "问寒潮路径"],
     "atomic", "",
     "气温分布：冬=南北温差 50℃+(纬度+冬季风)·越北越冷；夏=普遍高温除青藏(地势)·最热吐鲁番；温度带五带+高寒区定熟制；1 月 0℃ 线=秦岭淮河(南北供暖界)。"),
]

QUESTIONS = [
    ("QB-493", "厨房里的物理现象", "物理学", "技术直答",
     ["压强", "扩散", "液化"], "通识拓展90"),
    ("QB-494", "空气污染物有哪些", "化学", "技术直答",
     ["二氧化硫", "PM2.5", "一氧化碳"], "通识拓展90"),
    ("QB-495", "近视的成因是什么", "生物学", "技术直答",
     ["晶状体", "眼轴"], "通识拓展90"),
    ("QB-496", "中国冬季南北温差大的原因", "地理学", "技术直答",
     ["纬度", "冬季风"], "通识拓展90"),
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
                               "level:L2", "status:verified", "batch:通识拓展90"],
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
    bank["version"] = "v1.82"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
