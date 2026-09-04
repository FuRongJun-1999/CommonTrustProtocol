# -*- coding: utf-8 -*-
"""seed_common_32_cards.py · 通识拓展批次32知识卡+题库（幂等）

32：天文学-银河系与太阳系/生活常识-暖气与对流/历史-大禹治水/体育学-足球点球
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_milkywaypos",
     "太阳系在银河系中的位置",
     "基础科学知识点内容（人话接口）", "天文学",
     "银河系是一个棒旋星系：直径约 10 万光年，包含约 1000-4000 亿颗恒星。太阳"
     "系不在银河系中心，而是位于一条小旋臂——猎户臂（本地臂）上，距银河系中心"
     "约 2.6 万光年；太阳带着八大行星绕银心公转一周约 2.3 亿年（一个「银河"
     "年」）。我们夜空中看到的「银河」是银河系盘面恒星密集带在天球上的投影。银"
     "河系中心存在超大质量黑洞人马座 A*；银河系又与仙女座星系等约 50 个星系组"
     "成本星系群——尺度层层放大：地球→太阳系→银河系→本星系群→可观测宇宙"
     "（直径约 930 亿光年）。",
     ["太阳系在银河系的什么位置", "银河系有多大", "银河年是多少年",
      "夜空中的银河是什么", "银河系中心有什么", "可观测宇宙有多大"],
     ["问星系分类哈勃序列", "问暗物质证据"],
     "atomic", "",
     "太阳系位于银河系猎户臂，距银心约2.6万光年；银河系=棒旋·10万光年·千亿恒星；公转一周2.3亿年=银河年；银心=人马座A*。"),
    ("kp_card_convection",
     "暖气片为什么装在房间下方",
     "基础科学知识点内容（人话接口）", "生活常识",
     "暖气片装在窗户下方/房间低处，利用的是热对流：空气受热膨胀变轻（密度变"
     "小）上升，冷空气下降补充，形成「下进上出」的循环，把整个房间烘热——装"
     "在低处才能让热空气从地面整体升腾循环；装在屋顶则热空气滞留顶部、脚下依"
     "然冷（「头热脚冷」）。同理：空调制冷时风向朝上吹（冷气下沉循环）、冰箱冷"
     "冻室在上层（冷空气下沉，冷藏室在下靠冷气下沉补足？实际上直冷冰箱冷冻在"
     "上正是利用冷空气重）。烧开水、篝火上方空气流动、海陆风的形成都是热对流。",
     ["暖气片为什么装在房间下方", "什么是热对流", "空调制冷为什么朝上吹",
      "热空气为什么会上升", "海陆风是怎么形成的", "烧开水的水怎么循环"],
     ["问热辐射与热传导对比", "问保温瓶结构"],
     "atomic", "",
     "暖气装低处=热对流循环：热空气轻上升·冷空气降补；空调制冷朝上吹同理；三传热=传导/对流/辐射。"),
    ("kp_card_dayu",
     "大禹治水：疏而不堵",
     "人文通识知识点内容（人话接口）", "历史",
     "大禹治水是中国上古著名传说：尧舜时代黄河流域洪水泛滥，鲧（禹的父亲）用"
     "「堵」的方法筑堤围堵九年不成被处死；禹改用「疏导」——疏通河道、开渠引"
     "洪入海，历十三年三过家门而不入，终于平定水患。舜因此禅让部落联盟首领之"
     "位给禹，禹的儿子启建立中国第一个王朝夏（「公天下」变「家天下」）。大禹治"
     "水的方法论寓意深远：治理要顺应水性因势利导——「堵不如疏」至今仍用于治"
     "理思路的比喻。相关考古：二里头遗址被认为可能是夏代中晚期都城。",
     ["大禹治水用的什么方法", "鲧治水为什么失败", "三过家门而不入说的是谁",
      "中国第一个王朝是什么", "禅让制变成了什么制度", "二里头遗址和夏朝的关系"],
     ["问上古神话体系", "问夏商周断代工程"],
     "atomic", "",
     "大禹治水=改堵为疏导（父鲧堵九年败）：疏通河道引洪入海·十三年三过家门不入；禹→启建夏（第一个王朝·家天下）。"),
    ("kp_card_penalty",
     "足球点球规则",
     "人文通识知识点内容（人话接口）", "体育学",
     "足球点球（12 码球）：罚球点距球门线 12 码（约 11 米），只有守门员与主罚"
     "队员，其他球员须在罚球区（禁区）外、距球至少 9.15 米；哨响前守门员须站在"
     "球门线上，主罚队员向前踢且不得二次触球。两种场景：①比赛中防守方在本方禁"
     "区内犯规（手球/拉拽等直接任意球犯规）判给对方点球；②淘汰赛平局后的点球"
     "大战——双方各罚五轮比进球数，再平进入骤死轮。球门高 2.44 米、宽 7.32 米。"
     "黄牌警告与红牌罚下：一场两黄变一红。",
     ["点球距离球门多少米", "点球大战规则", "什么情况下判点球",
      "守门员在点球时的规定", "足球场球门多大", "红黄牌规则"],
     ["问越位规则细节", "问VAR裁判技术"],
     "atomic", "",
     "点球=12码(约11米)：禁区内犯规判点/淘汰赛五轮点球大战+骤死；守门员须站门线；球门2.44×7.32米；两黄变红。"),
]

QUESTIONS = [
    ("QB-261", "太阳系在银河系的什么位置", "天文学", "技术直答",
     ["猎户臂", "2.6万光年"], "通识拓展32"),
    ("QB-262", "暖气片为什么装在房间下方", "生活常识", "技术直答",
     ["热对流", "热空气上升"], "通识拓展32"),
    ("QB-263", "大禹治水用的什么方法", "历史", "技术直答",
     ["疏导"], "通识拓展32"),
    ("QB-264", "点球距离球门多少米", "体育学", "技术直答",
     ["12码", "11米"], "通识拓展32"),
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
                               "level:L2", "status:verified", "batch:通识拓展32"],
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
    bank["version"] = "v1.24"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
