# -*- coding: utf-8 -*-
"""seed_common_150_cards.py · 通识拓展批次150知识卡+题库（幂等·两卡精批次）

150：生活常识-医保报销常识/生活常识-科学减重
KCCS 四要素+题干原句触发词。三重预检：医保报销/异地就医双库零覆盖（五险一
金卡为缴存角度）；减肥零覆盖（基础代谢老卡为生理概念角度，划界）。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_medirefund",
     "医保报销常识",
     "生活常识知识点内容（人话接口）", "生活常识",
     "医保使用要点：①**两类身份**——职工医保（单位+个人共同缴，有个人账户，"
     "门诊药店刷卡）vs 居民医保（一年一缴几百元，无个人账户，住院门诊统筹报"
     "销）；②报销结构=**起付线**（以下自付，几百到千余元）+**报销比例**（在职"
     "约 70-90%，医院级别越高比例越低）+**封顶线**（年度上限）；③**医保目"
     "录**——甲类药全额纳入报销、乙类药部分自付、**目录外自费**（进口药/营养"
     "液多为自费——所以有商业医疗险补充）；④**异地就医**——提前在「国家医保"
     "服务平台」App/小程序**备案**，备案后可在就医地联网医院直接结算（无需垫"
     "付回老家报销）；⑤医保卡**不外借**（冒名就医骗保违法且记录影响自己投保）。",
     ["医保怎么报销", "起付线封顶线是什么", "异地就医怎么备案",
      "甲类药乙类药区别", "居民医保和职工医保区别", "医保卡可以借给别人吗"],
     ["问商业保险配置", "问慢性病门诊特殊病种"],
     "atomic", "",
     "医保=职工(个人账户刷卡)vs 居民(一年一缴统筹报销)；报销结构=起付线以下自付+比例 70-90%(医院级别越高越低)+封顶线；甲类全报乙类部分自付目录外自费；异地就医先 App 备案联网直接结算；医保卡禁外借（骗保违法）。"),
    ("kp_card_healthylow",
     "科学减重",
     "生活常识知识点内容（人话接口）", "生活常识",
     "减重的能量原理=**热量缺口**（消耗>摄入）——1kg 脂肪约合 7700kcal，每天"
     "缺口 500kcal 约每周减 0.5kg（健康速度每周 0.5-1kg）。可行做法：①**饮食**"
     "——控制总热量+高蛋白（保肌肉增饱腹）+多蔬菜，少吃精制糖与油炸（一杯奶"
     "茶≈慢跑 1 小时）；②**运动**——有氧（快走/慢跑/游泳）燃脂+**力量训练**"
     "增肌提高**基础代谢**（肌肉多=躺着的消耗也高）；③**睡眠与压力**——熬夜"
     "扰乱瘦素/饥饿素让人更想吃；④拒绝极端方法——**极低热量节食**掉的多是水"
     "和肌肉、代谢下降、恢复饮食即**反弹**；「减肥药」多泻药/抑制食欲有风险。"
     "BMI=体重(kg)÷身高²(m²)，18.5-23.9 为中国成人正常范围；减重目标先设 5%-"
     "10%（即可显著改善血压血糖）。体重不是唯一指标——围度/体脂率更说明问题。",
     ["怎么减肥才科学", "减重每周多少合适", "节食为什么反弹",
      "BMI怎么计算", "基础代谢与减肥", "力量训练能减肥吗"],
     ["问特定疾病人群减重（需医生指导）", "问健身增肌计划"],
     "atomic", "",
     "科学减重=热量缺口(1kg 脂肪≈7700kcal，每周减 0.5-1kg)+高蛋白多蔬+有氧燃脂+力量增肌提基础代谢+睡够防激素紊乱；极端节食掉肌肉降代谢必反弹；BMI=kg/m²，18.5-23.9 正常，先减 5-10% 即显著获益。"),
]

QUESTIONS = [
    ("QB-710", "医保报销中的「起付线」和「封顶线」分别是什么意思？异地就医怎么直接结算？", "生活常识", "技术直答",
     ["自付", "上限", "备案", "联网", "结算"], "通识拓展150"),
    ("QB-711", "为什么极端节食减肥容易反弹？健康减重的合理速度是每周多少？", "生活常识", "技术直答",
     ["肌肉", "基础代谢", "下降", "反弹", "0.5", "1kg"], "通识拓展150"),
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
                               "level:L2", "status:verified", "batch:通识拓展150"],
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
    bank["version"] = "v4.23"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
