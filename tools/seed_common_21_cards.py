# -*- coding: utf-8 -*-
"""seed_common_21_cards.py · 通识拓展批次21知识卡+题库（幂等）

21：物理学-影子的形成/历史-长城/生活常识-垃圾分类/数学-圆周率与祖冲之
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_shadow",
     "影子的形成与光的直线传播",
     "基础科学知识点内容（人话接口）", "物理学",
     "影子是光沿直线传播的直接证据：光在同种均匀介质中沿直线传播，遇到不透明"
     "物体被挡住，物体背面光线照不到的暗区就形成影子。改变光源位置影子会移动"
     "——早晨傍晚影子长，正午影子短。同类现象：日食（月亮挡住太阳光投在地球"
     "上的影子）、月食（地球影子罩住月亮）、小孔成像（倒立的实像）、激光准直。"
     "皮影戏就是用影子的原理表演的艺术。",
     ["影子是怎么形成的", "为什么正午影子最短", "小孔成像的原理",
      "日食月食和影子有什么关系", "光沿直线传播的例子", "皮影戏的原理"],
     ["问光的反射折射", "问光的波粒二象性"],
     "atomic", "",
     "影子=光沿直线传播被不透明物体挡住的暗区；同类=日食/月食/小孔成像；正午影短晨昏影长。"),
    ("kp_card_greatwall",
     "长城的修建历史",
     "人文通识知识点内容（人话接口）", "历史",
     "长城不是一次建成的：最早可追溯西周（烽火台，「烽火戏诸侯」）；秦始皇统"
     "一后连接并扩建各诸侯国城墙形成「秦长城」；今天看到的长城主要是明代修建"
     "的「明长城」——东起河北山海关（一说辽东虎山），西至甘肃嘉峪关，全长约"
     "8850 公里，若含各代长城总长超过两万公里。长城 1987 年入选世界文化遗产，"
     "八达岭、慕田峪是著名的开放游览段。修建目的：防御北方游牧政权南下。",
     ["现存长城主要是哪个朝代修建的", "明长城东起哪里西至哪里", "长城有多长",
      "秦始皇修的长城和现在的长城一样吗", "长城是什么时候入选世界遗产的",
      "烽火戏诸侯和长城的关系"],
     ["问长城军事防御体系细节", "问其他古建筑"],
     "atomic", "",
     "长城三代：西周烽火→秦连接→现存主体=明长城(山海关→嘉峪关·约8850km)；1987世界遗产；用途=防御北方。"),
    ("kp_card_garbage",
     "生活垃圾分类",
     "生活常识知识点内容（人话接口）", "生活常识",
     "生活垃圾分四大类：①可回收物（蓝色桶）——废纸/塑料瓶/易拉罐/玻璃瓶/旧衣"
     "服，能再利用；②厨余垃圾（绿色桶）——剩饭剩菜/果皮菜叶/茶渣，可堆肥发电"
     "；③有害垃圾（红色桶）——废电池/过期药品/灯管/油漆，需特殊安全处理；④其"
     "他垃圾（灰色桶）——污损纸巾/陶瓷碎片/烟头等。分类的意义：资源回收利用+减"
     "少填埋焚烧污染+有害物单独处置防污染。大棒骨因难降解归「其他垃圾」而非厨"
     "余，是易错点。",
     ["剩饭剩菜属于什么垃圾", "垃圾分类有哪四大类", "废电池属于什么垃圾",
      "塑料瓶是什么垃圾", "大棒骨是厨余垃圾吗", "垃圾分类有什么意义"],
     ["问各地分类标准差异", "问垃圾处理工艺"],
     "atomic", "",
     "四分类：可回收(蓝·纸塑金属玻璃)/厨余(绿·剩菜果皮)/有害(红·电池药品灯管)/其他(灰·污损纸巾)；大棒骨=其他垃圾。"),
    ("kp_card_pi",
     "圆周率与祖冲之",
     "基础科学知识点内容（人话接口）", "数学",
     "圆周率 π 是圆的周长与直径之比，约等于 3.14159，是无理数（无限不循环小"
     "数）。中国南北朝数学家祖冲之（429-500）把 π 精确到 3.1415926 与 "
     "3.1415927 之间——小数点后 7 位，这一纪录保持世界领先近千年；他还给出密"
     "率 355/113 的近似分数。古希腊阿基米德更早用圆内接外切正多边形逼近法算得"
     "两位小数精度。现代计算机已把 π 算到百万亿位以上，但精确值永远算不完——"
     "这正是无理数的本性。",
     ["我国古代哪位数学家把圆周率精确到小数点后七位", "圆周率是谁算的",
      "圆周率是多少", "什么是密率", "圆周率是无理数吗", "祖冲之的贡献"],
     ["问圆面积公式推导", "问无理数证明细节"],
     "atomic", "",
     "π=周长÷直径≈3.14159(无理数)；祖冲之(南北朝)精确到小数7位领先千年+密率355/113；阿基米德=正多边形逼近。"),
]

QUESTIONS = [
    ("QB-217", "影子是怎么形成的", "物理学", "技术直答",
     ["光沿直线传播"], "通识拓展21"),
    ("QB-218", "现存长城主要是哪个朝代修建的", "历史", "技术直答",
     ["明代"], "通识拓展21"),
    ("QB-219", "剩饭剩菜属于什么垃圾", "生活常识", "技术直答",
     ["厨余垃圾"], "通识拓展21"),
    ("QB-220", "我国古代哪位数学家把圆周率精确到小数点后七位", "数学", "技术直答",
     ["祖冲之"], "通识拓展21"),
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
                               "level:L2", "status:verified", "batch:通识拓展21"],
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
    bank["version"] = "v1.13"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
