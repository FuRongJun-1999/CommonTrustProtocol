# -*- coding: utf-8 -*-
"""seed_common_148_cards.py · 通识拓展批次148知识卡+题库（幂等）

148：历史学三连——王安石变法/土木堡之变与北京保卫战/京杭大运河
KCCS 四要素+题干原句触发词。三重预检：王安石老卡=文学角度（变法政治角度未
覆盖）、大运河在 snwd/keju 卡中仅借道或一句提及、土木堡双库零覆盖。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_wanganxin",
     "王安石变法",
     "人文通识知识点内容（人话接口）", "历史学",
     "王安石变法（熙宁变法）：**1069 年**宋神宗任用**王安石**推行，背景=北宋「"
     "积贫积弱」（冗官冗兵冗费+对辽西夏岁币）。主要内容：①**青苗法**——官府低"
     "息贷粮给农民（青黄不接时），抑制高利贷盘剥；②**募役法**——出钱代役（免"
     "役钱），官僚地主也要交（触动利益）；③**农田水利法**——兴修水利垦荒；"
     "④**方田均税法**——清丈土地按亩收税防隐瞒；⑤**保甲法/保马法**——农"
     "民编组练兵，寓兵于农强兵。争议与结局：**司马光**等保守派反对（「祖宗之法"
     "不可变」），新法用人不当执行走样扰民，神宗死后（1085）新法基本废罢，演"
     "变为新旧**党争**。王安石名言「**天变不足畏，祖宗不足法，人言不足恤**」"
     "（三不足）体现改革家气魄。文学身份：唐宋八大家之一（《游褒禅山记》）。",
     ["王安石变法是哪一年", "青苗法是什么", "王安石变法的内容",
      "司马光为什么反对", "熙宁变法", "天变不足畏是谁说的"],
     ["问王安石文学作品（用宋代诗文卡）", "问商鞅变法（战国）"],
     "atomic", "",
     "王安石变法=1069 宋神宗支持，针对积贫积弱：青苗法低息贷粮/募役法/农田水利/方田均税/保甲法；司马光反对党争，1085 后废罢；「三不足」名言；王安石亦为唐宋八大家。"),
    ("kp_card_tumubao",
     "土木堡之变与北京保卫战",
     "人文通识知识点内容（人话接口）", "历史学",
     "**1449 年**，蒙古瓦剌部南下侵扰，明英宗在宦官**王振**怂恿下草率亲征——"
     "50 万大军在**土木堡**（河北怀来）被围歼，**英宗被俘**（「土木之变」，明"
     "朝由盛转衰的转折）。消息传来京师震恐，徐珵等主张南迁；兵部侍郎**于谦**"
     "力排众议：「言南迁者可斩！」——拥立英宗之弟**景泰帝**（朱祁钰）即位稳"
     "定人心，集结各地勤王军。**北京保卫战**：于谦列阵九门之外背城而战，击退"
     "瓦剌（也先）进攻，保全北京城。后续：一年后瓦剌放回英宗；**1457 年「夺门"
     "之变」**英宗复辟，于谦以「谋逆」罪名被冤杀——「粉骨碎身浑不怕，**要留"
     "清白在人间**」（《石灰吟》）成为其人格写照；明宪宗时平反昭雪，与岳飞并"
     "祀西湖。",
     ["土木堡之变是哪一年", "明英宗被谁俘虏", "于谦和北京保卫战",
      "夺门之变", "要留清白在人间是谁写的", "景泰帝"],
     ["问岳飞（南宋抗金）", "问明朝海禁与郑和"],
     "atomic", "",
     "土木堡之变=1449 英宗听王振亲征瓦剌全军覆没被俘；于谦力排南迁议立景泰帝，北京保卫战背城列阵击退也先；1457 夺门之变英宗复辟冤杀于谦——《石灰吟》「要留清白在人间」人格写照；明朝由盛转衰转折。"),
    ("kp_card_grandcanal",
     "京杭大运河",
     "人文通识知识点内容（人话接口）", "历史学",
     "京杭大运河=世界上**里程最长、工程最大**的古代运河：①**开凿**——春秋吴"
     "国开邗沟肇始；**隋炀帝**（605 年起）大规模贯通：永济渠+通济渠+邗沟+江南"
     "河（以**洛阳**为中心，北达涿郡南至余杭）；元代「裁弯取直」改线直达大都"
     "（北京），形成今**北京—杭州**格局；②**贯通五大水系**——海河、黄河、淮"
     "河、长江、钱塘江；全长约 **1794 公里**；③**作用**——漕运（南粮北运的帝"
     "国命脉，「半天下之财赋悉由此路而进」）、沿线催生扬州/淮安/临清/苏州等繁"
     "华城市；④**现状与保护**——南水北调东线借道；部分河段仍通航；**2014 年"
     "列入世界文化遗产**。与长城并称中国古代两大伟大工程（一横一纵）。",
     ["京杭大运河是谁开凿的", "隋炀帝开凿大运河", "大运河连接哪五大水系",
      "大运河有多长", "漕运是什么", "大运河世界遗产"],
     ["问都江堰（用都江堰卡）", "问南水北调工程细节"],
     "atomic", "",
     "京杭大运河=隋炀帝 605 年贯通(永济渠通济渠邗沟江南河·以洛阳为中心)，元代裁弯取直成今北京—杭州格局；连海河黄河淮河长江钱塘江五大水系，全长约 1794km 世界最长古运河；漕运命脉催生扬州苏州繁华；2014 世遗，南水北调东线借道。"),
]

QUESTIONS = [
    ("QB-705", "王安石变法开始于哪一年？「青苗法」的主要内容是什么？", "历史学", "技术直答",
     ["1069", "宋神宗", "低息", "贷款", "青黄不接"], "通识拓展148"),
    ("QB-706", "土木堡之变发生在哪一年？哪位名臣领导了北京保卫战？", "历史学", "技术直答",
     ["1449", "于谦", "景泰", "北京保卫战"], "通识拓展148"),
    ("QB-707", "京杭大运河贯通了哪五大水系？它是什么时期大规模开凿贯通的？", "历史学", "技术直答",
     ["海河", "黄河", "淮河", "长江", "钱塘江", "隋炀帝", "隋朝"], "通识拓展148"),
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
                               "level:L2", "status:verified", "batch:通识拓展148"],
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
    bank["version"] = "v4.21"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
