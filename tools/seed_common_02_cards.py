# -*- coding: utf-8 -*-
"""seed_common_02_cards.py · 生活常识第二批知识卡（幂等）

02：地震安全应对/食品保存方法/烫伤处理/声音传播条件
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_quakesafe",
     "地震发生时的应对方法",
     "生活常识知识点内容（人话接口）", "安全常识",
     "地震发生时室内应对：①迅速躲到坚固的桌子下或承重墙角，保护头部（伏地、"
     "遮挡、手抓牢）；②远离窗户、吊灯、书柜等易坠落物；③切勿乘坐电梯、切勿"
     "跳楼；④晃动停止后有序从安全通道撤离到开阔地带。室外应远离建筑物、电线"
     "杆、广告牌，就近选择开阔地带蹲下。震后余震可能持续，注意收听官方信息。",
     ["地震发生时怎么办", "地震来了怎么应对", "地震避险方法", "地震时应该躲在哪里",
      "地震安全知识", "地震自救"],
     ["问地震预报", "问震后救援"],
     "atomic", "",
     "地震应对 = 伏地遮挡手抓牢→远离坠落物→不坐电梯不跳楼→晃停后撤离到开阔地→防余震。"),
    ("kp_card_foodpreserve",
     "常见食品保存方法",
     "生活常识知识点内容（人话接口）", "食品安全",
     "常见食品保存方法及原理：冷藏（4°C 以下抑制细菌繁殖，适合果蔬乳品）；冷"
     "冻（-18°C 以下基本停止微生物活动，适合肉类长期保存）；干燥/脱水（去除水"
     "分抑制微生物，如米面干货）；腌制（高盐高糖形成高渗透压抑菌，如咸菜蜂蜜）；"
     "真空包装（隔绝氧气抑制好氧菌）；巴氏杀菌（加热杀灭病原菌后冷链保存，如牛"
     "奶）。核心原则都是抑制或杀灭导致食品变质的微生物。",
     ["食品怎么保存", "常见食品保存方法", "冷藏和冷冻的区别", "食品保鲜",
      "真空包装原理", "腌制食品为什么能保存"],
     ["问罐头原理", "问食品添加剂"],
     "atomic", "",
     "食品保存核心=抑制微生物；方法=冷藏/冷冻/干燥/腌制/真空/巴氏杀菌，各适用不同食品。"),
    ("kp_card_burnfirstaid",
     "烫伤的正确处理方法",
     "生活常识知识点内容（人话接口）", "急救常识",
     "烫伤正确处理五步（冲脱泡盖送）：①冲——立即用流动冷水（15-25°C）冲洗"
     "15-30 分钟降温止痛；②脱——小心除去衣物，粘连处勿强行撕脱；③泡——冷水"
     "浸泡缓解疼痛；④盖——用干净纱布或布巾轻轻覆盖创面；⑤送——严重烫伤及时"
     "送医。绝对禁止：涂牙膏/酱油/香油（会感染且妨碍散热）、挑破水泡（易感染）、"
     "用冰块直接敷（冻伤加重损伤）。",
     ["烫伤了怎么处理", "烫伤急救", "烫伤后怎么处理", "烫伤能不能涂牙膏",
      "烫伤五步", "冲脱泡盖送"],
     ["问割伤处理", "问骨折急救"],
     "atomic", "",
     "烫伤五步 = 冲（冷水15-30min）→脱→泡→盖→送；禁止牙膏酱油冰块直敷；水泡勿挑破。"),
    ("kp_card_soundmedium",
     "声音传播需要介质",
     "基础科学知识点内容（人话接口）", "物理学",
     "声音传播需要介质：声音是振动在介质中传播的机械波，固体、液体、气体都能"
     "传声但真空不能传声——因为真空中没有物质粒子来传递振动。声速在不同介质中"
     "不同：一般固体>液体>气体（如钢铁约 5000m/s、水约 1500m/s、空气 15°C 约"
     " 340m/s）——介质分子间距越小、弹性越大，传声越快。",
     ["声音传播需要什么", "声音在真空中能传播吗", "声音的传播", "为什么真空不能传声",
      "声音在不同介质中的速度", "问声传播条件"],
     ["问超声波", "问多普勒效应"],
     "atomic", "",
     "声传声需介质（固/液/气），真空不能传声；声速固>液>气；本质=振动通过粒子依次传递。"),
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
                "name": f"{name}（{dgroup}·生活常识知识卡）",
                "生效条件": conds,
                "子功能": f"{name}——生活常识高频问题知识条目",
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
                               "level:L2", "status:verified", "batch:生活常识02"],
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
    return {"inserted": inserted, "updated": updated, "skipped": skipped}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
