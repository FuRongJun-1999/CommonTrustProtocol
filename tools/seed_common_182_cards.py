# -*- coding: utf-8 -*-
"""seed_common_182_cards.py · 通识拓展批次182知识卡+题库（幂等·两卡精批次）

182：工程常识-火车轨道下的石子（道砟）/生活常识-挑柚子的技巧
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_ballast",
     "火车轨道下为什么要铺石子",
     "人文通识知识点内容（人话接口）", "工程常识",
     "铁轨下的碎石层叫「**道砟**」（多为花岗岩等硬质碎石），五大功能：①**分"
     "散荷载**——把列车的巨大压力均匀扩散到路基（几十吨的车轴压强惊人）；"
     "②**排水**——碎石间隙让雨水快速流走，防止路基泡软下沉；③**缓冲减振**"
     "——碎石间的摩擦消耗振动能量（列车经过的「哐当」声一部分就来自此）；④"
     "**方便调校**——轨道热胀冷缩或沉降时，抬轨垫入道砟即可调整（碎石可流动"
     "填充）；⑤抑制杂草生长。**高铁为什么没有石子**——高铁多用「无砟轨道」："
     "混凝土整体道床替代碎石，轨道位置精准稳定（时速 300km+ 要求毫米级平顺"
     "度），少维护但造价高；中国高铁绝大多数为无砟，普通铁路仍以有砟为主。",
     ["火车轨道下为什么铺石子", "道砟是什么", "高铁轨道为什么没有石子",
      "无砟轨道", "铁路道床"],
     ["问高铁技术（用高铁卡）", "问桥梁工程"],
     "atomic", "",
     "道砟=铁轨下碎石层：分散列车荷载到路基+排水防沉+缓冲减振+方便抬轨调校+抑草；高铁无砟轨道=混凝土整体道床毫米级平顺少维护造价高——有砟无砟各有分工。"),
    ("kp_card_pickpomelo",
     "挑柚子的技巧",
     "生活常识知识点内容（人话接口）", "生活常识",
     "挑柚子四看一掂：①**看形状**——**上尖下宽的不倒翁形**为佳（发育充分的"
     "标志），圆滚滚或长条的多皮厚水分少；②**掂重量**——同样大小选**重的**"
     "（水分足、果肉饱满，轻飘飘的多已失水「糠」了）；③**看表皮**——光滑细"
     "腻、毛孔（油胞）细密的皮薄肉厚；毛孔粗大粗糙的多皮厚；④**按一按**——"
     "按压硬实有弹性=果肉紧实；软塌塌的多已失水或过熟；⑤**闻香气**——熟透"
     "的柚子有清香。储存：柚子皮厚耐放，阴凉处可存数月（「柚子越放越甜」——"
     "采后淀粉转糖的后熟过程，放一周左右风味最佳）；剥开后的柚子肉密封冷藏并"
     "尽快吃完。挑柚子与挑西瓜思路相通：**掂重听声看细节**。",
     ["怎么挑柚子", "柚子沉的好还是轻的好", "柚子越放越甜吗",
      "柚子皮厚好还是薄好", "挑柚子的方法"],
     ["问挑西瓜（用挑西瓜卡）", "问柚子蜂蜜茶做法"],
     "atomic", "",
     "挑柚子=上尖下宽不倒翁形+同大小掂重的水分足+表皮光滑毛孔细皮薄+按压硬实有弹性+清香熟透；皮厚耐放阴凉存数月越放越甜（后熟转糖）——与挑西瓜同思路：掂重看细节。"),
]

QUESTIONS = [
    ("QB-792", "火车轨道下面为什么要铺碎石（道砟）？高铁轨道为什么反而没有石子？", "工程常识", "技术直答",
     ["道砟", "分散荷载", "排水", "减振", "无砟", "混凝土"], "通识拓展182"),
    ("QB-793", "怎么挑到皮薄肉厚的柚子？同样大小的柚子选轻的还是重的？", "生活常识", "技术直答",
     ["不倒翁", "上尖下宽", "重", "水分", "毛孔细"], "通识拓展182"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    whitelist = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
                 "effect", "Additives"}
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{6,}", content):
            if word not in whitelist:
                problems.append((node[0], f"长英文词: {word}"))
    if problems:
        raise SystemExit(f"外文长词检测报警: {problems}")


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
                               "level:L2", "status:verified", "batch:通识拓展182"],
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
    bank["version"] = "v4.55"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
