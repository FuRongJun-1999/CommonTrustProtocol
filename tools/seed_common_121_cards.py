# -*- coding: utf-8 -*-
"""seed_common_121_cards.py · 通识拓展批次121知识卡+题库（幂等）

121：物理学-眼镜度数的计算/化学-体液pH与生命活动/地理学-中国九大商品粮基地
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_glassdeg",
     "眼镜度数的计算",
     "基础科学知识点内容（人话接口）", "物理学",
     "眼镜度数=镜片**焦距的倒数**×100（度数 D=100/f，f 单位米）——焦距 0.5m 的"
     "镜片度数为 200 度。近视镜（凹透镜）度数为负值（-300 度=f=-0.33m），远视/"
     "老花镜（凸透镜）为正值。度数与焦距成反比：度数越高焦距越短、折光越强。换"
     "算例：400 度近视镜 f=-0.25m。验光配镜原则：度数宁低勿高（过矫导致疲劳加"
     "深近视）；双眼度数差>250 度为屈光参差（大脑融像困难）。隐形眼镜度数与框"
     "镜略有差异（贴角膜更近，度数略低）。",
     ["眼镜度数是怎么计算的", "度数与焦距的关系", "近视镜度数是负的吗",
      "400度近视镜焦距是多少", "配镜为什么要宁低勿高", "什么是屈光参差"],
     ["问散光轴位", "问渐进多焦点镜片"],
     "atomic", "",
     "眼镜度数 D=100/f(焦距 m)：近视凹透镜负值(−300 度=f−0.33m)；度数越高焦距越短；配镜宁低勿高防过矫；双眼差>250 度=屈光参差。"),
    ("kp_card_bodyph",
     "体液pH与生命活动",
     "基础科学知识点内容（人话接口）", "化学",
     "人体体液 pH 各有定值且必须维持稳定：①**血液 pH 7.35-7.45**（弱碱性，波"
     "动超 0.4 即酸中毒/碱中毒危及生命）——靠缓冲对（碳酸/碳酸氢钠等）+呼吸排"
     " CO₂+肾脏排酸三重机制稳定；②胃液 pH 0.9-1.5（强酸，消化杀菌）；③小肠液"
     " pH 约 7.6（弱碱，消化吸收）；④尿液 pH 4.6-8.0（波动最大——肾脏排酸调"
     "节）。食物「酸碱性」不影响血液 pH（伪科学 acidbody 呼应）：代谢产生的酸由"
     "缓冲系统即时中和。「碱性体质」说法无科学依据。酸碱平衡失调：糖尿病酮症酸"
     "中毒/高原缺氧呼吸性碱中毒——是疾病结果不是原因。",
     ["人体血液的pH是多少", "胃液的pH是多少", "什么是酸中毒",
      "食物能改变血液pH吗", "体液pH如何维持稳定", "尿液pH范围"],
     ["问缓冲对化学原理", "问酸碱平衡失调类型"],
     "atomic", "",
     "体液 pH 各有定值：血液 7.35-7.45(缓冲+呼吸+肾三重稳定)/胃液 0.9-1.5/尿液 4.6-8.0 波动最大；食物不改血液 pH；酸碱中毒=疾病结果非原因。"),
    ("kp_card_grainbase",
     "中国九大商品粮基地",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国九大商品粮基地（提供商品粮的集中产区）：①太湖平原；②鄱阳湖平原；③"
     "洞庭湖平原；④江汉平原；⑤江淮地区；⑥珠江三角洲；⑦松嫩平原（黑龙江——玉"
     "米大豆）；⑧三江平原（黑龙江东北角——开荒北大仓）；⑨成都平原（「天府之国"
     "」）。分布规律：**都在东部季风区**（南方多为水稻，北方为小麦玉米），因为"
     "水热充足、地势平坦、土壤肥沃（东北黑土/长江中下游水稻土）、人口稠密农业"
     "历史悠久。共同威胁：城市化占地、水资源短缺（华北）、黑土退化（东北）。保"
     "护：永久基本农田制度、耕地红线 18 亿亩。",
     ["中国九大商品粮基地是哪些", "松嫩平原产什么", "成都平原为什么叫天府之国",
      "商品粮基地分布在哪", "三江平原在哪里", "商品粮基地的共同点"],
     ["问东北黑土保护", "问粮食主产区政策"],
     "atomic", "",
     "九大商品粮基地=太湖/鄱阳/洞庭/江汉/江淮/珠三角/松嫩/三江/成都平原：全在东部季风区·南方水稻北方玉米大豆；三江平原=北大仓；威胁=城市化缺水黑土退化。"),
]

QUESTIONS = [
    ("QB-620", "眼镜度数是怎么计算的", "物理学", "技术直答",
     ["焦距", "倒数"], "通识拓展121"),
    ("QB-621", "人体血液的pH是多少", "化学", "技术直答",
     ["7.35", "7.45", "弱碱性"], "通识拓展121"),
    ("QB-622", "中国九大商品粮基地是哪些", "地理学", "技术直答",
     ["松嫩", "三江", "成都", "太湖"], "通识拓展121"),
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
                               "level:L2", "status:verified", "batch:通识拓展121"],
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
    bank["version"] = "v3.5"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
