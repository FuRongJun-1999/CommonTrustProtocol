# -*- coding: utf-8 -*-
"""seed_common_20_cards.py · 通识拓展批次20知识卡+题库（幂等）

20：化学-化石燃料/地理学-天气与气候/生物学-疫苗原理/艺术-京剧四大行当
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_fossilfuel",
     "化石燃料与可再生能源",
     "基础科学知识点内容（人话接口）", "化学",
     "三大化石燃料：煤、石油、天然气——由古代生物遗骸经亿万年地质作用（高温高"
     "压）演变而成，属于不可再生能源，用一点少一点。化石燃料燃烧会释放二氧化碳"
     "（温室气体，加剧全球变暖）和二氧化硫等污染物（酸雨成因之一）。与之相对的"
     "可再生能源：太阳能、风能、水能、地热能、生物质能等——「碳中和」目标就是"
     "推动能源结构从化石燃料向清洁能源转型。",
     ["煤石油天然气属于什么能源", "什么是化石燃料", "为什么化石燃料不可再生",
      "可再生能源有哪些", "酸雨是怎么形成的", "什么是碳中和"],
     ["问核能利弊", "问具体化工工艺"],
     "atomic", "",
     "化石燃料=煤/石油/天然气(古生物遗骸·不可再生)；燃烧排CO₂致变暖、SO₂致酸雨；替代=太阳能风能水能；碳中和=能源转型。"),
    ("kp_card_weatherclimate",
     "天气与气候的区别",
     "基础科学知识点内容（人话接口）", "地理学",
     "天气：一个地方短时间内的大气状况（阴晴/冷热/风雨），特点是多变——「今天"
     "下雨」「明天气温下降」说的都是天气。气候：一个地区多年（通常30年以上）大"
     "气状况的平均与统计特征，特点是稳定——「昆明四季如春」「江南梅雨」说的是"
     "气候。区别口诀：天气看今天，气候看常年；描述天气用「阴晴雨雪气温风」，描"
     "述气候用「气候类型」（热带雨林气候/温带季风气候/地中海气候等）。",
     ["天气和气候有什么区别", "什么是气候类型", "昆明四季如春说的是天气还是气候",
      "天气预报报的是气候吗", "什么是温带季风气候", "气候为什么稳定天气为什么多变"],
     ["问气象雷达原理", "问气候变化争议细节"],
     "atomic", "",
     "天气=短时多变(今天下雨)；气候=多年平均稳定(四季如春)；气候类型=热带雨林/温带季风/地中海等。"),
    ("kp_card_vaccine",
     "疫苗预防传染病的原理",
     "基础科学知识点内容（人话接口）", "生物学",
     "疫苗的本质是「给免疫系统做演习」：把病原体或其特征片段（灭活的死病毒/减"
     "毒活疫苗/蛋白组分/mRNA 指令）接种进人体，刺激免疫系统产生针对性抗体和记"
     "忆细胞，但不会真的生病；等真正的病原体入侵时，记忆细胞快速启动，抗体大量"
     "增殖把病原体清除——这叫主动免疫。疫苗防病而不主要治病；历史上最早的疫苗"
     "是詹纳 1796 年的牛痘（预防天花），天花也因全民接种成为首个被人类消灭的传"
     "染病。",
     ["疫苗是怎么预防传染病的", "疫苗的原理是什么", "灭活疫苗和减毒疫苗的区别",
      "什么是记忆细胞", "最早的疫苗是谁发明的", "疫苗为什么能防病"],
     ["问过敏与自免机制", "问具体疫苗研发工艺"],
     "atomic", "",
     "疫苗=给免疫系统做演习：接种抗原→抗体+记忆细胞→真病原入侵时快速清除；主动免疫；牛痘(詹纳1796)开山。"),
    ("kp_card_beijingopera",
     "京剧四大行当与脸谱",
     "人文通识知识点内容（人话接口）", "艺术",
     "京剧是中国的「国粹」，角色分四大行当：生（男性正面角色，分老生/小生/武"
     "生）、旦（女性角色，分青衣/花旦/老旦/刀马旦）、净（又称花脸，性格鲜明"
     "的男性角色，脸上画脸谱）、丑（丑角，鼻梁抹白粉，幽默机敏）。脸谱颜色有"
     "含义：红色表忠义（关羽）、黑色表刚直（包公、张飞）、白色表奸诈（曹操）、"
     "蓝绿表勇猛草莽。京剧 2010 年入选联合国人类非物质文化遗产代表作名录。",
     ["京剧中的四大行当是什么", "生旦净丑分别指什么", "京剧脸谱颜色有什么含义",
      "关羽的脸谱是什么颜色", "什么是花脸", "京剧是什么时候入选非遗的"],
     ["问昆曲越剧等其他剧种", "问唱念做打基本功细节"],
     "atomic", "",
     "京剧四大行当=生(男)/旦(女)/净(花脸)/丑(白鼻梁)；脸谱：红忠(关羽)/黑刚直(包公)/白奸(曹操)；国粹·非遗。"),
]

QUESTIONS = [
    ("QB-213", "煤、石油、天然气属于什么能源", "化学", "技术直答",
     ["化石燃料", "不可再生"], "通识拓展20"),
    ("QB-214", "天气和气候有什么区别", "地理学", "技术直答",
     ["短时", "多年平均"], "通识拓展20"),
    ("QB-215", "疫苗是怎么预防传染病的", "生物学", "技术直答",
     ["抗体", "记忆细胞"], "通识拓展20"),
    ("QB-216", "京剧中的四大行当是什么", "艺术", "技术直答",
     ["生旦净丑"], "通识拓展20"),
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
                               "level:L2", "status:verified", "batch:通识拓展20"],
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
    bank["version"] = "v1.12"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
