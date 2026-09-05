# -*- coding: utf-8 -*-
"""seed_common_143_cards.py · 通识拓展批次143知识卡+题库（幂等·两卡精批次）

143：地理学-厄尔尼诺与拉尼娜/生活常识-个人所得税
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖（变态发育/成语等候选
命中已有覆盖当场弃选）。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_elnino",
     "厄尔尼诺与拉尼娜",
     "人文通识知识点内容（人话接口）", "地理学",
     "厄尔尼诺（El Niño，西班牙语「圣婴」）=**赤道中东太平洋海水异常升温**的"
     "气候现象，约 2-7 年不规则发生一次，每次持续 9-12 个月左右。升温扰动大气"
     "环流，引发全球连锁异常：①秘鲁渔场减产——正常年份冷水上翻带来营养盐，"
     "厄尔尼诺抑制上翻，鳀鱼大量死亡；②西太平洋（澳大利亚/印尼）高温干旱、"
     "森林大火；③我国常呈现**「南涝北旱」倾向**、易现暖冬、台风生成偏少。**拉"
     "尼娜（La Niña，「圣女」）**=相反现象——海水**异常降温**，影响大体反向"
     "（我国易现「南旱北涝」、冷冬概率升高）。注意区分：厄尔尼诺/拉尼娜是**年"
     "际尺度的自然波动**（海水温度起伏），全球变暖是**长期趋势**（温室气体），"
     "两者叠加使极端天气更频繁。",
     ["厄尔尼诺是什么现象", "厄尔尼诺对中国的影响", "拉尼娜和厄尔尼诺的区别",
      "圣婴现象", "秘鲁渔场为什么减产", "南涝北旱的原因"],
     ["问全球变暖成因（温室气体趋势）", "问具体年份预测"],
     "atomic", "",
     "厄尔尼诺=赤道中东太平洋海水异常升温（2-7 年一遇）：秘鲁渔场减产+澳洲印尼干旱+我国南涝北旱暖冬倾向；拉尼娜=相反的异常降温（南旱北涝冷冬）；两者为年际自然波动≠全球变暖（长期趋势）。"),
    ("kp_card_incometax",
     "个人所得税怎么看",
     "生活常识知识点内容（人话接口）", "生活常识",
     "工资个税算法：应纳税所得额=税前工资−**5000 元/月（6 万/年）基本减除费"
     "用**（俗称起征点）−「三险一金」个人缴纳部分−**专项附加扣除**−其他免税"
     "收入，再按**超额累进税率 3%-45%** 计税。**专项附加扣除**七项（定额扣，"
     "使很多人实际起征点远超 5000）：①子女教育（每孩每月 2000 元）②3 岁以下"
     "婴幼儿照护（2000 元/孩/月）③继续教育④大病医疗⑤住房贷款利息（1000 元"
     "/月）或住房租金（800-1500 元按城市）⑥赡养老人（3000 元/月分摊）⑦个人"
     "养老金。**年度汇算**：每年 3-6 月在「个人所得税」App 汇总全年四项综合所"
     "得（工资/劳务报酬/稿酬/特许权使用费）多退少补——很多人能**退税**。日"
     "常发薪时单位代扣代缴（累计预扣法）。",
     ["个人所得税起征点是多少", "专项附加扣除有哪些", "个税怎么计算",
      "年度汇算退税是什么", "工资5000要交税吗", "赡养老人扣除多少"],
     ["问经营所得与财产租赁计税", "问年终奖计税方式选择"],
     "atomic", "",
     "个税=（税前工资−5000/月−三险一金−专项附加扣除）×3%-45% 超额累进；专项附加七项=子女教育/婴幼儿照护各 2000/继续教育/大病医疗/房贷利息 1000 或房租 800-1500/赡养老人 3000/个人养老金；3-6 月个税 App 年度汇算多退少补。"),
]

QUESTIONS = [
    ("QB-693", "厄尔尼诺现象指的是哪片海域的什么异常？它对我国天气常有什么影响？", "地理学", "技术直答",
     ["赤道", "太平洋", "升温", "海水", "南涝北旱"], "通识拓展143"),
    ("QB-694", "个人所得税的起征点（基本减除费用）是每月多少元？专项附加扣除包括哪些项目？", "生活常识", "技术直答",
     ["5000", "五千", "子女教育", "赡养老人", "房贷", "房租"], "通识拓展143"),
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
                               "level:L2", "status:verified", "batch:通识拓展143"],
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
    bank["version"] = "v4.16"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
