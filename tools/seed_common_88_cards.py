# -*- coding: utf-8 -*-
"""seed_common_88_cards.py · 通识拓展批次88知识卡+题库（幂等）

88：物理学-电压/化学-物质的变化与性质/生物学-安全用药/地理学-中国的邻海
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_voltage",
     "电压：形成电流的原因",
     "基础科学知识点内容（人话接口）", "物理学",
     "电压（U）是使电路中形成**电流的原因**——类比水压：水位差使水流动，电位差"
     "使电荷定向移动；**电源**就是提供电压的装置（把其他形式能转化为电能）。单位"
     "伏特（V）——纪念伏特发明第一个电池（伏打电堆）。常见电压值：一节干电池 "
     "1.5V、家庭电路 220V、对人体安全电压不高于 36V、一节锂电池约 3.7V。电压表："
     "并联在被测元件两端测电压（与电流表串联用法相反）；电压表内阻极大（相当于"
     "断路，直接接电源两端不会烧表）；电流表内阻极小（相当于导线，**绝不能直接"
     "接电源两端**——短路烧表）。",
     ["电压是形成电流的原因", "电压的单位", "电压表和电流表的区别",
      "一节干电池的电压", "为什么电流表不能直接接电源", "什么是电位差"],
     ["问欧姆定律 U=IR", "问串并联电压分布"],
     "atomic", "",
     "电压 U=形成电流的原因(电源提供·水压类比)；单位伏特(干电池 1.5V/家庭 220V/安全≤36V)；电压表并联测压·内阻大可接电源两端；电流表串联·内阻小禁直连电源。"),
    ("kp_card_changes",
     "物质的变化与性质",
     "基础科学知识点内容（人话接口）", "化学",
     "**物理变化**与**化学变化**：无新物质生成的是物理变化（冰熔化、水蒸发、灯"
     "泡发光、纸张撕碎、酒精挥发、铁丝弯折）；有新物质生成的是化学变化（燃烧、"
     "生锈、食物腐败、呼吸作用、酿酒——常伴随发光/放热/变色/生成气体或沉淀）。"
     "**物理性质**与**化学性质**：物质不需要发生化学变化就表现的性质=物理性质"
     "（颜色/状态/气味/熔点/沸点/密度/硬度/溶解性/导电导热性）；物质在化学变化中"
     "表现的性质=化学性质（可燃性/氧化性/还原性/稳定性/酸碱性/毒性）。判断口诀"
     "：「性质」是物质固有能力描述（「能」「会」「易」「可以」）、「变化」是正在"
     "发生的过程——木炭能燃烧是化学性质，木炭正在燃烧是化学变化。",
     ["物理变化和化学变化的区别", "物理性质和化学性质怎么区分",
      "蜡烛熔化是什么变化", "挥发性是物理性质还是化学性质", "判断化学变化的依据",
      "什么是物质的性质"],
     ["问质量守恒衔接", "问变化与性质例题"],
     "atomic", "",
     "变化=过程(物理无新物质/化学有新物质·伴随能变)；性质=固有能力(物理不需变化表现·化学变化中表现)；口诀「能会易可」=性质描述；判断化学变化根本依据=有无新物质。"),
    ("kp_card_safemed",
     "安全用药常识",
     "生活常识知识点内容（人话接口）", "生活常识",
     "药品分两类：**处方药**（Rx）——必须凭执业医师处方购买，需医生指导使用；"
     "**非处方药**（OTC，又分甲类红色 OTC/乙类绿色 OTC）——可自行判断购买，按说"
     "明书使用。安全用药原则：①对症下药，不盲目；②看清说明书（适应症/用法用"
     "量/禁忌/不良反应）；③注意「慎用/忌用/禁用」的区别（禁用=绝对不可用）；④"
     "不滥用抗生素（对病毒无效+催生耐药菌——需处方）；⑤过期药不能吃（定期清家"
     "庭药箱）。特殊人群：孕妇/儿童/老人用药需格外谨慎（儿童不是缩小版成人——"
     "剂量按体重计算）。家庭药箱：常备退烧药/碘伏/创可贴/体温计/纱布，避光阴凉"
     "保存、定期清理。误区：输液好得快（能口服不肌注、能肌注不输液）。",
     ["处方药和非处方药的区别", "OTC是什么意思", "为什么不滥用抗生素",
      "慎用忌用禁用的区别", "儿童用药注意什么", "家庭药箱常备什么"],
     ["问药物相互作用", "问疫苗与药物关系"],
     "atomic", "",
     "处方药(Rx 需医嘱)vs 非处方药(OTC 红甲绿乙可自购)；禁用=绝对不可用；抗生素处方+不滥用(病毒无效·耐药菌)；儿童按体重给药；能口服不肌注·能肌注不输液。"),
    ("kp_card_seas",
     "中国的四海",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国濒临的海域自北向南：**渤海、黄海、东海、南海**；台湾岛东岸直临太平"
     "洋。①渤海——中国的内海（被辽东半岛与山东半岛环抱），有黄河入海口，著名的"
     "长芦盐场；②黄海——因黄河历史上携带泥沙入海使水色黄而得名（现在泥沙主要"
     "经渤海）；③东海——大陆架宽广，舟山渔场（中国最大渔场）所在，东海大桥通"
     "洋山深水港；④南海——面积最大（约 350 万平方公里）、水温最高，油气与渔业"
     "资源丰富，南海诸岛（东沙/西沙/中沙/南沙）散布其中。内海与领海概念：渤海"
     "和琼州海峡是中国的内海；领海宽度 12 海里。海洋经济：港口航运（上海港吞吐量"
     "世界第一）、渔业、油气、海盐。",
     ["中国濒临哪些海洋", "中国的内海是哪两个", "中国最大的渔场",
      "渤海为什么是内海", "南海的面积", "舟山渔场在哪里"],
     ["问海洋权益维护", "问海岸线类型"],
     "atomic", "",
     "四海自北南=渤海(内海·长芦盐场)黄海(泥沙得名)东海(舟山渔场·最大)南海(350 万km²·最大最深·诸岛)；内海还有琼州海峡；领海 12 海里；上海港吞吐全球第一。"),
]

QUESTIONS = [
    ("QB-485", "电压是形成电流的原因", "物理学", "技术直答",
     ["电源", "电位差"], "通识拓展88"),
    ("QB-486", "物理性质和化学性质怎么区分", "化学", "技术直答",
     ["是否需要化学变化"], "通识拓展88"),
    ("QB-487", "处方药和非处方药的区别", "生活常识", "技术直答",
     ["处方", "OTC"], "通识拓展88"),
    ("QB-488", "中国濒临哪些海洋", "地理学", "技术直答",
     ["渤海", "黄海", "东海", "南海"], "通识拓展88"),
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
                               "level:L2", "status:verified", "batch:通识拓展88"],
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
    bank["version"] = "v1.80"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
