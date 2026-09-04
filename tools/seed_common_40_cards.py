# -*- coding: utf-8 -*-
"""seed_common_40_cards.py · 通识拓展批次40知识卡+题库（幂等）

40：化学-二氧化碳检验/地理学-中国邻国/生物学-蜗牛与软体动物/数学-正方形面积
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_co2test",
     "二氧化碳的检验与性质",
     "基础科学知识点内容（人话接口）", "化学",
     "检验二氧化碳的标准方法：通入澄清石灰水——石灰水变浑浊即含 CO₂（CO₂ 与"
     "氢氧化钙反应生成不溶于水的碳酸钙沉淀：CO₂+Ca(OH)₂→CaCO₃↓+H₂O）；继续通"
     "入过量，浑浊又会变澄清（碳酸钙变成可溶的碳酸氢钙）——溶洞/石钟乳的形成与"
     "此相关。CO₂ 性质：无色无味、密度比空气大（可像倒水一样倾倒）、不燃烧不支"
     "持燃烧→可用于灭火；固态 CO₂=干冰（升华吸热，用于人工降雨/舞台烟雾）。与"
     "水反应生成碳酸（紫色石蕊变红）。手工检法（粗略）：使燃着的木条熄灭——但"
     "氮气也能，不严谨。",
     ["怎么检验二氧化碳", "二氧化碳能使澄清石灰水变浑浊吗", "干冰是什么",
      "二氧化碳可以灭火吗", "石钟乳是怎么形成的", "二氧化碳和水反应生成什么"],
     ["问碳酸钙工业用途", "问温室效应数据"],
     "atomic", "",
     "CO₂ 检验=澄清石灰水变浑浊(CaCO₃↓)；过量又变澄清(碳酸氢钙·溶洞成因)；性质=密度大于空气/不燃不助燃→灭火；干冰=固态CO₂。"),
    ("kp_card_neighbors",
     "中国的疆域与邻国",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国陆地邻国共 14 个（世界上陆地邻国最多的国家之一，与俄罗斯并列）：朝鲜"
     "（东北）、俄罗斯、蒙古（北）、哈萨克斯坦、吉尔吉斯斯坦、塔吉克斯坦（西"
     "北）、阿富汗、巴基斯坦（西）、印度、尼泊尔、不丹（西南）、缅甸、老挝、越"
     "南（南）。隔海相望的国家 6 个：韩国、日本、菲律宾、马来西亚、文莱、印度尼"
     "西亚。疆域四至：最北漠河以北黑龙江主航道、最南南沙群岛曾母暗沙（约 5500 "
     "公里）、最西帕米尔高原、最东黑龙江与乌苏里江主航道汇合处；陆地面积约 960 "
     "万平方公里（世界第三），大陆海岸线约 1.8 万公里。",
     ["中国陆地邻国有几个", "与中国隔海相望的国家有哪些", "中国陆地面积世界第几",
      "曾母暗沙在哪里", "中国的最西端是哪里", "与中国接壤的14个国家"],
     ["问省级行政区数量", "问海岸线岛屿分布"],
     "atomic", "",
     "陆上邻国 14 个(俄蒙朝哈吉塔阿巴印尼不缅老越)；隔海相望 6 国(日韩菲马文印尼)；面积约 960 万km²世界第三；四至=漠河/曾母暗沙/帕米尔/两江汇合。"),
    ("kp_card_snail",
     "蜗牛与软体动物",
     "基础科学知识点内容（人话接口）", "生物学",
     "蜗牛属于软体动物门腹足纲——身体柔软分头、足、内脏团三部分，背部有个螺旋"
     "形贝壳（遇到危险/干旱时缩进去，分泌黏液封住壳口）。同门成员：河蚌/牡蛎（双"
     "壳纲，两片贝壳）、章鱼/乌贼/鱿鱼（头足纲——贝壳退化成内壳或消失，是软体动"
     "物中的「智能担当」，有 Cambrian 以来最发达的无脊椎动物眼睛）。蜗牛的腹足"
     "靠肌肉波浪收缩爬行+分泌黏液减阻（干后成银线）。运动最慢的生物之一（约 1 "
     "米/小时）。注意：蜗牛喜欢潮湿但会危害农作物（吃嫩叶），是农业害虫也是养殖"
     "食材（法国大蜗牛）。",
     ["蜗牛属于什么动物", "章鱼是软体动物吗", "蜗牛的壳有什么用",
      "软体动物有哪些", "蜗牛怎么爬行的", "乌贼和鱿鱼的区别"],
     ["问贝类珍珠成因", "问头足类智力研究"],
     "atomic", "",
     "蜗牛=软体动物门腹足纲(螺旋壳+腹足黏液爬行)；同门=河蚌(双壳)/章鱼乌贼(头足·贝壳退化·无脊椎智力之王)。"),
    ("kp_card_squaresq",
     "正方形与长方形的面积",
     "基础科学知识点内容（人话接口）", "数学",
     "正方形面积 = 边长 × 边长 = a²（四条边相等、四个角都是直角）；正方形周长 = "
     "边长 × 4。长方形面积 = 长 × 宽；周长 = (长+宽) × 2。例：边长 6 厘米的正方"
     "形面积 36 平方厘米、周长 24 厘米。单位换算陷阱：1 平方米 = 100 平方分米 = "
     "10000 平方厘米（面积单位进率是长度进率的平方）。联系：正方形是特殊的矩形"
     "（长=宽），也是特殊的菱形（四边相等）；把长方形剪拼可推出平行四边形、三角"
     "形面积公式的来源。",
     ["正方形的面积怎么算", "正方形的周长公式", "边长5厘米的正方形面积是多少",
      "长方形面积公式", "平方米和平方厘米怎么换算", "正方形是特殊的长方形吗"],
     ["问梯形面积推导", "问根号与已知面积求边长"],
     "atomic", "",
     "正方形 S=a²、C=4a；长方形 S=ab、C=2(a+b)；面积单位进率=长度进率平方(1m²=10000cm²)；正方形⊂矩形⊂平行四边形。"),
]

QUESTIONS = [
    ("QB-293", "怎么检验二氧化碳", "化学", "技术直答",
     ["澄清石灰水", "变浑浊"], "通识拓展40"),
    ("QB-294", "中国陆地邻国有几个", "地理学", "技术直答",
     ["14", "十四"], "通识拓展40"),
    ("QB-295", "蜗牛属于什么动物", "生物学", "技术直答",
     ["软体动物"], "通识拓展40"),
    ("QB-296", "正方形的面积怎么算", "数学", "技术直答",
     ["边长", "平方"], "通识拓展40"),
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
                               "level:L2", "status:verified", "batch:通识拓展40"],
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
    bank["version"] = "v1.32"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
