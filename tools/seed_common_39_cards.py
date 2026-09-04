# -*- coding: utf-8 -*-
"""seed_common_39_cards.py · 通识拓展批次39知识卡+题库（幂等）

39：化学-氢气/地理学-赤道与经纬线/生物学-眼睛的成像/物理学-热胀冷缩
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_hydrogen",
     "氢气：最轻与最清洁的燃料",
     "基础科学知识点内容（人话接口）", "化学",
     "氢气（H₂）是密度最小的气体（约为空气的 1/14，曾用于飞艇——1937 年兴登"
     "堡号因氢气易燃失事后再改用惰性的氦气）。氢气燃烧只生成水：2H₂+O₂→点燃"
     "→2H₂O，无二氧化碳无污染物，是最清洁的燃料——氢能源被视为碳中和时代的"
     "终极能源之一（绿氢=用可再生电力电解水制氢）。安全特性：可燃范围宽（空气"
     "中 4%~75% 都可能爆炸），点燃前必须验纯（听爆鸣声）。实验室制法：锌粒+稀硫"
     "酸（置换反应），向下排空气法或排水法收集。",
     ["氢气燃烧生成什么", "为什么说氢气是最清洁的燃料", "氢气为什么能用于飞艇",
      "点燃氢气前为什么要验纯", "实验室怎么制取氢气", "什么是绿氢"],
     ["问氢燃料电池电化学细节", "问储氢材料"],
     "atomic", "",
     "氢气=最轻气体(1/14空气)·燃烧只生成水=最清洁；可燃范围宽点燃前必验纯；实验室=锌+稀硫酸置换；绿氢=可再生电电解水。"),
    ("kp_card_equator",
     "赤道与经纬线",
     "人文通识知识点内容（人话接口）", "地理学",
     "经纬网是地球的「坐标格」：纬线是东西方向的圆圈——赤道是 0° 纬线，也是最"
     "长的纬线（约 4 万公里），把地球分成南北两半球；纬度从赤道向两极递增到 90"
     "°。经线是连接南北两极的半圆——本初子午线是 0° 经线（过英国格林尼治天文"
     "台），经度向东向西各分 180°。经纬度定位：北京约 (40°N, 116°E)。实用意义："
     "赤道地区终年太阳直射、最热；纬线圈越靠近两极越短；经线指示南北方向、纬线"
     "指示东西方向；时区按经度划分（每 15° 相差 1 小时）。",
     ["什么是赤道", "赤道是南北半球的分界线吗", "本初子午线在哪里",
      "经线和纬线怎么区分", "北京的经纬度", "时区是怎么划分的"],
     ["问五带划分", "问GPS定位原理"],
     "atomic", "",
     "赤道=0°纬线·最长(4万km)·南北半球分界；本初子午线=0°经线(格林尼治)；经线定南北/纬线定东西；时区每15°差1小时。"),
    ("kp_card_eyelens",
     "眼睛如何看清远近",
     "基础科学知识点内容（人话接口）", "生物学",
     "眼睛像一台自动对焦的凸透镜相机：角膜+晶状体共同折射光线，在视网膜上成倒"
     "立缩小的实像，视神经把信号传给大脑「翻转」成正立世界。看远看近的调节：睫"
     "状体改变晶状体的弯曲度——看远时晶状体变薄（折光弱），看近时变厚（折光"
     "强），使像始终落在视网膜上。近视：眼轴过长或晶状体过凸，像落在视网膜**前"
     "**方→戴凹透镜（负度数）矫正；远视相反（像成在视网膜后→凸透镜矫正）；老"
     "花是晶状体弹性随年龄下降、调节变慢。护眼要点：远眺放松睫状体、光线充足、"
     "控制近距离用眼时长。",
     ["眼睛如何看清远近物体", "晶状体是怎么调节的", "近视的成像原理",
      "近视为什么戴凹透镜", "远视和老花一样吗", "视网膜上的像是正立还是倒立"],
     ["问眼镜度数计算", "问散光成因"],
     "atomic", "",
     "眼=自动对焦凸透镜：角膜+晶状体折射→视网膜倒立实像；睫状体调晶状体厚薄(远薄近厚)；近视=像成视网膜前→凹透镜矫正；远视/老花→凸透镜。"),
    ("kp_card_expansion",
     "热胀冷缩与温度计",
     "基础科学知识点内容（人话接口）", "物理学",
     "绝大多数物体受热膨胀、遇冷收缩——温度计就是利用液体（水银/酒精/煤油）"
     "热胀冷缩的原理制成的：温度升高液体体积膨胀沿细管上升，读出温度。生活实"
     "例：鸡蛋刚煮好放冷水里泡一下易剥壳（蛋壳膜与蛋白收缩程度不同）、夏天电线"
     "架得松（留出冷缩余量）、铁轨接缝留缝隙、瓶盖拧不开用热水烫（金属盖比玻"
     "璃胀得快而松）、实心桥两端留伸缩缝。反常膨胀特例：水在 4℃ 时密度最大，"
     "0~4℃ 反而「冷胀」——所以冰浮在水面上、湖底 4℃ 的水让鱼能过冬。气体的热"
     "胀冷缩最明显，固体最不明显（但应力巨大）。",
     ["温度计是根据什么原理制成的", "什么是热胀冷缩", "为什么铁轨接缝有缝隙",
      "热水为什么能烫开瓶盖", "水的反常膨胀是什么", "为什么冰浮在水面上"],
     ["问双金属片温控应用", "问热力学膨胀系数"],
     "atomic", "",
     "热胀冷缩=温度计原理；工程=铁轨缝/电线松架/伸缩缝(留冷缩余量)；瓶盖热水烫=金属胀得快；反常膨胀=水 4℃ 密度最大→冰浮·湖底 4℃ 鱼过冬。"),
]

QUESTIONS = [
    ("QB-289", "氢气燃烧生成什么", "化学", "技术直答",
     ["水"], "通识拓展39"),
    ("QB-290", "赤道是南北半球的分界线吗", "地理学", "技术直答",
     ["是", "0度纬线"], "通识拓展39"),
    ("QB-291", "眼睛如何看清远近物体", "生物学", "技术直答",
     ["晶状体", "调节"], "通识拓展39"),
    ("QB-292", "温度计是根据什么原理制成的", "物理学", "技术直答",
     ["热胀冷缩"], "通识拓展39"),
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
                               "level:L2", "status:verified", "batch:通识拓展39"],
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
    bank["version"] = "v1.31"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
