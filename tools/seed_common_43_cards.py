# -*- coding: utf-8 -*-
"""seed_common_43_cards.py · 通识拓展批次43知识卡+题库（幂等）

43：化学-雾霾与空气质量/历史-虎门销烟/生物学-恐龙灭绝/数学-轴对称图形
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_haze",
     "雾霾与空气质量指数",
     "基础科学知识点内容（人话接口）", "化学",
     "雾霾是雾和霾的合称：雾是水滴（自然现象），霾是空气中悬浮的大量细颗粒物"
     "（污染现象）。核心指标 PM2.5——直径 ≤2.5 微米的细颗粒物，能深入肺泡甚至"
     "进入血液，比 PM10（≤10 微米）危害更大。来源：燃煤/机动车尾气/工业排放/"
     "工地扬尘/秸秆焚烧等；不利气象条件（静风、逆温层）会加剧积累。空气质量指"
     "数 AQI 分六级（优/良/轻度/中度/重度/严重污染，对应不同颜色）。防护：重污"
     "染天减少户外活动、戴 N95/KN95 口罩、开空气净化器。治理手段：能源结构调整、"
     "机动车限排、扬尘管控——近年我国 PM2.5 浓度已显著下降。",
     ["雾霾是怎么形成的", "PM2.5是什么", "雾霾天为什么要戴口罩",
      "AQI是什么意思", "PM2.5和PM10哪个危害大", "怎样防护雾霾"],
     ["问逆温层气象细节", "问酸雨对比"],
     "atomic", "",
     "霾=悬浮细颗粒物(雾=水滴)；PM2.5≤2.5μm 深入肺泡入血最毒；来源=燃煤/尾气/扬尘；AQI 六级；防护=N95/净化器/减外出。"),
    ("kp_card_linzexu",
     "虎门销烟",
     "人文通识知识点内容（人话接口）", "历史",
     "虎门销烟（1839 年 6 月）：钦差大臣林则徐在广东虎门海滩当众销毁收缴的鸦片"
     "约 118 万公斤（2 万余箱），历时 23 天——不是烧而是「海水浸化法」（盐水泡"
     "浸+石灰发酵，销毁彻底且不留残膏）。背景：英国为扭转对华贸易逆差向中国大"
     "量走私鸦片，吸食者上瘾致白银外流、国民体质崩溃；林则徐名言「苟利国家生死"
     "以，岂因祸福避趋之」。虎门销烟是第一次鸦片战争（1840）的导火索；战争失败"
     "后 1842 年签订《南京条约》（中国近代史上第一个不平等条约，割香港岛）。6 "
     "月 26 日国际禁毒日的设立与虎门销烟精神相关。",
     ["虎门销烟是谁领导的", "虎门销烟发生在哪一年", "林则徐的名言",
      "鸦片战争的导火索是什么", "南京条约的内容", "销烟为什么用海水浸化而不是烧"],
     ["问条约体系细节", "问禁毒史"],
     "atomic", "",
     "虎门销烟=1839.6 林则徐虎门浸化销烟 118 万kg（23天）；「苟利国家生死以」；鸦片战争(1840)导火索→1842《南京条约》第一个不平等条约。"),
    ("kp_card_dino",
     "恐龙的灭绝",
     "基础科学知识点内容（人话接口）", "生物学",
     "恐龙统治地球约 1.6 亿年（三叠纪晚期出现，侏罗纪繁盛），在约 6600 万年前的"
     "白垩纪末期突然全部灭绝（除演化成鸟类的一支兽脚类恐龙——鸟类就是恐龙的后"
     "裔）。主流解释是「小行星撞击假说」：直径约 10 公里的小行星撞击今墨西哥尤"
     "卡坦半岛（希克苏鲁伯陨石坑，直径约 180 公里），撞击掀起遮天尘埃与硫酸盐气"
     "溶胶，阳光被遮蔽、光合作用崩溃→食物链断裂→全球性寒冬。支持证据：地层中"
     "铱元素异常富集（铱在地表罕见、小行星中常见）。另有德干暗色岩大火山喷发（加"
     "剧气候变化）等多因素叠加说。恐龙时代：侏罗纪的霸王龙（白垩纪）、梁龙、三角"
     "龙都是代表；「翼龙/蛇颈龙不是恐龙」（亲缘关系不同）。",
     ["恐龙是怎么灭绝的", "恐龙灭绝发生在多少年前", "希克苏鲁伯陨石坑",
      "鸟类是恐龙的后裔吗", "恐龙灭绝的假说有哪些", "翼龙是恐龙吗"],
     ["问地质年代划分", "问化石形成条件"],
     "atomic", "",
     "恐龙 6600 万年前灭绝：主流=10km 小行星撞尤卡坦(希克苏鲁伯坑)→尘埃蔽日光合崩溃→寒冬断链；证据=地层铱异常；鸟类=兽脚类恐龙后裔；翼龙非恐龙。"),
    ("kp_card_symmetry",
     "轴对称与轴对称图形",
     "基础科学知识点内容（人话接口）", "数学",
     "轴对称图形：沿一条直线对折后两部分完全重合的图形，这条线叫对称轴。常见例"
     "子：等腰三角形（1 条对称轴，顶角平分线所在直线）、矩形（2 条）、正方形（4"
     " 条）、圆（无数条——对称轴之王）、等边三角形（3 条）、角（1 条，角平分线）。"
     "两个图形成轴对称：一个图形沿对称轴翻折能与另一个图形完全重合（如人的左手"
     "与右手镜像）。注意区分「轴对称图形」（一个图形自身性质）与「两个图形成轴"
     "对称」（两个图形的位置关系）。生活应用：剪纸/蝴蝶翅膀/建筑立面设计；轴对"
     "称在镜面反射、汉字结构（中、田、美）中也常见。",
     ["什么是轴对称图形", "圆有多少条对称轴", "正方形有几条对称轴",
      "等腰三角形的对称轴", "轴对称和轴对称图形的区别", "生活中哪些是轴对称的"],
     ["问中心对称对比", "问坐标系中的对称变换"],
     "atomic", "",
     "轴对称图形=沿直线对折完全重合：等腰△1条/矩形2条/等边△3条/正方形4条/圆∞条；区别「两图形成轴对称」(位置关系)；例=剪纸/蝴蝶/汉字中田。"),
]

QUESTIONS = [
    ("QB-305", "雾霾是怎么形成的", "化学", "技术直答",
     ["PM2.5", "颗粒物"], "通识拓展43"),
    ("QB-306", "虎门销烟是谁领导的", "历史", "技术直答",
     ["林则徐"], "通识拓展43"),
    ("QB-307", "恐龙是怎么灭绝的", "生物学", "技术直答",
     ["小行星撞击", "陨石"], "通识拓展43"),
    ("QB-308", "什么是轴对称图形", "数学", "技术直答",
     ["对折", "重合", "对称轴"], "通识拓展43"),
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
                               "level:L2", "status:verified", "batch:通识拓展43"],
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
    bank["version"] = "v1.35"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
