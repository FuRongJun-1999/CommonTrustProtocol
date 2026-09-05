# -*- coding: utf-8 -*-
"""seed_common_120_cards.py · 通识拓展批次120知识卡+题库（幂等）

120：地理学-二十四节气的地域适用性/生活常识-未成年人游戏防沉迷/生物学-常见的遗传病
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_solartermreg",
     "二十四节气的地域适用性",
     "人文通识知识点内容（人话接口）", "地理学",
     "二十四节气起源于**黄河流域**（中原地区），最 accurately 反映的是这一带的"
     "气候与农事规律。地域适用性差异：①黄河流域（华北/关中）——最贴合：惊蛰春"
     "雷、芒种麦收、霜降见霜；②南方——节气总体偏晚：如「清明前后种瓜点豆」在岭"
     "南可提前一个节气，东北则要推迟；③东北/西北——明显偏差：东北立冬时秋收尚"
     "未结束，节气描述的物候与当地实际差一到两个月；④青藏高原——几乎不适用（高"
     "寒气候自成体系）。现代应对：农事指导更多参考当地农业气象预报而非死守节气"
     "；节气文化价值（节气美食/养生/诗词）超越地域仍具生命力。2016 年入选联合国"
     "非遗。",
     ["二十四节气起源于哪里", "二十四节气适合所有地区吗", "节气在南方准吗",
      "东北种地按节气吗", "二十四节气申遗成功是哪年", "芒种是什么意思"],
     ["问节气与农谚地域版", "问节气养生地域差异"],
     "atomic", "",
     "节气起源=黄河流域中原：华北最贴切/南方偏晚/东北差 1-2 个月/青藏不适用；现代参考当地气象预报为主；2016 入选非遗；文化价值超地域。"),
    ("kp_card_antiction",
     "未成年人游戏防沉迷",
     "生活常识知识点内容（人话接口）", "生活常识",
     "未成年人游戏防沉迷规定（2021 年「最严防沉迷新规」）：网络游戏企业仅可在"
     "**周五、周六、周日和法定节假日的 20-21 时**向未成年人提供 1 小时服务——其"
     "他时间一律不得提供。实名验证：游戏须实名注册（接入公安实名校验），未成年"
     "人冒用成人身份被人脸识别识别后触发人脸验证。充值限制：8 岁以下不能充值、"
     "8-16 岁单次≤50 元月≤200 元、16-18 岁单次≤100 元月≤400 元。目的：保护视"
     "力（近视防控国家战略）、防止沉迷影响学业与身心健康。家长工具：家长监护平"
     "台可绑定孩子账号查询/限制游戏时长与充值。",
     ["未成年人游戏防沉迷规定", "未成年人每周能玩多久游戏", "未成年人游戏充值限制",
      "防沉迷实名认证", "为什么要防沉迷", "家长监护平台是什么"],
     ["问近视防控国家战略", "问游戏成瘾WHO认定"],
     "atomic", "",
     "防沉迷 2021 新规=仅周五六日+法定节假日 20-21 时 1 小时；充值限制 8-16 岁单次 50 月 200/16-18 岁单次 100 月 400；实名+人脸验证防冒用；目的=护眼护学业。"),
    ("kp_card_gendisease",
     "常见的遗传病",
     "基础科学知识点内容（人话接口）", "生物学",
     "遗传病：由遗传物质改变引起的疾病，可从亲代传给子代。常见类型与病例：①**"
     "单基因遗传病**——红绿色盲（X 染色体隐性，男性发病率远高于女性约 7:1）、血"
     "友病（X 隐性，凝血功能障碍）、白化病（常染色体隐性，皮肤毛发缺乏色素）、"
     "苯丙酮尿症；②**多基因遗传病**——原发性高血压、冠心病、哮喘、糖尿病（遗传"
     "+环境共同作用）；③**染色体异常遗传病**——唐氏综合征（21 三体，第 21 号染"
     "色体多一条）。预防：禁止近亲结婚（三代以内旁系血亲——近亲结婚后代隐性遗传"
     "病发病率大增）、婚前检查、产前诊断（羊水穿刺/无创 DNA 筛查）。咨询：有家"
     "族史者备孕前做遗传咨询。",
     ["常见的遗传病有哪些", "色盲是遗传病吗", "为什么禁止近亲结婚",
      "唐氏综合征是什么", "遗传病能治疗吗", "什么是隐性遗传病"],
     ["问产前诊断技术", "问基因治疗进展"],
     "atomic", "",
     "遗传病三类=单基因(色盲 X 隐·男 7 倍/血友病/白化病)+多基因(高血压糖尿病)+染色体异常(唐氏 21 三体)；预防=禁近亲结婚+婚检+产前诊断；近亲婚隐性病大增。"),
]

QUESTIONS = [
    ("QB-614", "二十四节气起源于哪里", "地理学", "技术直答",
     ["黄河流域"], "通识拓展120"),
    ("QB-615", "未成年人游戏防沉迷规定", "生活常识", "技术直答",
     ["周五周六周日", "1小时"], "通识拓展120"),
    ("QB-616", "常见的遗传病有哪些", "生物学", "技术直答",
     ["色盲", "血友病", "唐氏综合征"], "通识拓展120"),
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
                               "level:L2", "status:verified", "batch:通识拓展120"],
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
    bank["version"] = "v3.4"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
