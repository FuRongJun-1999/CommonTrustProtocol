# -*- coding: utf-8 -*-
"""seed_common_46_cards.py · 通识拓展批次46知识卡+题库（幂等）

46：物理学-指南针与地磁场/化学-酒精（乙醇）/生物学-反刍动物/历史-商鞅变法
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_compass",
     "指南针与地磁场",
     "基础科学知识点内容（人话接口）", "物理学",
     "指南针能指示南北，是因为地球本身是个巨大的磁体——周围存在地磁场：悬浮的"
     "磁针受地磁作用，静止时一端指南（S 极）、一端指北（N 极）。重要细节：地磁"
     "的 N 极在地理南极附近、S 极在地理北极附近（异性相吸所以磁针北端指北）；地"
     "磁南北极与地理南北极并不重合（有磁偏角）——宋代沈括《梦溪笔谈》最早记载"
     "磁偏角，比欧洲早 400 年。指南针是中国四大发明之一：战国「司南」（天然磁石"
     "琢成勺形）→北宋人工磁化的罗盘用于航海→经阿拉伯人传入欧洲，助推大航海时"
     "代。鸽子和候鸟也能感应地磁导航。",
     ["指南针为什么能指示南北", "什么是地磁场", "磁偏角是谁发现的",
      "司南是什么", "指南针是哪个国家发明的", "地磁和地理的南北极重合吗"],
     ["问磁悬浮原理", "问磁极倒转假说"],
     "atomic", "",
     "指南针=磁针受地磁场作用定南北；地磁 N 极在地理南极附近·不重合→磁偏角(沈括《梦溪笔谈》最早记载)；四大发明：司南→罗盘航海。"),
    ("kp_card_ethanol",
     "酒精（乙醇）与消毒",
     "基础科学知识点内容（人话接口）", "化学",
     "酒精的化学名是乙醇（C₂H₅OH）——无色透明、有特殊香味、易挥发易燃的液体，"
     "与水以任意比例互溶。医用消毒酒精的浓度是 75%（体积分数），不是越高越好："
     "浓度过高（95%）会使细菌表面蛋白质迅速凝固形成保护壳，反而杀不死内部；75% "
     "能渗透进菌体内使蛋白质变性——恰到好处。乙醇是酒的主要成分（白酒约 38-60 "
     "度=体积百分数），饮酒伤肝（酒精在肝内代谢）。工业酒精含甲醇（有毒，饮用会"
     "失明甚至致死），绝不可勾兑饮用。化学用途：优良溶剂与燃料（乙醇汽油）。",
     ["酒精的成分是什么", "消毒酒精为什么是75度", "95%的酒精为什么消毒效果反而差",
      "工业酒精为什么不能喝", "白酒的度数是什么意思", "乙醇汽油是什么"],
     ["问甲醇毒性机理", "问酿酒发酵化学"],
     "atomic", "",
     "酒精=乙醇C₂H₅OH(易挥发易燃·与水互溶)；消毒 75% 恰好——95% 使表面蛋白凝固杀不死内部；工业酒精含甲醇毒不可饮；酒度数=体积百分数。"),
    ("kp_card_ruminate",
     "反刍动物：牛为什么不停嚼",
     "基础科学知识点内容（人话接口）", "生物学",
     "牛吃完草后还会把食物返回嘴里反复咀嚼——这叫反刍。牛是反刍动物，胃分四"
     "室：瘤网瓣皱（瘤胃最大，是发酵「仓库」，亿万微生物帮它分解草里的纤维"
     "素）——草在瘤胃浸泡软化后成团返回口腔细嚼，再咽下经网胃→瓣胃→皱胃（真"
     "胃，真正分泌胃液消化）。有此本领的还有羊/鹿/骆驼——草料纤维素难消化，反"
     "刍+微生物发酵才能榨取营养，且进食快、藏在安全处慢慢消化（躲避天敌的生存"
     "策略）。人不反刍，只有一个胃；马/兔子是单胃但靠盲肠微生物消化纤维。",
     ["牛吃完草为什么还在嚼", "什么是反刍", "牛有几个胃",
      "牛为什么能消化草", "骆驼是反刍动物吗", "人为什么不反刍"],
     ["问瘤胃微生物研究", "问单胃草食动物对比"],
     "atomic", "",
     "反刍=食物返回口腔再嚼；牛四胃：瘤胃(微生物发酵纤维素·最大)→网→瓣→皱(真胃)；羊鹿骆驼同款；进化意义=快进食+安全处慢消化。"),
    ("kp_card_shangyang",
     "商鞅变法",
     "人文通识知识点内容（人话接口）", "历史",
     "商鞅变法：战国时期秦孝公任用商鞅（公元前 356 年起）两次变法，使秦国从西陲"
     "弱邦一跃成为最强国家。核心内容：①废井田开阡陌——承认土地私有；②奖励耕"
     "战——生产粮食布帛多可免徭役、按军功授爵（斩敌首级计功，贵族无军功不得享"
     "特权）；③建立县制——由国君直接派官治理（加强中央集权）；④严明法度、连"
     "坐法。立木为信：商鞅城门徙木赏五十金取信于民，变法得以推行。结局：孝公死"
     "后商鞅被旧贵族车裂，但新法未被废除——「商鞅虽死，秦法未败」，为 100 多年"
     "后秦始皇统一六国奠基。",
     ["商鞅变法发生在哪个国家", "商鞅变法的内容", "立木为信的典故",
      "商鞅是怎么死的", "军功爵制是什么", "商鞅变法对秦统一的意义"],
     ["问战国七雄格局", "问法家思想体系"],
     "atomic", "",
     "商鞅变法=战国秦孝公 356BC 起：废井田/奖耕战(军功爵)/行县制/严法度；立木为信取信于民；商鞅车裂而秦法不败→秦统一奠基。"),
]

QUESTIONS = [
    ("QB-317", "指南针为什么能指示南北", "物理学", "技术直答",
     ["地磁场"], "通识拓展46"),
    ("QB-318", "消毒酒精为什么是75度", "化学", "技术直答",
     ["蛋白质", "凝固", "渗透"], "通识拓展46"),
    ("QB-319", "牛吃完草为什么还在嚼", "生物学", "技术直答",
     ["反刍"], "通识拓展46"),
    ("QB-320", "商鞅变法发生在哪个国家", "历史", "技术直答",
     ["秦国"], "通识拓展46"),
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
                               "level:L2", "status:verified", "batch:通识拓展46"],
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
    bank["version"] = "v1.38"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
