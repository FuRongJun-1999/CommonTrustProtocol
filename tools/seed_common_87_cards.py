# -*- coding: utf-8 -*-
"""seed_common_87_cards.py · 通识拓展批次87知识卡+题库（幂等）

87：物理学-声音的产生与传播/化学-氧化物/生物学-生物的变异/地理学-中国的民族
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_soundgen",
     "声音的产生与传播",
     "基础科学知识点内容（人话接口）", "物理学",
     "声音的产生：**物体的振动**——振动停止，发声也停止（但已发出的声音继续传"
     "播，「余音绕梁」是回声与混响）。声源：振动的弦/膜/空气柱/骨骼。声音的传播"
     "需要**介质**（固体/液体/气体都能传声，真空不能——「月球上听不到爆炸声」）；"
     "一般固体传声最快（钢铁约 5200m/s）、液体次之（水约 1500m/s）、气体最慢（空"
     "气 15℃ 约 340m/s）。人耳听声过程：声波→鼓膜振动→听小骨→耳蜗（感受器）→"
     "听神经→大脑。骨传导：声音经头骨/颌骨传到听觉神经（贝多芬咬棒抵钢琴听"
     "音）——骨传导耳机原理。人耳听觉范围 20Hz~20000Hz，低于 20Hz 为次声、高于 "
     "20000Hz 为超声。声音三项特性：音调（频率，女高音）、响度（振幅，音量）、音"
     "色（波形，「闻其声知其人」）。",
     ["声音是怎么产生的", "声音的传播需要什么", "真空能传声吗",
      "骨传导耳机原理", "人耳能听到的频率范围", "音调响度音色的区别"],
     ["问回声测距计算", "问耳朵结构"],
     "atomic", "",
     "声音=物体振动(停振即停声)·需介质传播(固>液>气·真空不传·15℃ 空气 340m/s)；人耳 20Hz-20kHz；骨传导=经头骨传听神经；三特性=音调(频)/响度(幅)/音色(波)。"),
    ("kp_card_oxide",
     "氧化物：由两种元素组成的含氧化合物",
     "基础科学知识点内容（人话接口）", "化学",
     "氧化物的定义：由**两种元素**组成、其中一种是**氧元素**的化合物——如 H₂O"
     "（水）、CO₂（二氧化碳）、Fe₂O₃（氧化铁）、CaO（生石灰）。易错辨析：①"
     " KClO₃（氯酸钾）含氧但由三种元素组成——不是氧化物（是含氧化合物/盐）；②"
     " O₂ 是单质不是化合物——不是氧化物；③含氧酸（H₂SO₄）、碱（NaOH）、盐"
     "（CuSO₄）都含氧但元素多于两种——都不是氧化物。氧化物分类：金属氧化物"
     "（Fe₂O₃/CaO——多为碱性氧化物）与非金属氧化物（CO₂/SO₂——多为酸性氧化"
     "物）；不成盐氧化物（CO/NO）。判断口诀：「两元素、有其一为氧，才叫氧」。",
     ["什么是氧化物", "氯酸钾是氧化物吗", "水是氧化物吗", "氧化物的分类",
      "CO 是氧化物吗", "金属氧化物和非金属氧化物"],
     ["问酸性碱性氧化物", "问氧化物与含氧酸转化"],
     "atomic", "",
     "氧化物=两元素+其一为氧：H₂O/CO₂/Fe₂O₃/CaO；KClO₃(三元素)/O₂(单质)/H₂SO₄ NaOH CuSO₄(多元素)都不是；金属氧化物多为碱性·非金属多为酸性·CO/NO 不成盐。"),
    ("kp_card_variation",
     "生物的变异",
     "基础科学知识点内容（人话接口）", "生物学",
     "变异：亲代与子代、子代个体之间的差异现象。分类：①**可遗传的变异**——遗"
     "传物质改变：基因重组（有性生殖杂交）、基因突变（宇宙射线/化学诱变/复制错"
     "误）、染色体变异——能传给后代（育种的基础）；②**不可遗传的变异**——仅环"
     "境影响，遗传物质未变：晒黑的皮肤、营养不良的矮小、修剪的树冠（对象是同一"
     "基因型）。应用：育种（杂交/诱变/太空种子）与警惕（致畸致突变因素：射线/"
     "尼古丁/甲醛影响胎儿）。意义：变异为进化提供原材料（有利变异被自然选择保"
     "留——与遗传共同推动物种演化）；没有变异，生物无法适应变化的环境。判断口"
     "诀：看遗传物质变没变——变了的才可遗传。",
     ["可遗传的变异和不遗传的变异", "变异的类型", "晒黑是可遗传变异吗",
      "太空育种利用什么变异", "变异对生物进化的意义", "基因突变是什么"],
     ["问变异来源三大类", "问人类基因组多样性"],
     "atomic", "",
     "变异两类：可遗传=遗传物质变(基因重组/突变/染色体变异·育种基础)vs 不可遗传=纯环境影响(晒黑/营养不良)；变异=进化原材料(有利变异被选择)；判断看 DNA 变否。"),
    ("kp_card_ethnic",
     "中国的民族",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国是统一的多民族国家：56 个民族——汉族人口最多（约 91%），其余 55 个为"
     "少数民族。人口最多的少数民族是**壮族**（约 1900 万，主要在广西壮族自治区）；"
     "其他人口较多的：维吾尔族（新疆）、回族（宁夏及全国分布——大分散小聚居）、"
     "苗族、满族、藏族、蒙古族等。分布特点：**大杂居、小聚居、交错居住**（汉族遍"
     "布全国，少数民族主要分布在西南/西北/东北边疆）。民族政策：民族区域自治制"
     "度（5 个自治区）、各民族一律平等、尊重风俗习惯与宗教信仰。民族文化丰富："
     "傣族泼水节、蒙古族那达慕、藏族雪顿节、回族开斋节；民族语言 130 余种。少数"
     "民族最多的省份是云南（25 个，被称为「民族博物馆」）。",
     ["中国人口最多的少数民族", "中国有多少个民族", "民族分布的特点",
      "什么是民族区域自治", "泼水节是哪个民族的节日", "哪个省少数民族最多"],
     ["问民族服饰文化", "问自治区制度细节"],
     "atomic", "",
     "中国 56 民族：汉族 91%·最多少数民族=壮族(广西)；分布=大杂居小聚居交错；政策=区域自治(5 自治区)+一律平等；云南少数民族最多(25 个)；节=泼水/那达慕/雪顿。"),
]

QUESTIONS = [
    ("QB-481", "声音是怎么产生的", "物理学", "技术直答",
     ["振动"], "通识拓展87"),
    ("QB-482", "什么是氧化物", "化学", "技术直答",
     ["两种元素", "氧元素"], "通识拓展87"),
    ("QB-483", "可遗传的变异和不遗传的变异", "生物学", "技术直答",
     ["遗传物质", "环境"], "通识拓展87"),
    ("QB-484", "中国人口最多的少数民族", "地理学", "技术直答",
     ["壮族"], "通识拓展87"),
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
                               "level:L2", "status:verified", "batch:通识拓展87"],
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
    bank["version"] = "v1.79"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
