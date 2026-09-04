# -*- coding: utf-8 -*-
"""seed_common_63_cards.py · 通识拓展批次63知识卡+题库（幂等）

63：物理学-噪声控制/化学-84消毒液/生物学-蜜蜂跳舞通讯/生活常识-电梯安全
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_noise3",
     "噪声与控制噪声三环节",
     "基础科学知识点内容（人话接口）", "物理学",
     "从物理角度：噪声是发声体做无规则振动发出的声音；从环保角度：妨碍人们正常"
     "休息学习工作的声音都是噪声（美妙的音乐打扰睡觉也是噪声）。声强等级用分贝"
     "（dB）表示：30-40dB ideal 安静、70dB 以上干扰谈话、90dB 长期损伤听力、爆"
     "炸声可达 150dB。控制噪声三环节（在声音产生与传递的路径上）：①防止噪声产"
     "生——声源处（摩托车消声器、市区禁鸣喇叭）；②阻断噪声传播——传播过程中"
     "（道路隔音墙/绿化带/双层玻璃）；③防止噪声入耳——人耳处（戴耳塞/耳罩）。"
     "考点辨析：隔音墙属于「传播过程」环节；「禁鸣喇叭」「装消声器」属于「声源"
     "处」。噪声也能利用：噪声除草/噪声除尘等探索。",
     ["控制噪声有三个环节", "什么是噪声", "分贝是什么单位",
      "隔音墙属于哪个环节", "多少分贝会损伤听力", "双层玻璃的隔音原理"],
     ["问声强等级计算", "问次声波危害"],
     "atomic", "",
     "噪声=无规则振动/妨碍生活；分贝 dB：70 干扰谈话·90 伤听力；控制三环节=声源处(消声器/禁鸣)→传播中(隔音墙绿化)→人耳处(耳塞)；隔音墙=传播环节。"),
    ("kp_card_84",
     "84 消毒液与消毒剂安全",
     "生活常识知识点内容（人话接口）", "生活常识",
     "84 消毒液的主要成分是次氯酸钠（NaClO）——强氧化性漂白杀菌（1984 年北京"
     "地坛医院研制故名「84」）。使用要点：需稀释（一般 1:100）后使用、对金属和彩"
     "色织物有腐蚀褪色作用、冷水现配现用（热水与久放会让有效氯流失）。**致命禁"
     "忌**：84 消毒液绝不能与洁厕灵（盐酸）混用——反应生成氯气（Cl₂），密闭卫"
     "生间内可致中毒窒息。也不能与酒精叠用（降低效果且可能生成有害物）。其他常"
     "见消毒剂：75% 酒精（皮肤小物件）、碘伏（伤口，不刺痛）、过氧乙酸、双氧水"
     "（伤口发泡）。消毒后通风、收好防儿童误食。次氯酸钠遇酸放氯气的原理与工业"
     "制氯气同源。",
     ["84消毒液的主要成分", "84消毒液和洁厕灵为什么不能混用", "84消毒液怎么稀释",
      "伤口消毒用什么", "次氯酸钠是什么", "84消毒液能洗彩色衣服吗"],
     ["问氯气毒性机制", "问消毒剂发展史"],
     "atomic", "",
     "84=次氯酸钠(NaClO·氧化漂白杀菌·1984 地坛医院)；稀释用/冷水现配/蚀金属褪色；**与洁厕灵(盐酸)混用产氯气致命**；伤口用碘伏；消毒后通风。"),
    ("kp_card_beedance",
     "蜜蜂的舞蹈语言",
     "基础科学知识点内容（人话接口）", "生物学",
     "蜜蜂用「舞蹈」传递蜜源信息——动物通讯的经典案例（弗里希研究，1973 年诺贝"
     "尔奖）：①圆圈舞——蜜源很近（百米内），原地转圈；②「8 字舞」（摆尾舞）—"
     "—蜜源较远，沿 8 字路径摆尾：**直跑方向**相对太阳的角度指示蜜源方位（太"
     "阳罗盘），**摆尾持续时间**指示距离（越久越远）；舞蹈越起劲表示蜜源越丰"
     "富。动物通讯其他方式：蚂蚁信息素（气味踪迹）、海豚声呐哨声、孔雀开屏（视"
     "觉求偶）、狼群嚎叫（声觉集结）、狗尿标记领地（化学标记）。通讯的意义：种"
     "群协作觅食/求偶/报警/御敌——社会性动物尤其依赖。人类信息素研究尚在早期"
     "（费洛蒙香水多为营销概念）。",
     ["蜜蜂跳舞传递什么信息", "8字舞是什么意思", "动物怎么通讯",
      "蚂蚁怎么找到食物的路", "动物通讯的方式有哪些", "蜜蜂的太阳罗盘"],
     ["问社会性昆虫分工", "问信息素化学"],
     "atomic", "",
     "蜂舞=动物通讯经典(弗里希诺奖)：圆舞=近；8字舞=直跑角度指方位(太阳罗盘)+摆尾时长指距离+劲头指丰富度；其他=信息素/声呐/开屏/嚎叫；社会性动物靠协作。"),
    ("kp_card_elevator",
     "乘坐电梯的安全常识",
     "生活常识知识点内容（人话接口）", "生活常识",
     "电梯（直梯）有多重安全保护：钢丝绳多根冗余（每根都能独立承重）、限速器+安"
     "全钳（超速时钳死导轨——**不会自由坠落**）、缓冲器（底部液压/弹簧缓冲）。"
     "万一电梯急停困人：①按警铃/对讲呼救，拨打 96333 电梯应急救援电话；②不要扒"
     "门爬出（电梯可能突然恢复运行，井道危险）；③背靠墙壁、屈膝、踮脚跟（缓冲冲"
     "击的标准姿势）——但牢记：现代电梯极难「坠楼」，被困本身不危险，窒息也不"
     "会发生（轿厢有通风口），慌乱自救反而危险。扶梯安全：握扶手、不倚靠、鞋带"
     "裙摆远离缝隙、儿童看护；扶梯「左行右立」渐被「禁止行走」取代（行走易摔）。"
     "火灾地震不要乘电梯（断电被困+烟囱效应）。",
     ["电梯下坠怎么自救", "电梯会自由落体吗", "被困电梯会窒息吗",
      "乘扶梯要注意什么", "为什么火灾不能坐电梯", "电梯困人打什么电话"],
     ["问电梯检验周期", "问安全钳机械结构"],
     "atomic", "",
     "电梯安全=多绳冗余+限速器安全钳(**不会自由坠**)+缓冲器；被困=按铃/96333·勿扒门·背墙屈膝；不会窒息(有通风)；扶梯握扶手禁行走；火灾地震勿乘梯。"),
]

QUESTIONS = [
    ("QB-385", "控制噪声有三个环节", "物理学", "技术直答",
     ["声源", "传播", "人耳"], "通识拓展63"),
    ("QB-386", "84消毒液的主要成分", "化学", "技术直答",
     ["次氯酸钠"], "通识拓展63"),
    ("QB-387", "蜜蜂跳舞传递什么信息", "生物学", "技术直答",
     ["蜜源", "方向", "距离"], "通识拓展63"),
    ("QB-388", "电梯下坠怎么自救", "生活常识", "技术直答",
     ["按警铃", "背靠墙", "屈膝"], "通识拓展63"),
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
                               "level:L2", "status:verified", "batch:通识拓展63"],
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
    bank["version"] = "v1.55"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
