# -*- coding: utf-8 -*-
"""seed_common_91_cards.py · 通识拓展批次91知识卡+题库（幂等）

91：物理学-光的折射定律/化学-材料发展史/生物学-呼吸系统的组成/地理学-中国降水分布
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_refrlaw",
     "光的折射定律",
     "基础科学知识点内容（人话接口）", "物理学",
     "光从一种介质斜射入另一种介质时传播方向偏折——折射。规律：①三线共面（入"
     "射/折射/法线）；②空气中角大、水中/玻璃中角小——光从空气斜射入水或玻璃："
     "折射角**小于**入射角（光线向法线靠拢）；从水斜射入空气：折射角大于入射角"
     "（远离法线）；③垂直入射不偏折；④光路**可逆**。生活现象解释：插入水中的筷"
     "子「折断」、池水看起来变浅（看到的池底是升高的虚像——所以看起来 1 米深实际"
     "更深，禁止贸然下水）、海市蜃楼（不均匀空气连续折射）、星星眨眼（大气抖"
     "动）。折射与反射同时发生：光到水面既反射又折射（所以水面也能照见自己）。",
     ["光从空气斜射入水中怎么偏折", "光的折射规律", "水中的筷子为什么看起来折断",
      "池水为什么看起来变浅", "什么是海市蜃楼", "折射时光路可逆吗"],
     ["问折射角入射角计算", "问鱼在水中看人"],
     "atomic", "",
     "折射规律：空气斜入水/玻璃→折射角<入射角(向法线靠)；斜出反之；垂直入射不偏·光路可逆；解释=筷子折断/池水变浅虚像/海市蜃楼；水面同时反射+折射。"),
    ("kp_card_mathist",
     "材料发展史的四个时代",
     "基础科学知识点内容（人话接口）", "化学",
     "人类材料史即文明史：①**石器时代**（史前）——天然材料：石头/骨头/木头；②"
     "**青铜时代**（约公元前 2000 年起，中国商周青铜鼎盛——司母戊鼎/四羊方尊）"
     "——铜锡合金，铸造技术；③**铁器时代**（春秋战国起中国领先——生铁冶铸技"
     "术早欧洲约 2000 年）——铁器普及促进农耕；④**合成材料时代**（20 世纪——"
     "塑料/合成纤维/合成橡胶+半导体硅：信息时代）。材料分类总览：金属材料（纯金"
     "属+合金）、无机非金属（陶瓷/玻璃/水泥）、有机合成材料（三大合成）、复合材"
     "料（玻璃钢/钢筋混凝土/碳纤维）。未来材料：石墨烯/超导/纳米材料/智能材料"
     "（形状记忆合金——眼镜架被折弯可复原）。",
     ["材料发展史的顺序", "青铜时代和铁器时代", "中国冶铁技术早欧洲多久",
      "材料分为哪四大类", "什么是形状记忆合金", "复合材料举例"],
     ["问高新材料前沿", "问材料与文明断代"],
     "atomic", "",
     "材料史=石器(天然)→青铜(铜锡合金·商周鼎盛)→铁器(春秋起·早欧 2000 年)→合成材料(20 世纪塑料+半导体)；四类=金属/无机非金属/有机合成/复合(玻璃钢碳纤维)；未来=石墨烯。"),
    ("kp_card_respsys",
     "呼吸系统的组成",
     "基础科学知识点内容（人话接口）", "生物学",
     "呼吸系统=**呼吸道**+**肺**。呼吸道（气体通道）：鼻→咽→喉→气管→支气管，"
     "特点与功能：①温暖（毛细血管加热冷空气）；②湿润（黏液加湿）；③清洁（鼻毛"
     "滤尘、黏液粘尘、纤毛清扫——「鼻涕」就是清扫成果）；故用鼻呼吸优于口呼吸。"
     "喉部有声带（发声）。**肺**是气体交换的场所：支气管入肺反复分支成肺泡（约 3"
     " 亿个，总表面积近百平方米）——肺泡壁和毛细血管壁都只有**一层上皮细胞**，"
     "利于气体扩散（氧气入血、二氧化碳出）。呼吸运动=肋间肌+膈肌收缩舒张改变胸"
     "廓容积（吸气时膈肌收缩下降——「肚子鼓起」）。戒烟：烟草烟雾损伤纤毛+致癌，"
     "呼吸道清洁能力丧失。",
     ["呼吸系统的组成", "呼吸道对空气的处理", "肺泡适合气体交换的特点",
      "呼吸运动是怎么完成的", "为什么用鼻呼吸比用口好", "吸烟对呼吸系统的危害"],
     ["问哮喘慢阻肺", "问气体交换原理复习"],
     "atomic", "",
     "呼吸系统=呼吸道(鼻咽喉气管支气管：温暖湿润清洁)+肺(肺泡 3 亿个·壁一层细胞·面积近百㎡ 交换)；呼吸运动=肋间肌+膈肌；吸烟损纤毛致癌。"),
    ("kp_card_raindist",
     "中国降水的分布",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国降水分布规律：①**空间**——从东南沿海向西北内陆递减（东南受夏季风影响"
     "大、西北深居内陆）：降水最多=台湾火烧寮（年均 6000mm+，「雨极」）；最少=新"
     "疆吐鲁番托克逊（年均不足 10mm）。②**时间**——夏秋多、冬春少；年际变化大"
     "（夏季风不稳定→旱涝交替）。干湿地区划分（降水量与蒸发量对比）：湿润区（秦"
     "岭淮河以南——森林）、半湿润区（东北/华北——森林草原）、半干旱区（内蒙古/"
     "黄土高原——草原）、干旱区（西北——荒漠）。对农业：湿润区水田、半湿润旱"
     "地、半干旱草原畜牧、干旱区绿洲农业——「降水分布决定农业格局」。原因：夏季"
     "风进退+海陆位置+地形。",
     ["中国降水分布规律", "中国降水最多的地方", "中国干湿地区的划分",
      "为什么西北降水少", "降水对农业的影响", "什么是雨极"],
     ["问夏季风停滞梅雨", "问降水年际变化灾害"],
     "atomic", "",
     "降水分布=东南沿海向西北内陆递减：最多=火烧寮(6000mm+·雨极)/最少=托克逊(<10mm)；四干湿区=湿润(森林)半湿润半干旱(草原)干旱(荒漠)→水田/旱地/畜牧/绿洲。"),
]

QUESTIONS = [
    ("QB-497", "光从空气斜射入水中怎么偏折", "物理学", "技术直答",
     ["折射角", "小于", "法线"], "通识拓展91"),
    ("QB-498", "材料发展史的顺序", "化学", "技术直答",
     ["石器", "青铜", "铁器", "合成材料"], "通识拓展91"),
    ("QB-499", "呼吸系统的组成", "生物学", "技术直答",
     ["呼吸道", "肺"], "通识拓展91"),
    ("QB-500", "中国降水分布规律", "地理学", "技术直答",
     ["东南", "西北", "递减"], "通识拓展91"),
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
                               "level:L2", "status:verified", "batch:通识拓展91"],
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
    bank["version"] = "v1.83"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
