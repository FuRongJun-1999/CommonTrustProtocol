# -*- coding: utf-8 -*-
"""seed_common_136_cards.py · 通识拓展批次136知识卡+题库（幂等）

136：生活常识-驾驶证记分与酒驾红线/生活常识-护照与签证/地理学-世界海峡与运河
KCCS 四要素+题干原句触发词。三重预检：三主题既有卡均「仅提及」非主题覆盖。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_drivingscore",
     "驾驶证记分与酒驾红线",
     "生活常识知识点内容（人话接口）", "生活常识",
     "驾驶证记分制度：记分周期为**初次领证日期起 12 个月**，满分 **12 分**，周"
     "期内累加。常见记分：闯红灯记 6 分、高速倒车/逆行/占用应急车道记 12 分或"
     "9 分、不系安全带/接打手机记分罚款。**记满 12 分**：扣留驾驶证，须参加满"
     "分学习（道路交通安全法规）并重考科目一，合格后记分清除。**酒驾红线**："
     "饮酒驾驶（血液酒精 20-80mg/100ml）=记 12 分+暂扣驾照 6 个月+罚款；再次"
     "饮酒驾驶=拘留+吊销；**醉酒驾驶**（≥80mg/100ml）=吊销驾照+5 年内不得重"
     "考+构成危险驾驶罪追究刑事责任（「开车不喝酒，喝酒不开车」）。C1 实习期"
     "12 个月，实习期记满 12 分注销驾驶资格。",
     ["驾驶证记分周期是多久", "记满12分怎么办", "酒驾怎么处罚",
      "醉驾是什么罪", "闯红灯记几分", "实习期是多久"],
     ["问驾考科目技巧", "问具体事故责任认定"],
     "atomic", "",
     "记分周期=初次领证起 12 个月满分 12 分（闯红灯 6 分/高速逆行倒车 12 分）；记满 12 分=扣证+满分学习+重考科目一；酒驾(20-80mg)=记12分暂扣6月，醉驾(≥80mg)=吊销+5年禁考+危险驾驶罪刑责；实习期 12 个月记满分即注销。"),
    ("kp_card_passportvisa",
     "护照与签证的区别",
     "生活常识知识点内容（人话接口）", "生活常识",
     "护照=**国籍与身份证明**：证明持有人国籍和身份，供出入境和在国外使用，由"
     "本国政府签发（中国由公安部出入境管理机构签发），普通护照有效期成人 **10"
     " 年**、未满 16 周岁 **5 年**——「没有护照出不了国门」。签证=**目的地国"
     "的入境许可**：由前往国签发（贴在护照页上的贴纸签/电子签/落地签），表示"
     "该国允许你入境并注明停留期，常见类型旅游/商务/学生/工作签证。即：护照问"
     "「你是谁、哪国人」，签证问「对方国家让你来吗、待多久」。出行检查链：值"
     "机（机票）→**边防检查**（护照+签证/登机牌）→安检（人身行李）。注意：去"
     "港澳用港澳通行证、台湾用台湾通行证——**不走护照**；对免签国家（如对中"
     "国单方面免签的部分国家）无需签证但护照+往返机票仍必备。",
     ["护照和签证有什么区别", "护照有效期多少年", "签证是谁签发的",
      "免签落地签电子签", "去港澳需要护照吗", "边防检查查什么"],
     ["问具体国家签证材料清单", "问移民定居政策"],
     "atomic", "",
     "护照=本国签发的国籍身份证明（成人 10 年/未成年 5 年）；签证=前往国签发的入境许可（贴纸/电子/落地签，注明停留期）；护照答「你是谁」签证答「放你进来」；出入境流程值机→边检（护照+签证）→安检；港澳台用通行证不走护照。"),
    ("kp_card_straitscanals",
     "世界著名海峡与运河",
     "人文通识知识点内容（人话接口）", "地理学",
     "海峡=两块陆地之间的狭窄水道（天然），运河=人工开挖的水上通道——都常是"
     "航运咽喉。**两大运河**：①**苏伊士运河**（埃及）——连通**地中海与红"
     "海**，亚欧航路捷径，免绕非洲好望角 5500-8000 公里；②**巴拿马运河**——"
     "连通**太平洋与大西洋**（加勒比海），免绕南美合恩角。**著名海峡**：③**马"
     "六甲海峡**——马来半岛与苏门答腊岛之间，连通太平洋与印度洋的咽喉，中国"
     "约八成进口石油经此（「海上生命线」）；④直布罗陀海峡——地中海西出口（西"
     "班牙-摩洛哥间）；⑤英吉利海峡——英国与法国之间，世界最繁忙航道之一；⑥"
     "霍尔木兹海峡——波斯湾唯一出口，全球石油运输动脉（「油库阀门」）；⑦白令"
     "海峡——亚洲与北美洲分界（俄美之间，宽约 86 公里）。",
     ["苏伊士运河连接哪两个海", "巴拿马运河沟通哪两个大洋",
      "马六甲海峡为什么重要", "中国的海上生命线", "霍尔木兹海峡在哪",
      "亚洲和北美洲的分界线"],
     ["问运河修建历史", "问具体航线运费"],
     "atomic", "",
     "苏伊士运河（埃及）连地中海-红海免绕好望角；巴拿马运河连太平洋-大西洋免绕合恩角；马六甲海峡=太平洋-印度洋咽喉+中国八成进口石油海上生命线；直布罗陀=地中海出口；霍尔木兹=波斯湾石油阀门；白令海峡=亚北美分界。"),
]

QUESTIONS = [
    ("QB-673", "驾驶证的记分周期是多长时间？一个周期内最多记多少分？", "生活常识", "技术直答",
     ["12个月", "一年", "12分", "十二分"], "通识拓展136"),
    ("QB-674", "护照和签证有什么区别？分别由谁签发？", "生活常识", "技术直答",
     ["国籍", "身份", "入境许可", "本国", "前往国", "目的地国"], "通识拓展136"),
    ("QB-675", "苏伊士运河连接哪两个海？它使船只避免了绕行非洲的哪个角落？", "地理学", "技术直答",
     ["地中海", "红海", "好望角"], "通识拓展136"),
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
                               "level:L2", "status:verified", "batch:通识拓展136"],
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
    bank["version"] = "v4.9"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
