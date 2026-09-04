# -*- coding: utf-8 -*-
"""seed_common_54_cards.py · 通识拓展批次54知识卡+题库（幂等）

54：物理学-弹簧测力计/化学-肥皂去油污/生物学-嫁接繁殖/地理学-中国省级行政区
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_springf",
     "弹簧测力计的原理",
     "基础科学知识点内容（人话接口）", "物理学",
     "弹簧测力计测力的原理：在弹性限度内，弹簧的伸长量与所受拉力**成正比**（胡"
     "克定律 F=kx）——拉力越大伸得越长，刻度均匀。使用要点：①使用前调零（指针"
     "对准零刻度）；②看清量程与分度值，所测力不能超过量程（超量程弹簧「过劳」"
     "不能恢复，测力计报废）；③沿力的方向拉、避免摩擦。弹力产生条件：物体发生"
     "弹性形变（恢复原状的力）；常见弹力：支持力/压力/拉力都是弹力。弹性与塑性："
     "弹簧撤力恢复=弹性，橡皮泥捏了不恢复=塑性。其他应用：握力计、拉力器、电子"
     "秤里的应变片（更精密的力电转换）。",
     ["弹簧测力计的原理", "使用弹簧测力计的注意事项", "什么是弹性限度",
      "弹力是怎么产生的", "弹簧测力计能测重力吗", "胡克定律是什么"],
     ["问胡克定律计算题", "问弹力方向判断"],
     "atomic", "",
     "测力计原理=弹性限度内伸长与拉力成正比(F=kx·刻度均匀)；使用=调零/不超量程/顺向拉；弹力=弹性形变产生的力(支持/压力/拉力)；橡皮泥=塑性。"),
    ("kp_card_soap",
     "肥皂去油污的原理：乳化",
     "基础科学知识点内容（人话接口）", "化学",
     "油污不溶于水，用水洗不掉；肥皂/洗洁精能去油污靠的是**乳化作用**：肥皂分子"
     "一头亲水、一头亲油（双亲分子）——亲油端扎进油污、亲水端朝向水，把大油滴"
     "拆散成无数小油滴稳定悬浮在水中被冲走（乳化，物理分散过程不是溶解）。洗衣"
     "粉/洗洁精/沐浴露同理（表面活性剂）。对比：汽油去油污是**溶解**（油溶于油）；"
     "热水去油污更快（温度高乳化/溶解都更快，且油脂软化）。肥皂的历史：油脂+碱"
     "（皂化反应）制得，中国古代用皂角/猪胰（「胰子」的由来）。合成洗涤剂在硬水"
     "中不产生浮渣（肥皂遇硬水生成钙镁皂垢），这是洗衣粉胜出的原因。",
     ["肥皂去油污的原理", "乳化和溶解有什么区别", "洗洁精去油的原理",
      "为什么汽油也能去油污", "肥皂是怎么发明的", "洗衣粉和肥皂哪个更适合硬水"],
     ["问表面活性剂家族", "问皂化反应方程"],
     "atomic", "",
     "肥皂去油污=乳化(双亲分子拆散油滴悬浮冲走·非溶解)；汽油=溶解；热水更快；硬水中肥皂生钙镁垢→洗衣粉胜；肥皂=油脂+碱皂化，古用皂角/胰子。"),
    ("kp_card_graft",
     "嫁接：无性繁殖的智慧",
     "基础科学知识点内容（人话接口）", "生物学",
     "嫁接是把一株植物的枝或芽（接穗）接到另一株植物（砧木）上，使它们愈合长成"
     "完整植株的技术——属于**无性生殖**（不经过两性生殖细胞结合，后代保持接穗"
     "的优良性状）。关键要领：接穗与砧木的**形成层**必须紧贴对齐（形成层细胞分"
     "裂愈合是成活关键）。应用：苹果/柑橘/月季等几乎全部果树与名贵花卉都用嫁接"
     "——一株上可接多个品种（「一树多果」）；砧木提供抗病/耐旱/矮化的根。无性生"
     "殖家族：扦插（月季/葡萄枝条插土生根）、压条（桂花）、组织培养（植物细胞全"
     "能性，工厂化育苗）。对比有性生殖（种子繁殖）：有性产生变异利于进化，无性"
     "保持品种纯度利于生产——各有所长。",
     ["嫁接属于什么繁殖方式", "嫁接成活的关键是什么", "接穗和砧木分别是什么",
      "果树为什么都要嫁接", "扦插和嫁接的区别", "一树多果是怎么做到的"],
     ["问植物组织培养流程", "问有性无性生殖对比"],
     "atomic", "",
     "嫁接=无性生殖：接穗(枝芽)接砧木·形成层对齐是成活关键→保持接穗优状；果树花卉全靠它(一树多果)；家族=扦插/压条/组织培养；无性保纯·有性产变。"),
    ("kp_card_province34",
     "中国的行政区划",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国的省级行政区共 **34 个**：23 个省、5 个自治区（内蒙古/新疆/西藏/宁夏/"
     "广西）、4 个直辖市（北京/天津/上海/重庆）、2 个特别行政区（香港/澳门）。"
     "记忆口诀「两湖两广两河山，五江云贵福吉安……」。特别行政区实行「一国两"
     "制」（港人治港、高度自治，分别于 1997/1999 回归）。省级行政中心之最：面"
     "积最大=新疆（约166万km²）、最小=澳门（约33km²）、人口最多=广东；「北纬"
     "30°穿过」的省会湖（杭州西湖/武汉东湖）。三级行政区划基本框架：省级—县级—"
     "乡级。简称考点：鲁（山东）/晋（山西）/豫（河南）/粤（广东）/蜀或川（四"
     "川）等。",
     ["中国有多少个省级行政区", "五个自治区是哪几个", "四个直辖市是什么",
      "什么是特别行政区", "山东的简称是什么", "面积最大的省级行政区"],
     ["问省份简称大全", "问一国两制内容"],
     "atomic", "",
     "省级行政区 34 个=23 省+5 自治区(内蒙古新疆西藏宁夏广西)+4 直辖市(京津沪渝)+2 特区(港澳·一国两制)；最大新疆/最小澳门；简称：鲁晋豫粤川。"),
]

QUESTIONS = [
    ("QB-349", "弹簧测力计的原理", "物理学", "技术直答",
     ["弹性形变", "成正比"], "通识拓展54"),
    ("QB-350", "肥皂去油污的原理", "化学", "技术直答",
     ["乳化"], "通识拓展54"),
    ("QB-351", "嫁接属于什么繁殖方式", "生物学", "技术直答",
     ["无性生殖", "无性繁殖"], "通识拓展54"),
    ("QB-352", "中国有多少个省级行政区", "地理学", "技术直答",
     ["34"], "通识拓展54"),
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
                               "level:L2", "status:verified", "batch:通识拓展54"],
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
    bank["version"] = "v1.46"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
