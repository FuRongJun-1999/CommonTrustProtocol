# -*- coding: utf-8 -*-
"""seed_common_145_cards.py · 通识拓展批次145知识卡+题库（幂等·两卡精批次）

145：生活常识-酒店入住常识/生活常识-点外卖的食品安全
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖（体检指标候选命中
既有老卡当场弃选）。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_hotelcheck",
     "酒店入住常识",
     "生活常识知识点内容（人话接口）", "生活常识",
     "入住流程与要点：①**实名登记**——所有入住人都要登记身份证（《旅馆业治安"
     "管理办法》要求一证一住，带家人朋友入住需全员登记）；②**押金/预授权**——"
     "入住收押金（现金或信用卡预授权冻结），退房无消费则原路退回（预授权解冻"
     "需几个工作日）；③**退房时间**——行业惯例**次日 12:00 前**（会员/新规部"
     "分酒店延至 14:00），超时半天房费；入住一般 14:00 后；④卫生自查——进房"
     "先烧一壶开水烫洗杯具，检查床品是否换新（有无头发/折痕）、马桶浴缸；⑤**"
     "安全**——进门先看消防通道位置和灭火器；猫眼反装检查；门锁反扣；⑥正规"
     "渠道预订、保留订单与发票（报销/维权凭证）。退房查房：多数连锁酒店已免查"
     "房（信用体系），但损坏物品仍需赔偿。",
     ["酒店退房时间是几点", "住酒店要登记所有人身份证吗", "酒店押金什么时候退",
      "住酒店怎么检查卫生", "酒店查房吗", "预授权是什么意思"],
     ["问具体酒店比价", "问酒店星级评定标准"],
     "atomic", "",
     "酒店入住=全员实名登记(一证一住)+押金或信用卡预授权(解冻数日)+惯例 12:00 前退房(会员可延 14 点)；卫生自查烫杯查床品；进门先看消防通道+反扣门锁；正规渠道留凭证，连锁多免查房但损坏照赔。"),
    ("kp_card_takeoutfood",
     "点外卖的食品安全",
     "生活常识知识点内容（人话接口）", "生活常识",
     "点外卖看四点：①**商家资质**——平台店铺页查「食品安全档案」：营业执照+**"
     "食品经营许可证**必须公示（无证黑作坊风险高，实体店可查实际地址与评价）；"
     "②**食安封签**——配送包装上的一次性封签（撕毁不可复原）防配送途中污染，"
     "无封签且包装破损可**拒收**；③**及时食用**——收到后 2 小时内吃完（夏季 1"
     " 小时），剩菜冷藏不隔餐——外卖在常温下细菌繁殖极快（6-60°C 是「危险温"
     "度带」）；④**维权**——变质/异物拍照留证，平台投诉可退赔（平台有**先行"
     "赔付**机制），严重的向 12315/12331（食药投诉）举报。健康提示：外卖普遍"
     "高油高盐，长期当主餐注意营养均衡；奶茶「无糖」也含糖（奶茶原料本身含"
     "糖）——看营养成分表。",
     ["点外卖怎么看商家靠不靠谱", "食安封签是什么", "外卖可以拒收吗",
      "外卖变质怎么维权", "外卖放多久不能吃", "12331是什么电话"],
     ["问外卖骑手行业问题", "问预制菜争议"],
     "atomic", "",
     "点外卖四看=商家资质(营业执照+食品经营许可证公示)+食安封签(破损可拒收)+2 小时内食用(夏季 1 小时，6-60°C 危险温度带细菌快繁)+维权留证(平台先行赔付，12315/12331)；外卖高油高盐注意均衡。"),
]

QUESTIONS = [
    ("QB-697", "酒店的退房时间一般是几点？入住酒店为什么所有人都要登记身份证？", "生活常识", "技术直答",
     ["12", "十二点", "实名", "登记", "治安"], "通识拓展145"),
    ("QB-698", "点外卖时怎么判断商家资质是否正规？食安封签破损可以拒收吗？", "生活常识", "技术直答",
     ["营业执照", "食品经营许可证", "公示", "封签", "拒收"], "通识拓展145"),
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
                               "level:L2", "status:verified", "batch:通识拓展145"],
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
    bank["version"] = "v4.18"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
