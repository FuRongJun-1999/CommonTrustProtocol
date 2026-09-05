# -*- coding: utf-8 -*-
"""seed_common_140_cards.py · 通识拓展批次140知识卡+题库（幂等）

140：生活常识-快递寄收件常识/历史学-两弹一星/地理学-黄河凌汛
KCCS 四要素+题干原句触发词。三重预检：三主题双库均零覆盖（全新域组）。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_express",
     "快递寄收件常识",
     "生活常识知识点内容（人话接口）", "生活常识",
     "寄快递：**实名寄递**（寄件人身份证+开箱验视是法规要求）；**贵重物品务必"
     "保价**——未保价件丢失损毁一般按运费倍数赔偿（常见为运费的 3-7 倍，几百"
     "元的物品可能只赔几十元），保价费通常为声明价值的 1%-3%，按保价额赔；电"
     "池/液体/压缩气体等禁限寄提前确认。收快递：贵重/易碎品**签收前当面验"
     "货**；驿站/快递柜代收属于合同变更需同意，可要求送货上门（送货上门是默"
     "计义务）；**隐私面单**或撕毁面单防信息泄露（姓名电话住址）。发生丢损："
     "先找快递公司索赔，协商不成向**邮政业申诉平台 12305**（国家邮政局申诉热"
     "线/网站）申诉——先向企业投诉 7 日无果或对处理不满才能申诉。",
     ["快递丢了一般怎么赔", "快递保价是什么意思", "签收前可以验货吗",
      "快递必须送货上门吗", "12305是什么电话", "快递单信息泄露"],
     ["问各快递公司价格对比", "问跨境海淘流程"],
     "atomic", "",
     "寄递=实名+开箱验视（法定）；贵重必保价（未保价按运费倍数赔常见 3-7 倍，保价费约 1%-3% 按声明价值赔）；收件可当面验货、驿站代收需同意可要求上门；面单涂抹隐私防泄露；丢损找公司→12305 邮政业申诉（先投诉 7 日）。"),
    ("kp_card_twobombs",
     "两弹一星",
     "人文通识知识点内容（人话接口）", "历史学",
     "「两弹一星」=**原子弹（后含氢弹）、导弹、人造地球卫星**——新中国 20 世"
     "纪五六十年代在极端困难条件下（苏联撤走专家+三年困难时期）自力更生搞出的"
     "国防尖端工程。时间线：**1964 年 10 月 16 日**第一颗**原子弹**在新疆罗布"
     "泊爆炸成功（打破核垄断）；1966 年导弹核武器（两弹结合）试验成功；**1967"
     " 年 6 月 17 日**第一颗**氢弹**（距原子弹仅 2 年 8 个月，速度世界第一）；"
     "**1970 年 4 月 24 日**「东方红一号」**卫星**升空（中国成为第五个独立发"
     "射卫星的国家，4 月 24 日后定为「中国航天日」）。代表人物：**钱学森**（"
     "「中国航天之父」，冲破美国阻挠 1955 年归国）、**邓稼先**（「两弹元勋」，"
     "隐姓埋名 28 年，临终「不要让人家把我们落得太远」）、钱三强、王淦昌、郭"
     "永怀（坠机时以身体护住数据资料）。意义：打破核讹诈、奠定大国地位；「两"
     "弹一星精神」=热爱祖国、无私奉献、自力更生、艰苦奋斗。",
     ["两弹一星指什么", "第一颗原子弹什么时候爆炸的", "东方红一号卫星",
      "钱学森邓稼先的贡献", "中国航天日是哪天", "两弹一星精神"],
     ["问核武器物理原理", "问当代航天工程（空间站/探月）"],
     "atomic", "",
     "两弹一星=原子弹(1964.10.16 罗布泊)+导弹(1966 两弹结合)+氢弹(1967.6.17 间隔 2 年 8 月世界最快)+东方红一号卫星(1970.4.24=现航天日)；钱学森 1955 破阻归国=航天之父，邓稼先隐姓埋名 28 年=两弹元勋，郭永怀护数据牺牲；意义=破核讹诈立大国地位。"),
    ("kp_card_iceflood",
     "凌汛",
     "人文通识知识点内容（人话接口）", "地理学",
     "凌汛=江河**冰凌阻塞**引起水位明显上涨的现象。发生需两个条件：①河流有"
     "**结冰期**；②河道**从低纬度流向高纬度**——秋末下游（高纬）先结冰、初春"
     "上游（低纬）先解冻，上游流下来的水/冰被下游冰层挡住，冰块堆积成**冰坝**"
     "抬高水位，甚至漫溢成灾（俗称「武开河」）。中国典型：**黄河**上游宁夏—内"
     "蒙古段（北纬越高越冷，河道自低纬流向高纬）和下游**山东段**（西南流向东"
     "北入海）——每年秋末冬初和初春两个时段最危险，需飞机轰炸破冰、水库调节"
     "流量防凌。长江珠江等南方河流冬季不结冰，**没有凌汛**。对比概念：桃汛（春"
     "汛）只是融雪涨水无冰坝；「凌汛期」黄河部分河段还会封河停航。",
     ["凌汛是怎么形成的", "黄河哪里有凌汛", "凌汛发生在什么时间",
      "为什么低纬流向高纬才有凌汛", "冰坝怎么处理", "长江有凌汛吗"],
     ["问黄河改道历史", "问水库调水调沙"],
     "atomic", "",
     "凌汛=冰凌阻塞致水位骤涨：条件=有结冰期+低纬流向高纬（下游先冻后融挡水上路）；黄河内蒙段+山东段每年初冬初春两发，用炸冰/水库调节防治；长江无结冰无凌汛；桃汛=融雪涨水无冰坝另算。"),
]

QUESTIONS = [
    ("QB-684", "快递丢了怎么赔偿？为什么寄贵重物品建议保价？", "生活常识", "技术直答",
     ["运费", "倍数", "保价", "声明价值", "赔偿"], "通识拓展140"),
    ("QB-685", "我国第一颗原子弹是什么时候在哪里爆炸成功的？「两弹一星」分别指什么？", "历史学", "技术直答",
     ["1964", "10月16日", "罗布泊", "原子弹", "导弹", "卫星"], "通识拓展140"),
    ("QB-686", "凌汛是怎么形成的？为什么长江没有凌汛？", "地理学", "技术直答",
     ["结冰", "冰坝", "低纬", "高纬", "不结冰"], "通识拓展140"),
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
                               "level:L2", "status:verified", "batch:通识拓展140"],
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
    bank["version"] = "v4.13"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
