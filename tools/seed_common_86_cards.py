# -*- coding: utf-8 -*-
"""seed_common_86_cards.py · 通识拓展批次86知识卡+题库（幂等）

86：物理学-并联电路电流规律/化学-燃烧条件实验/生物学-现代生物技术/地理学-西北地区
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_parcur",
     "并联电路的电流规律",
     "基础科学知识点内容（人话接口）", "物理学",
     "并联电路电流规律：**干路电流等于各支路电流之和**（I=I₁+I₂+…）——像水管分"
     "叉，总流量=各支管流量之和；各支路互不影响（一条支路断开，其他支路照常工"
     "作）。电压规律：并联各支路两端电压**相等**（=电源电压）。电阻规律：并联总电"
     "阻比任何一个支路电阻都**小**（相当于加粗了导体——越并越「粗」越导电）。家"
     "庭应用：各用电器并联（电压都是 220V、互不干扰）；但总电流=各电器电流之和，"
     "同时开太多电器→干路电流过大→跳闸（保险丝/空气开关的作用）。串联对照：电"
     "流处处相等 I=I₁=I₂，总电压=各部分电压之和，总电阻=各电阻之和（越串越"
     "「大」）。",
     ["并联电路的电流规律", "串联和并联电路电压规律", "并联总电阻怎么变",
      "家里电器为什么不能同时开太多", "干路和支路电流的关系", "串联电路电流规律"],
     ["问欧姆定律综合计算", "问家庭电路故障分析"],
     "atomic", "",
     "并联：I 干=ΣI 支·各支路电压相等·总电阻反而更小(越并越粗)；互不影响；同时开多电器→干路电流过大→跳闸；串联对照：I 处处相等·U=ΣU·R=ΣR。"),
    ("kp_card_burnexp",
     "燃烧条件的探究实验",
     "基础科学知识点内容（人话接口）", "化学",
     "教科书经典实验「烧杯热水上的白磷与红磷」：装置——烧杯盛 80℃ 热水，水中"
     "放一块白磷，铜片上左边放白磷、右边放红磷。现象与结论：①铜片上的白磷燃烧"
     "（温度达着火点 40℃+接触空气）→燃烧需要**温度达到着火点**；②红磷不燃（着"
     "火点 240℃，80℃ 不够）→同上；③水中白磷不燃（温度够但**无氧气**）——通入"
     "氧气后水中白磷竟在「水下燃烧」（气泡包裹火焰）→燃烧需要**氧气**。总结：燃"
     "烧三条件=可燃物+氧气（或空气）+温度达到着火点，三者缺一不可。控制变量法"
     "的经典应用：每次只改变一个条件对比。拓展：白磷着火点仅 40℃（毒且易自燃"
     "——必须水下保存），红磷 240℃（安全，火柴盒侧面用的是红磷）。",
     ["怎么证明燃烧需要氧气", "白磷红磷对照实验", "水下燃烧是怎么回事",
      "白磷的着火点是多少", "白磷为什么保存在水中", "燃烧的三个条件实验"],
     ["问爆炸极限概念", "问灭火原理复习"],
     "atomic", "",
     "白磷红磷实验(80℃ 热水)：铜片白磷燃/红磷不燃(着火点 240℃)→需达着火点；水中白磷不燃通氧后水下燃→需氧气；三条件=可燃物+O₂+达着火点；白磷 40℃ 水下保存。"),
    ("kp_card_biotech",
     "现代生物技术的应用",
     "基础科学知识点内容（人话接口）", "生物学",
     "现代生物技术四大领域：①**转基因技术**——转入外源基因（抗虫棉/黄金大米/微"
     "生物产胰岛素）；②**克隆技术**——体细胞核移植（克隆羊多莉/克隆猴中中华"
     "华）；③**干细胞技术**——造血干细胞移植治白血病/iPS 细胞再生医学；④**基因"
     "编辑**——CRISPR-Cas9「基因剪刀」（精确修改 DNA，2020 年诺奖，应用于治疗镰"
     "刀型贫血等遗传病研究）。传统生物技术对照：发酵（酸奶/泡菜/酿酒——微生物"
     "）、杂交育种、组织培养（植物快速繁殖——兰花工厂化）。生物安全与伦理：转基"
     "因标识制度、禁止生殖性克隆人、基因编辑婴儿事件被严惩——技术有边界、生命"
     "须敬畏。新冠 mRNA 疫苗是现代生物技术的集大成应用（把病毒特征「说明书」注"
     "入人体让细胞自产抗原）。",
     ["现代生物技术包括哪些", "什么是CRISPR技术", "克隆和转基因的区别",
      "组织培养的原理", "mRNA疫苗的原理", "生物技术有什么伦理问题"],
     ["问基因治疗进展", "问生物安全法规"],
     "atomic", "",
     "现代生物技术=转基因(抗虫棉)+克隆(多莉/中中华华)+干细胞(iPS 再生)+基因编辑(CRISPR 2020 诺奖)；传统=发酵/杂交/组培；mRNA 疫苗=集大成；伦理=禁克隆人/标识制。"),
    ("kp_card_northwest",
     "西北地区：干旱的自然特征",
     "人文通识知识点内容（人话接口）", "地理学",
     "西北地区（内蒙古/新疆/宁夏/甘肃北部）最突出的自然特征是**干旱**：成因——"
     "深居内陆、距海遥远，加上山岭阻隔，湿润气流难以到达（降水自东向西从 400mm"
     " 递减到 50mm 以下）。景观变化（自东向西）：草原→荒漠草原→荒漠（降水递减"
     "的「降水地图」）。农业特色：**畜牧业**为主（内蒙古温带草原牧场/新疆山地牧"
     "场——天山转场放牧）；**灌溉农业/绿洲农业**——宁夏平原、河套平原（「塞上江"
     "南」，黄河水灌溉）、新疆绿洲（坎儿井引地下水，特色作物：哈密瓜/葡萄/长绒"
     "棉——光照强昼夜温差大瓜果甜）。资源：煤石油天然气丰富（西气东输起点）、稀"
     "土（白云鄂博）。生态问题：荒漠化（过度放牧/开垦），治理=三北防护林/退牧还"
     "草。",
     ["西北地区自然环境的主要特征", "西北地区为什么干旱", "坎儿井的作用",
      "内蒙古发展什么农业", "西北地区的农业特色", "三北防护林"],
     ["问河西走廊", "问荒漠化治理案例"],
     "atomic", "",
     "西北=干旱(深居内陆距海远·400→50mm 自东向西递减)：畜牧为主(内蒙温带草原/新疆山地转场)+灌溉农业(河套塞上江南/新疆绿洲坎儿井·瓜果甜)；资源油气稀土；防荒漠化。"),
]

QUESTIONS = [
    ("QB-477", "并联电路的电流规律", "物理学", "技术直答",
     ["干路", "支路之和"], "通识拓展86"),
    ("QB-478", "怎么证明燃烧需要氧气", "化学", "技术直答",
     ["白磷", "对照实验"], "通识拓展86"),
    ("QB-479", "现代生物技术包括哪些", "生物学", "技术直答",
     ["转基因", "克隆", "干细胞", "基因编辑"], "通识拓展86"),
    ("QB-480", "西北地区自然环境的主要特征", "地理学", "技术直答",
     ["干旱"], "通识拓展86"),
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
                               "level:L2", "status:verified", "batch:通识拓展86"],
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
    bank["version"] = "v1.78"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
