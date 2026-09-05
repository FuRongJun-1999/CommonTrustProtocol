# -*- coding: utf-8 -*-
"""seed_common_173_cards.py · 通识拓展批次173知识卡+题库（幂等）

173：辟谣与生物三连——银器试毒辟谣/指甲月牙辟谣/蜜蜂蜇人
KCCS 四要素+题干原句触发词。三重预检：三主题双库零覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_cardsilvertest",
     "银器试毒靠不靠谱",
     "基础科学知识点内容（人话接口）", "化学",
     "「银针试毒」半真半假：①**古代为什么有效**——古代砒霜（三氧化二砷）提"
     "纯技术差，混有**硫或硫化物杂质**；银与硫反应生成**黑色硫化银**——银针"
     "变黑，其实验出的是「**硫**」这个杂质，不是砒霜本身；②**为什么现在失"
     "效**——现代砒霜提纯度高（无硫），银针不变色；而且**根本不含硫的毒物**"
     "（氰化物/毒鼠强/农药）银器毫无反应——银器试不出绝大多数毒；③**反向误"
     "会**——银器碰到**鸡蛋黄/温泉水**也会变黑（蛋黄含硫、温泉含硫），难道"
     "鸡蛋有毒？④正确的「试毒」=现代检测手段（化学分析/仪器检测）。银器真正"
     "的价值：质软易加工+抑菌性（微量银离子有抗菌作用——银离子过滤器是真的）"
     "——但「银饰养生排毒」是营销话术。",
     ["银器试毒是真的吗", "银针为什么变黑", "银器遇到鸡蛋为什么变黑",
      "硫化银", "银器试毒的原理", "银离子抗菌"],
     ["问古代法医验毒史", "问重金属中毒检测"],
     "atomic", "",
     "银针试毒=古代砒霜含硫杂质遇银生成黑色硫化银（验出的是硫非毒）；现代高纯砒霜/无硫毒物（氰化物农药）银器无反应；碰蛋黄温泉也变黑——变黑只说明有硫；银离子确有抗菌但「排毒」是营销。"),
    ("kp_card_lunula",
     "指甲上的月牙是健康晴雨表吗",
     "基础科学知识点内容（人话接口）", "生物学",
     "指甲根部淡白色的「月牙」（半月痕）真相：①**它是什么**——指甲从根部**甲"
     "母质（甲基质）**不断长出，新生的细胞还没完全角化（未变透明），是白色的；"
     "被后方的皮肤遮住一部分，露出来的弧形就是月牙——本质=**刚长出来还没「磨"
     "砂变透明」的新指甲**；②**为什么有人有有人没有**——月牙大小数量主要由"
     "**甲基质位置**决定（甲基质靠后的人月牙天生被挡住看不见），与「气血不足"
     "」「肾虚」无关；大拇指勤用磨损快、指甲长得快，月牙最明显；③**什么时候"
     "需要留意**——月牙**短期内突然明显变化**（突然全部消失或突然变大变多），"
     "可能提示甲状腺问题/营养剧变/重大应激——是「变化」需要留意，不是「没有"
     "」；④指甲与健康：指甲整体的颜色凹陷（匙状甲=缺铁）、增厚变色（真菌/灰"
     "指甲）才是更有意义的信号。",
     ["指甲月牙是什么", "月牙少是身体不好吗", "月牙与健康的关系",
      "甲基质", "指甲上月牙突然消失"],
     ["问灰指甲治疗", "问指甲读懂健康信号"],
     "atomic", "",
     "月牙=甲母质新生未角化的白色指甲被皮肤遮露出的弧：大小数量天生（甲基质位置）与气血肾虚无关；突然明显变化才留意（甲状腺/营养剧变）；匙状甲缺铁/增厚变色灰指甲更有意义——别用月牙算健康。"),
    ("kp_card_beekeeper",
     "蜜蜂蜇人后为什么会死",
     "基础科学知识点内容（人话接口）", "生物学",
     "**蜜蜂**（工蜂）蜇人后常会死：它的蜇针（产卵器特化）**带倒钩**，刺入哺"
     "乳动物有弹性的皮肤后**拔不出来**——挣扎飞走时整只蜇针连**毒囊、部分内"
     "脏**被拉出体腔，蜜蜂因内脏损伤很快死亡——所以工蜂的蜇击是「同归于尽」"
     "的最后防御。**马蜂/黄蜂的蜇针光滑**，可以拔出反复蜇（更危险）。**被蜜蜂"
     "蜇了怎么办**：①**刮除蜇针**——用指甲/银行卡边缘横向刮掉（**别用镊子夹"
     "捏**——挤压毒囊注入更多毒液）；②肥皂水清洗（蜜蜂毒液偏酸性）；③冷敷"
     "消肿止痛；④**危险信号**：全身荨麻疹、呼吸困难、喉头水肿、头晕血压下降"
     "=**过敏性休克**，立即拨打 120（蜂毒过敏可数分钟内致命，过敏体质者可咨"
     "询医生随身携带肾上腺素笔）；马蜂蜂毒偏碱性且可反复攻击，就医标准更宽。",
     ["蜜蜂蜇人后为什么会死", "被蜜蜂蜇了怎么处理", "蜜蜂和马蜂的区别",
      "蜇针拔出来还是刮掉", "蜂毒过敏休克"],
     ["问被蛇咬急救（就医）", "问昆虫防叮咬"],
     "atomic", "",
     "蜜蜂蜇针带倒钩拔不出——飞走时连毒囊内脏拉出而死=一次性防御；马蜂蜇针光滑可反复蜇；被蜇=银行卡边缘刮除蜇针（勿镊夹挤毒囊）+肥皂水洗+冷敷；全身荨麻疹呼吸困难=过敏性休克立即 120。"),
]

QUESTIONS = [
    ("QB-770", "古代「银针试毒」为什么能让银针变黑？它真的能验出所有的毒吗？", "化学", "技术直答",
     ["硫", "硫化银", "砒霜", "杂质", "现代", "失灵"], "通识拓展173"),
    ("QB-771", "指甲上的月牙是什么？月牙少真的代表身体不健康吗？", "生物学", "技术直答",
     ["甲基质", "新生指甲", "天生", "角化", "无关"], "通识拓展173"),
    ("QB-772", "蜜蜂蜇人后为什么会死？被蜜蜂蜇伤后正确处理蜇针的方法是什么？", "生物学", "技术直答",
     ["倒钩", "毒囊", "内脏", "刮除", "挤压", "过敏性休克"], "通识拓展173"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{6,}", content):
            problems.append((node[0], f"长英文词: {word}"))
    if problems:
        raise SystemExit(f"外文长词检测报警: {problems}")


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
                               "level:L2", "status:verified", "batch:通识拓展173"],
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
    bank["version"] = "v4.46"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
