# -*- coding: utf-8 -*-
"""seed_common_38_cards.py · 通识拓展批次38知识卡+题库（幂等）

38：化学-天然气主要成分/地理学-世界最高峰/生物学-植物根的作用/体育学-奥运五环
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_methane",
     "天然气与甲烷",
     "基础科学知识点内容（人话接口）", "化学",
     "天然气的主要成分是甲烷（CH₄）——最简单的有机物，无色无味的气体（家用天"
     "然气的臭味是人为加的警示剂四氢噻吩，方便漏气时察觉）。甲烷是清洁能源：燃"
     "烧产物只有二氧化碳和水，比煤和石油污染小。甲烷也是温室气体——其温室效应"
     "强度约为二氧化碳的 25-30 倍（百年尺度），沼气/垃圾填埋气/冻土释放的甲烷都"
     "是减排关注点。可燃冰（天然气水合物）=甲烷被水分子包裹的冰状晶体，主要存"
     "在于深海沉积物与永久冻土中，1 立方米可燃冰可释放约 160 立方米天然气。",
     ["天然气的主要成分是什么", "甲烷是什么", "天然气为什么有臭味",
      "可燃冰是什么", "甲烷是温室气体吗", "沼气的主要成分"],
     ["问有机物系统命名", "问水合物开采难点"],
     "atomic", "",
     "天然气=甲烷CH₄(最简单有机物·无色无味·臭味=人为警示剂)；清洁但为强温室气体(约CO₂ 25-30倍)；可燃冰=甲烷水合物(1m³→160m³气)。"),
    ("kp_card_qomolangma",
     "珠穆朗玛峰与山峰之最",
     "人文通识知识点内容（人话接口）", "地理学",
     "世界最高峰是珠穆朗玛峰：喜马拉雅山脉主峰，位于中国与尼泊尔边界，最新测定"
     "高程 8848.86 米（2020 年中尼联合宣布）——珠峰仍在缓慢长高（印度板块与欧"
     "亚板块持续碰撞挤压，每年约上升数毫米）。山峰之对比：若按山体从底部算，夏"
     "威夷的冒纳凯阿火山从海底算高约 10200 米（但大部分在水下）；「距地心最远」"
     "的山峰是南美洲的钦博拉索山（地球是赤道略鼓的椭球）。珠峰北坡在中国西藏，"
     "北坡登顶难度大于南坡；1960 年中国登山队首次从北坡登顶。",
     ["世界最高峰是哪座", "珠穆朗玛峰有多高", "珠峰为什么还在长高",
      "哪座山从山脚算最高", "距地心最远的山峰", "珠峰北坡是谁登顶的"],
     ["问登山气候窗口", "问板块构造驱动力"],
     "atomic", "",
     "最高峰=珠穆朗玛 8848.86m(2020中尼联测·仍在长高)；从底算最高=冒纳凯阿(水下10200m)；距地心最远=钦博拉索；1960北坡首登。"),
    ("kp_card_roots",
     "植物根的作用",
     "基础科学知识点内容（人话接口）", "生物学",
     "植物的根有三大功能：①固定——把植株锚定在土壤里支撑地上部分；②吸收——"
     "根尖成熟区的根毛大幅增加吸收面积，从土壤吸收水分和溶解在水中的无机盐（矿"
     "质营养）；③输导与储藏——根把水分无机盐向上运给茎叶（配合蒸腾拉力），有"
     "的根还储藏养分（胡萝卜/萝卜/红薯都是变态储藏根）。根的生长特点：向地性"
     "（向下扎）、向水性（向湿润处生长）、向肥性——「根深叶茂」的道理。土壤板"
     "结/积水会伤根（缺氧无法呼吸），所以盆栽要松土、浇水要见干见湿。",
     ["植物的根有什么作用", "根毛长在根的什么部位", "萝卜和红薯是根还是茎",
      "根为什么向下长", "花盆里的土为什么要松", "什么是见干见湿"],
     ["问根瘤菌固氮", "问无土栽培营养液"],
     "atomic", "",
     "根三用=固定+根毛吸水吸无机盐+输导储藏(萝卜红薯=储藏根)；向地/向水/向肥；土壤板结缺氧伤根→松土/见干见湿。"),
    ("kp_card_rings",
     "奥运五环",
     "人文通识知识点内容（人话接口）", "体育学",
     "奥林匹克五环标志由现代奥运会创始人顾拜旦 1913 年设计：五个相互套连的圆"
     "环——颜色自左至右为蓝、黄、黑、绿、红（白底之上），覆盖了当时各国国旗的"
     "全部颜色。五环象征五大洲的团结：传统说法蓝=欧洲、黄=亚洲、黑=非洲、绿="
     "大洋洲、红=美洲（国际奥委会也强调五环本义是「五大洲团结」，颜色与洲的对"
     "应并非严格官方规定）。奥林匹克格言：「更快、更高、更强——更团结」（2021"
     " 年加入「更团结」）。奥运会每四年一届：夏季与冬季奥运会相间举行（间隔 2 "
     "年）；2008 北京夏奥+2022 北京冬奥=北京是首座「双奥之城」。",
     ["奥运五环有几个环什么颜色", "五环的五种颜色代表什么", "奥林匹克格言是什么",
      "奥运几年一届", "双奥之城是哪个城市", "五环是谁设计的"],
     ["问冬奥项目列表", "问马拉松起源"],
     "atomic", "",
     "五环=顾拜旦1913设计：蓝黄黑绿红套连象征五大洲团结；格言=更快更高更强·更团结(2021增)；4年一届夏冬相间；北京=双奥之城。"),
]

QUESTIONS = [
    ("QB-285", "天然气的主要成分是什么", "化学", "技术直答",
     ["甲烷", "CH4"], "通识拓展38"),
    ("QB-286", "世界最高峰是哪座", "地理学", "技术直答",
     ["珠穆朗玛", "8848"], "通识拓展38"),
    ("QB-287", "植物的根有什么作用", "生物学", "技术直答",
     ["固定", "吸收"], "通识拓展38"),
    ("QB-288", "奥运五环有几个环什么颜色", "体育学", "技术直答",
     ["5", "蓝黄黑绿红"], "通识拓展38"),
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
                               "level:L2", "status:verified", "batch:通识拓展38"],
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
    bank["version"] = "v1.30"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
