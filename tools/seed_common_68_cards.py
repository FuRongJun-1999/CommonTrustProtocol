# -*- coding: utf-8 -*-
"""seed_common_68_cards.py · 通识拓展批次68知识卡+题库（幂等）

68：物理学-一度电/化学-稀有气体/生物学-脊椎动物分类/地理学-世界人口分布
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_kwh",
     "一度电：千瓦时",
     "基础科学知识点内容（人话接口）", "物理学",
     "「一度电」=1 千瓦时（kW·h）——功率 1 千瓦的用电器工作 1 小时消耗的电能"
     "（1 kW·h=3.6×10⁶ J）。电费按「度」计费就是按电能多少收费。直观感受一度电"
     "能干什么：LED 灯 10W 亮约 100 小时、手机充电约 100 次、冰箱运行 1-2 天、电"
     "饭煲煮 20 锅饭、洗衣机洗十几桶衣服。电器耗电=功率×时间：2 匹空调约 1500W，"
     "开 1 小时约 1.5 度；电热水器 3000W 开 1 小时 3 度（夏季电费大头）。节电常"
     "识：待机也耗电（机顶盒待机一年可达几十度）、空调调高 1℃ 省电约 6-8%、选"
     "一级能效电器。电表读数：月末减月初=当月用电度数。",
     ["一度电是多少", "1千瓦时等于多少焦耳", "一度电能干什么",
      "空调一小时用几度电", "怎么看电表读数", "什么电器最耗电"],
     ["问电功率计算 P=UI", "问阶梯电价"],
     "atomic", "",
     "一度电=1kW·h=3.6×10⁶J（1kW 用 1h）；LED 10W 亮 100h/冰箱 1-2 天/2 匹空调 1h=1.5 度；耗电=功率×时间；待机也耗·空调+1℃ 省 6-8%。"),
    ("kp_card_noblegas",
     "稀有气体与霓虹灯",
     "基础科学知识点内容（人话接口）", "化学",
     "稀有气体（氦氖氩氪氙氡）是元素周期表最右一列（0 族）——原子最外层电子已达"
     "稳定结构，所以化学性质极不活泼（旧称「惰性气体」，但现已合成出氙氪的化合"
     "物，「惰性」名不副实）。通电会发出特征颜色的光（不同气体/气压颜色不同）——"
     "霓虹灯的原理：氖发红光（「霓虹」音译自 NEON）、氩发紫蓝光、氦发粉光。用"
     "途：氦气（密度仅次于氢但不燃——飞艇/气球，深海呼吸混合气防减压病）；氩气"
     "（化学惰性做保护气——焊接保护/灯泡填充/食品充氮的搭档）；氙气（疝气车灯/"
     "麻醉研究）；氡（放射性气体，地下室氡超标是肺癌风险因素，需检测通风）。",
     ["霓虹灯为什么五颜六色", "稀有气体有哪些", "氦气能代替氢气做飞艇吗",
      "稀有气体为什么化学性质不活泼", "氡气有什么危害", "焊接时为什么要用氩气"],
     ["问惰性化合物 XePtF6", "问宇宙氦丰度"],
     "atomic", "",
     "稀有气体(He Ne Ar Kr Xe Rn)=0 族·外层稳定故不活泼；通电发特征色→霓虹灯(氖红氩紫蓝氦粉)；氦=飞艇/深海混合气；氩=焊接保护气；氡放射性地下室监测。"),
    ("kp_card_vertebrate",
     "脊椎动物的五大类",
     "基础科学知识点内容（人话接口）", "生物学",
     "动物按有无脊椎骨分脊椎动物与无脊椎动物（昆虫/蜗牛/章鱼等约占 95%）。脊椎"
     "动物五大纲（由低等到高等）：①鱼类——水生、鳃呼吸、鳍游泳、体表鳞片（变"
     "温），如鲤鱼鲨鱼；②两栖类——幼体水生用鳃（蝌蚪）、成体肺+皮肤呼吸（青"
     "蛙/蟾蜍/大鲵「娃娃鱼」），变态发育；③爬行类——体表鳞片或甲、肺呼吸、陆"
     "生产羊膜卵（龟/蛇/蜥蜴/鳄），真正摆脱水的束缚；④鸟类——恒温、卵生、前肢"
     "变翼、气囊辅助呼吸（双重呼吸）；⑤哺乳类——恒温、胎生哺乳（鸭嘴兽例外卵"
     "生）、牙齿分化（鲸/蝙蝠也是哺乳类）。从鱼到哺乳类的演化主线：水生→陆生、"
     "变温→恒温、卵生→胎生。",
     ["脊椎动物和无脊椎动物的区别", "脊椎动物分为哪五大类", "两栖动物是什么意思",
      "鲸鱼为什么不是鱼", "什么是变温动物", "从低等到高等的顺序"],
     ["问鱼类登陆演化", "问无脊椎主要门类"],
     "atomic", "",
     "脊椎五纲（低→高）：鱼(鳃·鳞·变温)→两栖(变态·肺+皮肤)→爬行(羊膜卵·离水)→鸟(恒温·双重呼吸)→哺乳(胎生哺乳·恒温)；鲸蝙蝠=哺乳；变温=鱼两栖爬行。"),
    ("kp_card_popdist",
     "世界人口分布",
     "人文通识知识点内容（人话接口）", "地理学",
     "世界人口超 80 亿（2022 年 11 月联合国宣布突破），分布极不均匀：四大人口稠"
     "密区——东亚（中国东部/日本）、南亚（印度/孟加拉）、东南亚、欧洲西部（以及"
     "北美东部）——共同点：中低纬度近海的平原丘陵、气候温和湿润、农业工业发达。"
     "人口稀疏区：干旱沙漠（撒哈拉）、高寒高原（青藏/西伯利亚北部）、湿热雨林"
     "（亚马孙）、高纬严寒——「四疏」对应「不适居」。人口大国：印度（2023 年超"
     "中国成第一）、中国、美国、印尼、巴基斯坦。人口问题两面：过快增长压资源环"
     "境（非洲部分区域）；老龄化与负增长压经济社会（日/欧/中国政策转向鼓励生育"
     "）。城市化：全球超半数人口住在城市。",
     ["世界人口最多的洲", "世界人口稠密区在哪里", "世界人口突破多少亿",
      "人口稀疏区有哪些", "印度人口超过中国了吗", "什么是人口老龄化"],
     ["问人口金字塔判读", "问中国人口政策演变"],
     "atomic", "",
     "世界 80 亿+·亚洲第一；四密=东亚/南亚/东南亚/西欧(中低纬近海平原)；四疏=沙漠/高寒/雨林/高纬；印度 2023 超中国居首；两难=过快增长 vs 老龄化。"),
]

QUESTIONS = [
    ("QB-405", "一度电是多少", "物理学", "技术直答",
     ["1千瓦时", "kWh"], "通识拓展68"),
    ("QB-406", "霓虹灯为什么五颜六色", "化学", "技术直答",
     ["稀有气体", "通电发光"], "通识拓展68"),
    ("QB-407", "脊椎动物分为哪五大类", "生物学", "技术直答",
     ["鱼", "两栖", "爬行", "鸟", "哺乳"], "通识拓展68"),
    ("QB-408", "世界人口最多的洲", "地理学", "技术直答",
     ["亚洲"], "通识拓展68"),
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
                               "level:L2", "status:verified", "batch:通识拓展68"],
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
    bank["version"] = "v1.60"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
