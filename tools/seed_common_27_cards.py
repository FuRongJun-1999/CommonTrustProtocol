# -*- coding: utf-8 -*-
"""seed_common_27_cards.py · 通识拓展批次27知识卡+题库（幂等·新域+深化混合）

27：物理学-增大减小摩擦（深化）/生活常识-冰箱保鲜/历史-兵马俑/自然常识-云和雾
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_frictionctrl",
     "增大与减小摩擦的方法",
     "基础科学知识点内容（人话接口）", "物理学",
     "摩擦力有利也有弊，按需要调控：增大摩擦——增大压力（刹车时用力捏闸）、增"
     "大接触面粗糙程度（鞋底轮胎花纹/防滑垫/瓶盖竖纹）、刹车抱死（滑动摩擦大于"
     "滚动摩擦）；减小摩擦——变滑动为滚动（轴承滚珠/行李箱轮）、加润滑油（形成"
     "油膜分离接触面）、减小压力、气垫悬浮（气垫船）。同一现象两种用途：轮胎花"
     "纹增大摩擦防打滑，冰面上摩擦小所以易摔倒——「没有摩擦力的世界」人将无法"
     "行走（靠摩擦蹬地）、筷子夹不住东西。",
     ["怎么增大摩擦力", "怎么减小摩擦力", "轴承为什么用滚珠", "鞋底花纹的作用",
      "润滑油是怎么减小摩擦的", "如果没有摩擦力会怎样"],
     ["问摩擦力方向判断", "问静摩擦与动摩擦计算"],
     "atomic", "",
     "增摩擦=加压/加糙(轮胎花纹)；减摩擦=滚动代滑动(滚珠轴承)/润滑油/气垫；无摩擦世界=无法行走。"),
    ("kp_card_fridge",
     "冰箱保鲜的原理",
     "生活常识知识点内容（人话接口）", "生活常识",
     "食物变质的主要原因是微生物（细菌/霉菌）繁殖和酶的分解作用。冰箱保鲜的核"
     "心是「低温抑菌」而非杀菌：冷藏室（0-10℃，常用 4℃ 左右）抑制大多数细菌"
     "繁殖速度，延长保质期，但李斯特菌等嗜冷菌仍可缓慢生长——冷藏食品也要尽快"
     "吃，剩菜取出须彻底加热；冷冻室（-18℃ 以下）微生物基本停止活动，可保存数"
     "月，但解冻后要立即食用。冰箱不是保险箱：生熟分开（防止交叉污染）、食物密"
     "封存放、定期清理。冰箱制冷原理=制冷剂循环：压缩→冷凝放热→膨胀→蒸发吸热"
     "把箱内热量搬到箱外。",
     ["冰箱为什么能保鲜", "冷藏和冷冻有什么区别", "冰箱能杀死细菌吗",
      "剩菜放冰箱就安全吗", "冰箱制冷的原理是什么", "生熟食物为什么要分开存放"],
     ["问冰箱除霜方法", "问不同食材最佳保存温度"],
     "atomic", "",
     "冰箱=低温抑菌非杀菌：冷藏0-10℃减缓繁殖(嗜冷菌仍长)/冷冻-18℃停止活动；生熟分开防交叉污染；制冷剂循环搬热。"),
    ("kp_card_terracotta",
     "秦始皇陵兵马俑",
     "人文通识知识点内容（人话接口）", "历史",
     "秦始皇陵兵马俑：位于陕西西安临潼，是秦始皇陵的大型陪葬坑，1974 年由当地"
     "农民打井时意外发现，被誉为「世界第八大奇迹」，1987 年与长城等同批入选世"
     "界文化遗产。已发掘三个俑坑，出土陶俑陶马约 8000 件——一号坑最大（步兵与"
     "战车主力军阵）；兵马俑千人千面、发髻铠甲细节各异，原为彩绘，出土后氧化"
     "褪色；另出土铜车马、青铜剑（铬盐氧化处理防锈之谜）等珍贵文物。它是秦代"
     "军事、雕塑、冶金技术的集中实证。",
     ["秦始皇陵兵马俑是什么", "兵马俑是哪年被发现的", "兵马俑在世界哪个城市",
      "兵马俑为什么是世界第八大奇迹", "兵马俑原来是什么颜色", "铜车马在哪里出土"],
     ["问秦陵地宫勘探争议", "问秦代军制细节"],
     "atomic", "",
     "兵马俑=秦始皇陵陪葬坑(西安临潼)，1974 农民打井发现·世界第八大奇迹·1987 非遗；约8000 陶俑千人千面，原彩绘。"),
    ("kp_card_cloudfog",
     "云和雾是怎么形成的",
     "基础科学知识点内容（人话接口）", "自然常识",
     "云和雾本质相同——都是空气中的水蒸气遇冷「液化」成的小水滴（或凝华成小冰"
     "晶），只是位置不同：地面附近的水蒸气在夜间遇冷凝结成雾（贴近地表，日出升"
     "温后消散）；高空的水蒸气上升遇冷（高空温度低）凝结在尘埃上形成云。相关现"
     "象同一原理：露水（草叶上水蒸气液化）、白气（冬天呵气/冰棒周围「白烟」="
     "水蒸气液化成小水滴——水蒸气本身看不见，看得见的「白气」已不是蒸气）。夏"
     "季自来水管「出汗」也是水蒸气遇冷水管液化。",
     ["云和雾是怎么形成的", "雾和云有什么区别", "冬天呼出的白气是什么",
      "露水是怎么形成的", "水蒸气能看见吗", "水管为什么会出汗"],
     ["问雨雪形成链条", "问人工降雨原理"],
     "atomic", "",
     "云雾=水蒸气遇冷液化成小水滴：贴地=雾/高空=云；露水/白气/管出汗同理；水蒸气不可见，见到的白气已是水滴。"),
]

QUESTIONS = [
    ("QB-241", "轴承为什么用滚珠", "物理学", "技术直答",
     ["滚动摩擦", "减小摩擦"], "通识拓展27"),
    ("QB-242", "冰箱为什么能保鲜", "生活常识", "技术直答",
     ["低温", "抑制细菌"], "通识拓展27"),
    ("QB-243", "兵马俑是哪年被发现的", "历史", "技术直答",
     ["1974"], "通识拓展27"),
    ("QB-244", "冬天呼出的白气是什么", "自然常识", "技术直答",
     ["液化", "小水滴"], "通识拓展27"),
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
                               "level:L2", "status:verified", "batch:通识拓展27"],
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
    bank["version"] = "v1.19"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
