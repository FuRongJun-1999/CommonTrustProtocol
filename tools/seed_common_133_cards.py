# -*- coding: utf-8 -*-
"""seed_common_133_cards.py · 通识拓展批次133知识卡+题库（幂等·两卡精批次）

133：生活常识-居民身份证号结构/数学-折扣与满减计算
KCCS 四要素+题干原句触发词。多轮候选预检命中已有覆盖（节气/奥运/时区/修辞等
全部已存在）——按「宁精勿滥」收敛为两卡精批次。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_idnumber",
     "居民身份证号码的结构",
     "生活常识知识点内容（人话接口）", "生活常识",
     "中国居民身份证号共 **18 位**，结构=地址码+出生日期码+顺序码+校验码：①前"
     "**6 位地址码**——省（2 位）+市（2 位）+县区（2 位），反映首次申领时的户"
     "籍所在地；②第 7-14 位**出生日期码**（YYYYMMDD，如 19900815）；③第 15-"
     "17 位**顺序码**——同一地区同一天出生者的编号，其中**第 17 位奇数为男性、"
     "偶数为女性**；④第 18 位**校验码**——由前 17 位按固定权重公式（ISO "
     "7064 MOD 11-2）计算得出，取值 0-9 或 **X**（X 即罗马数字 10——余数为 2"
     " 时校验码记作 X，保证一人一号唯一）。用途：银行开户/购票/住宿等实名核验"
     "；身份证号码是终身不变的法定身份标识。",
     ["身份证号码有多少位", "身份证第17位是什么意思", "身份证校验码X是什么",
      "身份证号码怎么看出性别", "地址码是什么", "身份证号会变吗"],
     ["问身份证丢失补办流程", "问户籍迁移手续"],
     "atomic", "",
     "身份证 18 位=6 位地址码(省市区·首次申领户籍地)+8 位出生日期(YYYYMMDD)+3 位顺序码(第 17 位奇男偶女)+1 位校验码(前 17 位按 ISO 7064 加权算，余 2 记 X=10)；终身唯一法定标识。"),
    ("kp_card_discount",
     "折扣与满减的计算",
     "基础科学知识点内容（人话接口）", "数学",
     "折扣计算：**打 n 折=按原价的 n/10 出售**——「八折」=原价×0.8，「7.5 折」"
     "=×0.75；折扣率=现价÷原价（现价 160/原价 200=8 折）。**满减对比**要看总"
     "价是否达门槛：原价 400 元，「满 300 减 100」实付 300（折合 7.5 折），「打"
     " 7 折」实付 280——**7 折更便宜**；若原价 310，满减后 210（约 6.8 折）反"
     "而更省——结论：满减必须**算实际折合率**再比较，且为凑单多买可能反亏。常"
     "见陷阱：①「先涨价后打折」——假把原价抬到 500 再「5 折」=250，可能比平时"
     "原价还贵（比价看历史价）；②「买一送一」≈半价的前提是两件单价相同；③满"
     "减不叠加时选优惠力度大的一种。核心口诀：**只看最终实付价÷原价**。",
     ["打八折怎么计算", "满300减100和7折哪个划算", "折扣率怎么算",
      "先涨价后打折的套路", "买一送一等于半价吗", "满减和折扣怎么比较"],
     ["问具体商家活动真假", "问会员积分规则"],
     "atomic", "",
     "折扣=n 折×原价 n/10（八折 0.8）；折扣率=现价÷原价；满减对比算实际折合率（400 元满减后 300=7.5 折 vs 7 折 280，7 折便宜）；陷阱=先涨后打/凑单反亏/买一送一≈半价需同单价；口诀=只看实付÷原价。"),
]

QUESTIONS = [
    ("QB-665", "居民身份证号码共有多少位？第 17 位数字能看出什么信息？校验码中的 X 表示什么？", "生活常识", "技术直答",
     ["18", "性别", "奇数", "偶数", "10", "校验"], "通识拓展133"),
    ("QB-666", "一件衣服原价 400 元，「满 300 减 100」和「打 7 折」两种优惠哪个最终实付更少？", "数学", "技术直答",
     ["7折", "280", "满减", "300", "少"], "通识拓展133"),
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
                               "level:L2", "status:verified", "batch:通识拓展133"],
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
    bank["version"] = "v4.6"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
