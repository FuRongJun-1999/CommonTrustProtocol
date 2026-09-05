# -*- coding: utf-8 -*-
"""seed_common_117_cards.py · 通识拓展批次117知识卡+题库（幂等）

117：生活常识-交通标志识别/生活常识-网络安全防诈骗/生活常识-酗酒的危害
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_trafficsign",
     "常见交通标志识别",
     "生活常识知识点内容（人话接口）", "生活常识",
     "交通标志按功能分三大类：①**警告标志**——黄底黑边三角形（顶角朝上），警"
     "告前方危险：注意行人/急弯/陡坡/学校区域；②**禁令标志**——白底红圈红杠，"
     "禁止或限制：禁止通行/限速 40/禁止停车/禁止鸣笛；③**指示标志**——蓝底白"
     "图圆形或矩形，指示允许：直行/右转/机动车道/人行横道。辅助：信号灯（红灯"
     "停绿灯行黄灯亮了等一等）、交通标线（实线不可压、虚线可变道）。安全口诀："
     "「红灯停、绿灯行、黄灯亮了等一等」；行人走斑马线/过街天桥，不在马路上嬉"
     "戏；骑车戴头盔（一盔一带安全守护行动）。",
     ["常见的交通标志有哪些", "警告标志是什么样子", "禁令标志和指示标志的区别",
      "红灯停绿灯行", "过马路要走什么", "骑车为什么要戴头盔"],
     ["问交通信号灯历史", "问高速公路标志"],
     "atomic", "",
     "交通标志三类：警告(黄底三角·注意危险)/禁令(白底红圈·禁止限制)/指示(蓝底·允许通行)；信号灯红停绿行黄等；实线禁压虚线可变；一盔一带。"),
    ("kp_card_netfraud",
     "网络安全：防诈骗常识",
     "生活常识知识点内容（人话接口）", "生活常识",
     "常见网络诈骗形式：①钓鱼链接/假冒网站（仿冒银行购物网站骗账号密码）——"
     "不点陌生链接、核对官方域名；②冒充客服退款诈骗（谎称商品质量问题退款，实"
     "则骗取验证码）——验证码等于密码，绝不告诉任何人；③刷单兼职诈骗（先小额返"
     "利后大额卷款——刷单本身违法）；④冒充公检法（谎称涉案要求转账到「安全账户"
     "」——公检法不会电话办案要求转账）；⑤杀猪盘（网络交友诱导投资赌博）。防骗"
     "三不一多：不轻信、不透露、不转账，多核实。国家反诈中心 APP 可预警诈骗电"
     "话。被骗后立即：拨打 110、保留证据（聊天记录/转账凭证）、联系银行冻结。",
     ["常见的网络诈骗有哪些", "什么是杀猪盘", "冒充客服退款怎么识别",
      "验证码能告诉别人吗", "被骗了怎么办", "国家反诈中心APP"],
     ["问个人信息保护法", "问电信诈骗话术演变"],
     "atomic", "",
     "常见诈=钓鱼链接/冒充客服退款/刷单兼职/假公检法/杀猪盘；口诀三不一多=不轻信不透露不转账多核实；验证码=密码绝不给；反诈 APP 预警；被骗即 110 留证据。"),
    ("kp_card_alcoholharm",
     "酗酒的危害",
     "生活常识知识点内容（人话接口）", "生活常识",
     "酗酒（过量饮酒）的危害：①**肝脏损伤**——酒精 90% 在肝脏代谢：脂肪肝→酒"
     "精性肝炎→肝硬化（三部曲），严重可致肝癌；②**神经系统损害**——损害大脑"
     "细胞（记忆力减退/痴呆风险升高）、酒后驾驶极易引发交通事故（酒驾入刑）；③"
     "**消化系统**——胃炎/胃溃疡/胰腺炎；④**胎儿酒精综合征**——孕妇饮酒致胎"
     "儿智力障碍、面部畸形（无安全剂量）；⑤**心血管**——少量红酒有益的说法已"
     "被最新研究否定（ Lancet：最安全的饮酒量是零）。中国建议：不劝酒、不拼"
     "酒、酒后不开车。酒精致癌：国际癌症研究机构（IARC）将酒精列为一类致癌物。",
     ["酗酒的危害有哪些", "酒精对肝脏的损害", "酒后为什么不能开车",
      "孕妇饮酒有什么危害", "少量喝酒有益健康吗", "酒精是一类致癌物吗"],
     ["问酒精代谢酶差异", "问戒酒综合征"],
     "atomic", "",
     "酗酒三害=肝(脂肪肝→肝硬化→肝癌)+神经(记忆减退·酒驾入刑)+胎儿酒精综合征(孕妇无安全剂量)；Lancet：最安全饮酒量=零；IARC 一类致癌物；不劝酒不拼酒。"),
]

QUESTIONS = [
    ("QB-605", "常见的交通标志有哪些", "生活常识", "技术直答",
     ["警告标志", "禁令标志", "指示标志"], "通识拓展117"),
    ("QB-606", "常见的网络诈骗有哪些", "生活常识", "技术直答",
     ["钓鱼", "杀猪盘", "冒充客服"], "通识拓展117"),
    ("QB-607", "酗酒的危害有哪些", "生活常识", "技术直答",
     ["肝硬化", "神经", "胎儿"], "通识拓展117"),
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
                               "level:L2", "status:verified", "batch:通识拓展117"],
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
    bank["version"] = "v3.1"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
