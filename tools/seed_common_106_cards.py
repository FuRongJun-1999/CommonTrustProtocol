# -*- coding: utf-8 -*-
"""seed_common_106_cards.py · 通识拓展批次106知识卡+题库（幂等）

106：物理学-卫星通信/化学-微量元素与人体健康/生物学-合理膳食/地理学-中国海洋资源
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_satellitecomm",
     "卫星通信",
     "基础科学知识点内容（人话接口）", "物理学",
     "卫星通信用微波传递信号：地面站把信号发射到通信卫星，卫星放大后转发回另一"
     "地面站——覆盖广、不受地形限制（偏远山区/海洋/应急救灾利器）。同步通信卫星"
     "在赤道上空约 36000 公里，与地球自转同步（相对地面静止），三颗即可覆盖全球"
     "（除两极）。与地面 5G 互补：星链等低轨卫星星座用数千颗卫星实现全球互联网"
     "接入。北斗短报文也是卫星通信的一种（无信号区求救刚需）。",
     ["卫星通信用什么传递信号", "什么是同步卫星", "卫星通信的优点",
      "星链是什么", "北斗短报文怎么用"],
     ["问卫星轨道类型", "问低轨星座竞争"],
     "atomic", "",
     "卫星通信=微波转发：覆盖广不受地形；同步星 36000km 相对静止·三颗覆盖全球；低轨星座（星链）与北斗短报文同源。"),
    ("kp_card_traceelem",
     "微量元素与人体健康",
     "基础科学知识点内容（人话接口）", "化学",
     "人体必需微量元素缺乏引发的疾病：缺铁——缺铁性贫血（补：动物肝脏/瘦肉）；"
     "缺锌——发育不良味觉减退（海产品/瘦肉）；缺碘——甲状腺肿大「大脖子病」"
     "（加碘盐）；缺硒——克山病（心肌病）；缺氟——龋齿（但过量氟斑牙氟骨症）。"
     "微量元素需求量极少但不可或缺——「微量」不等于「不重要」。均衡饮食（不挑"
     "食）是最好的补充方式，过量补充反而中毒（硒过量脱发、氟过量氟骨症）——剂"
     "量决定利弊。",
     ["人体缺少铁会怎样", "缺锌有什么症状", "微量元素有哪些",
      "缺碘会得什么病", "微量元素过量会怎样", "怎么补微量元素"],
     ["问重金属中毒对比", "问毛发微量元素检测争议"],
     "atomic", "",
     "微量元素：缺铁贫血/缺锌发育不良/缺碘大脖子/缺硒克山/缺氟龋齿；微量但必需；均衡饮食最好·过量反中毒（剂量决定利弊）。"),
    ("kp_card_balancediet",
     "合理膳食与膳食宝塔",
     "基础科学知识点内容（人话接口）", "生物学",
     "合理膳食原则：食物多样、谷类为主（能量主要来源）；多吃蔬果奶豆；适量鱼禽"
     "蛋瘦肉；少盐少油控糖限酒（盐<5g/油 25-30g/添加糖<25g）。中国居民膳食宝塔"
     "分五层：底层谷薯类最多，往上蔬果层、鱼禽肉蛋层、奶豆类层，顶层油盐最少。"
     "三餐比例建议 3:4:3（早中晚）。不健康饮食：高油高盐高糖（三高饮食）与肥胖、"
     "高血压、糖尿病相关。喝水建议：每天 1500-1700ml，少量多次。食品安全五要点："
     "保持清洁、生熟分开、烧熟煮透、安全温度、安全水源。",
     ["合理膳食的原则", "膳食宝塔分几层", "每天吃盐不超过多少",
      "三餐怎么分配", "什么是三高饮食", "每天喝多少水"],
     ["问食物成分表", "问特殊人群膳食指南"],
     "atomic", "",
     "合理膳食=多样谷为主+多蔬果奶豆+适量肉+少盐油糖；宝塔五层谷底油尖；三餐 3:4:3；水 1500-1700ml 少量多次；食安五要点。"),
    ("kp_card_marineres",
     "中国的海洋资源",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国海洋资源丰富：①海洋生物——渔场（舟山最大）与海水养殖（产量世界第一）"
     "；②海洋油气——渤海/东海/南海油气田（深海开采技术发展）；③海洋化学资源——"
     "海盐（长芦盐场最大）、镁、溴；④海洋空间——港口航运/跨海大桥/填海造地；⑤"
     "海洋能源——潮汐能（浙江温岭江厦潮汐试验电站）、海上风电（广东福建江苏）。"
     "保护：海洋污染防治（陆源排污/海上溢油）、伏季休渔制度（让鱼类繁殖）、海洋"
     "保护区建设。海洋强国战略：开发利用与生态保护并重。",
     ["中国海洋资源有哪些", "中国最大的渔场", "长芦盐场在哪里",
      "什么是伏季休渔", "海洋能源有哪些", "海洋强国战略"],
     ["问深海采矿", "问海洋生态保护红线"],
     "atomic", "",
     "海洋资源=生物(舟山渔场·养殖第一)+油气+盐化(长芦)+空间港口+潮汐风电旅游；伏季休渔护资源；开发与保护并重。"),
]

QUESTIONS = [
    ("QB-557", "卫星通信用什么传递信号", "物理学", "技术直答",
     ["微波"], "通识拓展106"),
    ("QB-558", "人体缺少铁会怎样", "化学", "技术直答",
     ["贫血"], "通识拓展106"),
    ("QB-559", "合理膳食的原则", "生物学", "技术直答",
     ["均衡", "食物多样"], "通识拓展106"),
    ("QB-560", "中国海洋资源有哪些", "地理学", "技术直答",
     ["渔业", "油气", "海盐"], "通识拓展106"),
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
                               "level:L2", "status:verified", "batch:通识拓展106"],
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
    bank["version"] = "v1.98"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
