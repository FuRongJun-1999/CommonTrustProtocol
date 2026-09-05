# -*- coding: utf-8 -*-
"""seed_common_135_cards.py · 通识拓展批次135知识卡+题库（幂等）

135：权益生活硬知识三连——消费者七天无理由退货/社保五险一金/劳动合同与试用期
KCCS 四要素+题干原句触发词。三重预检：三主题题库与卡库均零覆盖（全新域组）。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_consumer7day",
     "消费者权益与七天无理由退货",
     "生活常识知识点内容（人话接口）", "生活常识",
     "《消费者权益保护法》要点：①**网购七天无理由退货**——采用网络、电视、电"
     "话、邮购方式购的商品，自**收货之日起 7 日内**可无理由退货（商品应当完"
     "好）；**例外**：消费者定作的商品、鲜活易腐商品、在线下载或已拆封的音像"
     "制品与计算机软件、交付的报纸期刊（拆封易影响二次销售）。退货运费一般由"
     "买家承担，商家或商品有问题则由卖家承担；②**三包责任**——质量问题包修、"
     "包换、包退：7 日内出现质量问题可退货，15 日内可换货（三包期内两次修理仍"
     "不能正常使用可换或退）；③经营者欺诈可主张「退一赔三」（不足 500 元按 "
     "500 元）；④投诉渠道：与商家协商→平台介入→**12315** 热线/全国平台→消"
     "协调解→仲裁诉讼。维权先保留凭证：订单/聊天记录/发票/实物照片。",
     ["七天无理由退货", "网购退货几天", "哪些商品不能无理由退货",
      "三包是什么", "12315投诉", "退一赔三"],
     ["问线下实体店退货（无理由退货不强制，看商家承诺）", "问具体商品质量鉴定"],
     "atomic", "",
     "网购/电视/邮购商品收货 7 日内无理由退货（商品完好）；例外=定作/鲜活易腐/已拆音像软件/报纸期刊；质量三包=7 日退 15 日换、两修不好可退换；欺诈退一赔三不足 500 按 500；投诉 12315；维权先留凭证。"),
    ("kp_card_socialinsurance",
     "社保五险一金",
     "生活常识知识点内容（人话接口）", "生活常识",
     "「五险一金」=社会保障+住房保障：①养老保险；②医疗保险；③失业保险；④工"
     "伤保险（单位全额缴，个人不缴）；⑤生育保险（2019 年起与医保合并征缴）；"
     "「一金」=住房公积金（买房/租房/装修可提取，公积金贷款利率低于商业贷"
     "款）。缴费由**个人+单位共同承担**：个人通常缴养老 8%、医疗 2%左右、失"
     "业约 0.5%（从工资代扣），工伤生育全由单位缴。关键条件：养老保险**累计缴"
     "满 15 年**且达到法定退休年龄才能按月领养老金（多缴多得长缴长得）；医保"
     "缴满当地规定年限退休后可享终身医保待遇。社保是**法定强制**的，不缴或以"
     "现金补贴替代都违法——不是「单位给的福利」。",
     ["五险一金是什么", "社保包括哪些", "养老保险缴满多少年",
      "工伤保险个人要缴吗", "公积金有什么用", "社保是强制缴纳吗"],
     ["问养老金具体计算公式（各地参数不同）", "问商业保险选购"],
     "atomic", "",
     "五险=养老/医疗/失业/工伤(单位全缴)/生育(并入医保)+公积金(贷款利率低于商贷)；个人缴养老8%+医疗2%+失业约0.5%，从工资代扣；养老保险累计缴满15年+到退休年龄可领养老金；社保法定强制非单位福利。"),
    ("kp_card_laborcontract",
     "劳动合同与试用期规则",
     "生活常识知识点内容（人话接口）", "生活常识",
     "建立劳动关系应当订立**书面劳动合同**：自用工之日起 1 个月内签订；超过 1"
     " 个月不满 1 年未签的，单位应付**双倍工资**；满 1 年未签视为已订无固定期"
     "限合同。**试用期上限**与合同期挂钩：合同期 3 个月-1 年→试用期≤1 个月；"
     "1-3 年→≤2 个月；**3 年以上或无固定期限→≤6 个月**；同一单位与同一劳动"
     "者**只能约定一次**试用期（续签不得再设）。待遇底线：试用期工资≥转正工"
     "资的 80%且不低于当地最低工资标准，单位也须缴纳社保。解除：试用期辞职提"
     "前 **3 天**通知，转正后提前 **30 天**书面通知即可，无需单位「批准」；"
     "试用期辞退员工也须证明「不符合录用条件」等法定情形。",
     ["试用期最长多少个月", "不签劳动合同怎么办", "试用期工资标准",
      "试用期辞职提前几天", "双倍工资什么情况", "试用期要交社保吗"],
     ["问竞业限制与违约金细节", "问劳动仲裁具体流程"],
     "atomic", "",
     "书面合同用工 1 月内签，超 1 月不满 1 年未签=双倍工资；试用期上限=合同 3 月-1 年→1 月/1-3 年→2 月/3 年以上→6 个月，同一单位只能一次；试用期工资≥转正 80%且≥最低工资+须缴社保；辞职试用期 3 天/正式 30 天书面即可；试用期辞退须法定理由。"),
]

QUESTIONS = [
    ("QB-670", "网购商品几天内可以无理由退货？哪些商品不适用七天无理由退货？", "生活常识", "技术直答",
     ["七天", "7日", "定作", "鲜活", "完好"], "通识拓展135"),
    ("QB-671", "「五险一金」包括哪些？养老保险累计缴满多少年才能按月领养老金？", "生活常识", "技术直答",
     ["养老", "医疗", "失业", "工伤", "生育", "公积金", "15"], "通识拓展135"),
    ("QB-672", "签订三年期劳动合同，试用期最长不得超过几个月？试用期内辞职需要提前几天通知？", "生活常识", "技术直答",
     ["6", "六个月", "3天", "三天"], "通识拓展135"),
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
                               "level:L2", "status:verified", "batch:通识拓展135"],
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
    bank["version"] = "v4.8"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
