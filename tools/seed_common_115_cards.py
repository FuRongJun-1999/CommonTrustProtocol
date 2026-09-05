# -*- coding: utf-8 -*-
"""seed_common_115_cards.py · 通识拓展批次115知识卡+题库（幂等）

115：物理学-太阳能的利用/化学-焰色反应/生物学-献血与健康/地理学-聚落与环境
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_solaruse",
     "太阳能利用的三种方式",
     "基础科学知识点内容（人话接口）", "物理学",
     "太阳能利用三种方式：①**光热转换**——把光能转化为内能：太阳能热水器（集"
     "热管）、太阳灶、太阳能供暖——最简单直接的方式；②**光电转换**——太阳能电"
     "池（光伏板）把光能直接转化为电能（solarcell 呼应：光生伏特效应）；③**光"
     "化转换**——光能转化为化学能：植物光合作用（天然的）、光化学电池。太阳能"
     "优点：清洁无污染、可再生、无处不在；缺点：分散、不稳定（昼夜阴晴）、储能"
     "难。中国是全球最大的光伏发电国和应用国（青海塔拉滩光伏园区——「光伏羊」"
     "在板下吃草，板上发电板下牧羊）。太阳能寿命长（光伏板 25 年+）、维护成本低。",
     ["太阳能的利用方式有哪些", "光热转换和光电转换", "太阳能热水器原理",
      "光伏发电和太阳能热发电的区别", "中国光伏产业世界第一", "太阳能的优缺点"],
     ["问光伏农业", "问太阳能储能技术"],
     "atomic", "",
     "太阳能利用三式=光热(热水器/太阳灶)+光电(光伏板·光生伏特)+光化(光合)；优点清洁可再生/缺点分散不稳难储能；中国光伏装机全球第一；板下牧羊=农光互补。"),
    ("kp_card_flametest",
     "焰色反应：烟花的颜色密码",
     "基础科学知识点内容（人话接口）", "化学",
     "焰色反应：某些金属或其化合物在无色火焰中灼烧时呈现**特征颜色**的物理现"
     "象（电子跃迁发光）——不是化学变化。常见焰色：钠——黄色（食盐在火焰上烧"
     "出黄光）、钾——紫色（透过蓝色钴玻璃观察，滤去黄光干扰）、钙——砖红色、"
     "锶——洋红色、钡——黄绿色、铜——绿色。应用：①烟花五彩缤纷=添加不同金属"
     "盐；②检验金属元素（定性分析——钠黄、钾紫是经典考点）；③节日信号弹。注"
     "意：焰色反应是物理变化（元素本身性质，与化合价化学键无关），且可用于检验"
     "微量金属（灵敏度极高）。",
     ["烟花为什么有各种颜色", "什么是焰色反应", "钠的焰色反应是什么颜色",
      "钾的焰色反应为什么要透过蓝色钴玻璃", "焰色反应是化学变化吗",
      "焰色反应的应用"],
     ["问光谱分析法", "问烟花化学配方"],
     "atomic", "",
     "焰色反应=金属灼烧特征色(物理变化·电子跃迁)：钠黄/钾紫(钴玻璃滤黄)/钙砖红/锶洋红/钡黄绿/铜绿；烟花五色=不同金属盐；灵敏到可检微量金属。"),
    ("kp_card_blooddonor",
     "献血与健康",
     "基础科学知识点内容（人话接口）", "生物学",
     "健康成年人献血 200-300 毫米（ml）**不影响健康**：损失的血量占全身血量"
     "（4000-5000ml）不到 10%——血浆中的水分和无机盐 1-2 小时内恢复，血浆蛋白"
     " 1-2 天恢复，红细胞约一个月完全恢复；适量献血还能**刺激骨髓造血功能**。"
     "献血条件：年龄 18-55 周岁、体重男≥50kg/女≥45kg、血压正常、无经血传染疾"
     "病。献血前：清淡饮食不空腹、保证睡眠；献血后：按压针眼 10 分钟、24 小时"
     "内不剧烈运动、适当多喝水。一次献血 400ml 比 200ml 更利于成分分离（科学界"
     "共识不影响健康）。无偿献血制度保证血液安全（有偿供血易隐瞒病史）。",
     ["献血会损害健康吗", "一次献血多少毫升", "献血后多久恢复",
      "献血的条件是什么", "献血后注意什么", "为什么提倡无偿献血"],
     ["问造血干细胞动员", "问稀有血型库"],
     "atomic", "",
     "献血 200-300ml 无碍健康(占全血<10%)：血浆 1-2 天恢复·红细胞 1 月·并刺激骨髓造血；条件=18-55 岁·男 50kg 女 45kg·血压正常；献血后按压+多水+24h 勿剧烈运动。"),
    ("kp_card_settlement",
     "聚落：人类居住地的形成",
     "人文通识知识点内容（人话接口）", "地理学",
     "聚落=人类聚居和生活的场所（乡村聚落+城市聚落）。形成与环境密切相关：**依"
     "山傍水**——水源充足（河流沿岸）、地形平坦、土壤肥沃、交通便利、气候适宜"
     "（古代文明都发源于大河流域：尼罗河/两河/印度河/黄河长江）。民居与环境适"
     "应：①东南亚高脚屋（防潮防虫）；②北极冰屋（因纽特人——保温）；③黄土高"
     "原窑洞（黄土直立性+冬暖夏凉）；④云南竹楼（散热防潮）；⑤西亚厚墙小窗平"
     "顶（隔热少雨）。乡村聚落与城市聚落差异：规模/建筑密度/职业/景观——乡村"
     "从事农耕牧渔，城市以工商业服务业为主。传统聚落是文化遗产（如平遥古城/丽"
     "江古城/皖南古村落——已被列为世界遗产），要保护性开发。",
     ["聚落的形成与环境的关系", "民居与气候的关系", "高脚屋分布在哪",
      "窑洞为什么冬暖夏凉", "乡村聚落和城市聚落的区别", "为什么要保护传统聚落"],
     ["问世界民居赏析", "问城市化进程问题"],
     "atomic", "",
     "聚落形成=水源+地形平坦+土壤肥沃+交通便利+气候适宜（大河文明摇篮）；民居适应气候=高脚屋(湿热)/冰屋(极寒)/窑洞(黄土直立)/竹楼；传统聚落=文化遗产保护。"),
]

QUESTIONS = [
    ("QB-598", "太阳能的利用方式有哪些", "物理学", "技术直答",
     ["光热", "光电"], "通识拓展115"),
    ("QB-599", "烟花为什么有各种颜色", "化学", "技术直答",
     ["焰色反应", "金属"], "通识拓展115"),
    ("QB-600", "献血会损害健康吗", "生物学", "技术直答",
     ["不会", "恢复"], "通识拓展115"),
    ("QB-601", "聚落的形成与环境的关系", "地理学", "技术直答",
     ["水源", "地形", "气候"], "通识拓展115"),
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
                               "level:L2", "status:verified", "batch:通识拓展115"],
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
    bank["version"] = "v2.9"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
