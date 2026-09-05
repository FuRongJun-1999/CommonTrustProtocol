# -*- coding: utf-8 -*-
"""seed_common_153_cards.py · 通识拓展批次153知识卡+题库（幂等）

153：历史学-戚继光抗倭/生活常识-高原反应/化学-「鬼火」的科学解释
KCCS 四要素+题干原句触发词。三重预检：戚继光/鬼火双库零覆盖；高原反应与
血液循环保温卡仅「缺氧」一词提及（主题未覆盖）划界。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_qijiguang",
     "戚继光抗倭",
     "人文通识知识点内容（人话接口）", "历史学",
     "明朝中期，日本浪人与中国海盗勾结侵扰东南沿海，史称「**倭寇**」之患。**戚"
     "继光**受命抗倭：①组建「**戚家军**」——在浙江义乌招募矿工农民，训练严"
     "明（「封侯非我意，但愿海波平」言志）；②创**鸳鸯阵**——12 人小队长短兵"
     "器配合（狼筅压阵+长枪+藤牌+镗钯），专克倭寇单兵刀法，灵活变阵；③**台"
     "州大捷**（1561）九战九捷荡平浙江倭患，后转战福建广东，与**俞大猷**等"
     "合力基本肃清东南沿海倭患（二人并称「俞龙戚虎」）；④著兵书《**纪效新书**"
     "》《练兵实纪》——实用主义练兵思想流传后世。戚继光是民族英雄（今山东蓬"
     "莱人），台州等地有戚公祠纪念。注意区分：同期「倭患」与后来万历朝鲜战争"
     "（援朝抗日）不同事件。",
     ["戚继光是哪个朝代的", "戚家军和鸳鸯阵", "台州大捷", "倭寇是什么",
      "俞龙戚虎", "纪效新书"],
     ["问万历援朝战争", "问郑成功（明清之际）"],
     "atomic", "",
     "戚继光抗倭=明朝中期荡平倭寇：戚家军(义乌矿工农民·「封侯非我意但愿海波平」)+鸳鸯阵 12 人长短兵器配合+台州九战九捷(1561)+俞大猷并称俞龙戚虎；兵书《纪效新书》；民族英雄。"),
    ("kp_card_altitudesick",
     "高原反应",
     "生活常识知识点内容（人话接口）", "生活常识",
     "高原反应（高反）=快速进入海拔 **2500 米以上**地区，因空气稀薄（大气压与"
     "氧分压随海拔升高而降低——拉萨约 3650m 含氧量≈海平面 60-70%）导致的急"
     "性不适。**症状**：头痛（最常见）、心慌气短、乏力、恶心失眠——多数人 24-"
     "48 小时内逐渐适应。**应对**：①**循序渐进**——阶梯式上升（「爬高睡低」："
     "白天爬升、夜里回低处睡）；②头两天不剧烈运动、不洗澡防感冒、戒酒、多喝"
     "水；③**吸氧**可快速缓解（便携氧瓶/酒店弥散供氧）；④药物：乙酰唑胺（处"
     "方药需遵医嘱）、布洛芬缓解头痛；红景天预防效果证据有限勿迷信；⑤**危险"
     "信号**——剧烈头痛呕吐、走路不稳、咳粉红色泡沫痰=**高原肺水肿/脑水肿**"
     "前兆，**立即下撤低海拔+就医**（唯一根治法是下撤）。儿童/重感冒/心肺疾病"
     "者慎入高海拔。",
     ["高原反应怎么缓解", "去拉萨会高反吗", "高原肺水肿前兆",
      "红景天能预防高反吗", "高反几天能适应", "阶梯式上升"],
     ["问慢性病人群高原旅行（就医评估）", "问登山技术"],
     "atomic", "",
     "高反=快速上 2500m+ 因氧分压降低：头痛心慌恶心，24-48h 多适应；应对=阶梯式上升爬高睡低+头两天缓动戒酒+吸氧+布洛芬/乙酰唑胺遵医嘱（红景天证据有限）；剧吐共济失调粉红泡沫痰=肺/脑水肿前兆立即下撤就医。"),
    ("kp_card_willowisp",
     "「鬼火」的科学解释",
     "基础科学知识点内容（人话接口）", "化学",
     "「鬼火」=**磷火**，化学自燃现象，与鬼魂无关：尸体腐烂时，骨骼中的磷化合"
     "物经细菌分解产生**磷化氢**（PH₃，含微量联膦 P₂H₄）气体逸出土壤——联膦"
     "燃点极低（约几十度甚至常温自燃），逸出时氧化燃烧发出**淡蓝绿色**的冷火"
     "焰，多见于夏季坟地/沼泽（高温利腐烂产气）。「鬼火追人」的真相：①火苗轻"
     "（气体燃烧），人走动带动**气流**，火随风飘看似「跟着人跑」——你越跑带"
     "的气流越大它跟得越紧，站住不动它也就停了；②磷火温度低（「冷火焰」），触"
     "碰一般不烫但含磷有毒勿碰；③白天也有只是光线强看不见。科学视角：一切"
     "「灵异」现象背后都有物理/化学/心理机制——磷火（化学）、海市蜃楼（光的折"
     "射）、「鬼压床」（睡眠瘫痪）皆如此。",
     ["鬼火是怎么形成的", "磷火为什么是绿色的", "鬼火为什么追人",
      "磷化氢自燃", "坟地的火是鬼吗", "鬼火烫不烫"],
     ["问海市蜃楼（光学）", "问其他灵异现象辟谣"],
     "atomic", "",
     "鬼火=磷火：尸骨磷化合物腐败产磷化氢(含联膦低燃点)自燃发淡蓝绿冷焰（夏夜坟地沼泽多见）；「追人」=人走带气流火随风飘、站住即停；低温不烫但含磷有毒勿碰；灵异现象均有科学机制（蜃景=折射/鬼压床=睡眠瘫痪）。"),
]

QUESTIONS = [
    ("QB-716", "戚继光是哪个朝代的抗倭名将？他创立的「鸳鸯阵」有什么特点？", "历史学", "技术直答",
     ["明朝", "明代", "戚家军", "12人", "长短兵器", "台州"], "通识拓展153"),
    ("QB-717", "高原反应是怎么引起的？出现哪些危险信号必须立即下撤就医？", "生活常识", "技术直答",
     ["海拔", "缺氧", "氧分压", "肺水肿", "脑水肿", "下撤"], "通识拓展153"),
    ("QB-718", "坟地里的「鬼火」到底是什么？为什么它看起来会「跟着人跑」？", "化学", "技术直答",
     ["磷化氢", "磷火", "自燃", "气流", "蓝色", "绿色"], "通识拓展153"),
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
                               "level:L2", "status:verified", "batch:通识拓展153"],
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
    bank["version"] = "v4.26"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
