# -*- coding: utf-8 -*-
"""seed_common_144_cards.py · 通识拓展批次144知识卡+题库（幂等·两卡精批次）

144：生活常识-儿童乘车安全与安全座椅/生物学-森林的生态作用
KCCS 四要素+题干原句触发词。三重预检：安全座椅双库零覆盖；森林生态作用
（「森林」命中均为布雷顿森林/随机森林等同名异物）主题未覆盖。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_carseat",
     "儿童乘车安全与安全座椅",
     "生活常识知识点内容（人话接口）", "生活常识",
     "儿童乘车三大铁律：①**必须用安全座椅**——身高不足 145cm/12 岁以下儿童"
     "不能直接用成人安全带：腰带勒腹部、肩带勒颈部，急刹时会造成内脏损伤甚至"
     "勒颈；应按年龄体重使用**安全座椅或增高垫**（婴儿期**反向安装**——婴儿颈"
     "部脆弱，反向座椅整体承接冲击力）；《未成年人保护法》已要求父母采取配备"
     "儿童安全座椅等措施；②**绝不抱孩子坐车**——30km/h 碰撞时 10kg 儿童的惯"
     "性冲击力超过 300kg，成人根本抱不住（相当于从 3 层楼摔下的力）；③后排两"
     "侧=最安全位置。下车安全：教孩子「**荷式开门法**」——用离车门远的那只手"
     "开门，身体自然转动回头观察后方来车（电动车「鬼探头」事故多因突然推门）。"
     "另：车内不留儿童独处（高温窒息/误操作）。",
     ["儿童为什么要用安全座椅", "孩子能用成人安全带吗", "安全座椅反向安装",
      "抱孩子坐车安全吗", "荷式开门法", "儿童坐车哪个位置最安全"],
     ["问安全座椅品牌选购", "问校车管理规定"],
     "atomic", "",
     "儿童乘车=12 岁以下/145cm 以下用安全座椅(婴儿反向安装)——成人安全带勒腹勒颈；勿抱孩子坐车(30km/h 碰撞 10kg 儿童冲击力超 300kg 抱不住)；后排两侧最安全；下车用荷式开门法(远端手开门回头观察)；儿童不独留车内。"),
    ("kp_card_forestrole",
     "森林的生态作用",
     "基础科学知识点内容（人话接口）", "生物学",
     "森林被称为「**地球之肺**」，七大生态功能：①**固碳释氧**——光合作用吸"
     "收二氧化碳释放氧气（一棵成年树一天约吸收二氧化碳、释放够数人呼吸的氧"
     "气）；②**调节气候**——蒸腾作用增加空气湿度、促进降水，夏季林荫降温；"
     "③**涵养水源**——「绿色水库」，树冠截雨、枯枝落叶层吸水，减缓地表径流"
     "（砍林→山洪暴发）；④**保持水土**——根系固土，黄土高原治理关键=植树种"
     "草；⑤**防风固沙**——三北防护林工程锁住风沙；⑥**净化空气**——吸附粉"
     "尘、吸收有害气体、杀菌降噪；⑦**生物多样性宝库**——森林是陆地上大多数"
     "物种的家园。纪念：**3 月 12 日中国植树节**（纪念孙中山）；**塞罕坝林"
     "场**——三代人把荒漠变百万亩林海，获联合国「地球卫士奖」。反例警示：亚"
     "马孙雨林砍伐加剧气候危机——「地球之肺」变成排碳源。",
     ["森林的作用", "为什么说森林是地球之肺", "植树节是哪一天",
      "涵养水源是什么意思", "三北防护林", "塞罕坝精神"],
     ["问垃圾分类（另类环保）", "问林业产业经济"],
     "atomic", "",
     "森林=地球之肺：固碳释氧+蒸腾调湿+涵养水源(绿色水库)+保持水土(黄土治理)+防风固沙(三北防护林)+净化空气+生物多样性宝库；3.12 植树节(纪念孙中山)；塞罕坝荒漠变林海获地球卫士奖。"),
]

QUESTIONS = [
    ("QB-695", "为什么儿童乘车必须使用安全座椅，而不能直接使用成人安全带？", "生活常识", "技术直答",
     ["勒", "腹部", "颈部", "身高", "12", "反向"], "通识拓展144"),
    ("QB-696", "森林为什么被称为「地球之肺」？它有哪些主要生态功能？", "生物学", "技术直答",
     ["光合", "氧气", "二氧化碳", "固碳", "涵养水源", "水土"], "通识拓展144"),
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
                               "level:L2", "status:verified", "batch:通识拓展144"],
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
    bank["version"] = "v4.17"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
