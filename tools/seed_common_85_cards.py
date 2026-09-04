# -*- coding: utf-8 -*-
"""seed_common_85_cards.py · 通识拓展批次85知识卡+题库（幂等）

85：物理学-力的作用效果/化学-吸热与放热反应/生物学-遗传育种/地理学-南北方差异
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_forceeff",
     "力的作用效果与三要素",
     "基础科学知识点内容（人话接口）", "物理学",
     "力是物体对物体的作用，产生两个效果：①改变物体的**运动状态**（由静到动/由"
     "动到静/变速/转向——足球被踢飞、守门员接住球）；②改变物体的**形状**（捏橡"
     "皮泥、拉弓、压弹簧）。力的三要素（影响力作用效果）：大小、方向、**作用点**"
     "——推门时推门轴附近很费力、推门边轻松（作用点不同的证据）。力的单位牛顿"
     "（N）——托起两个鸡蛋的力约 1N。力的作用是**相互的**：划船桨推水、水也推"
     "船；拍桌子手也疼；火箭向后喷气获得向前的推力。力的示意图：用带箭头的线段"
     "表示（起点=作用点、箭头=方向、长度≈大小）。",
     ["力的作用效果有哪些", "力的三要素", "为什么说力的作用是相互的",
      "力的单位是什么", "划船时船为什么前进", "力的示意图怎么画"],
     ["问力的示意图规范", "问二力平衡"],
     "atomic", "",
     "力两效果=改变运动状态+改变形状；三要素=大小/方向/作用点(推门轴费力为例)；单位牛顿(托两鸡蛋≈1N)；力的作用相互(桨推水水推船·火箭喷气)；示意图=箭头线段。"),
    ("kp_card_exotherm",
     "放热反应与吸热反应",
     "基础科学知识点内容（人话接口）", "化学",
     "化学反应伴随能量变化，常表现为热量：**放热反应**——燃烧（木炭/氢气/天然"
     "气）、中和反应（酸+碱）、生石灰与水（自热米饭加热包）、活泼金属与酸、缓慢"
     "氧化（呼吸/生锈）——「燃烧储热」。**吸热反应**——碳与二氧化碳高温反应（C"
     "+CO₂→2CO）、碳与水蒸气反应、大多数分解反应（高锰酸钾加热分解）、氢氧化钡"
     "晶体与氯化铵晶体搅拌（烧杯壁结冰的经典演示）——需要持续加热才能维持。辨析"
     "：需要点燃的（燃烧）是放热反应——点燃只是「启动钥匙」不是「持续供能」；"
     "放热一旦启动自发进行。能量守恒视角：化学能转化为热能（放热）或热能转化为"
     "化学能（吸热储存）。生活：暖宝宝（铁缓慢氧化放热）、冷敷包（吸热反应）。",
     ["哪些化学反应放热", "哪些化学反应吸热", "碳和二氧化碳反应是吸热吗",
      "点燃是放热还是吸热", "暖宝宝的原理", "自热米饭为什么能加热"],
     ["问反应热与键能", "问生石灰原理"],
     "atomic", "",
     "放热=燃烧/中和/生石灰遇水(自热饭)/缓慢氧化(暖宝宝)；吸热=C+CO₂ 高温/多数分解/Ba(OH)₂+NH₄Cl 结冰演示；点燃只是启动钥匙——燃烧本身放热自发。"),
    ("kp_card_breeding",
     "遗传育种：杂交水稻的故事",
     "基础科学知识点内容（人话接口）", "生物学",
     "育种利用遗传变异原理培育优良品种：①**杂交育种**——基因重组：袁隆平杂交水"
     "稻（利用野生稻雄性不育株与栽培稻杂交，1973 年三系配套成功，增产 20%+，"
     "「杂交水稻之父」解决亿人吃饭问题）；②诱变育种——基因突变：太空育种（种子"
     "上太空宇宙射线诱变，返回后筛选）、辐射育种；③**选择育种**——长期人工挑选"
     "优良个体（古已有之）；④转基因育种（转入外源基因——抗虫棉）；⑤单倍体/多倍"
     "体育种（三倍体无籽西瓜）。袁隆平的两个梦：「禾下乘凉梦」（超高产）与「杂交"
     "水稻覆盖全球梦」。2021 年袁老逝世，长沙十里长街送别。育种的遗传学原理：基"
     "因重组（杂交）、基因突变（诱变）、染色体变异（多倍体）。",
     ["杂交育种利用什么原理", "袁隆平的贡献", "太空育种是什么原理",
      "三系配套是什么", "无籽西瓜怎么来的", "诱变育种的原理"],
     ["问孟德尔定律衔接", "问种业安全"],
     "atomic", "",
     "育种原理：杂交=基因重组(袁隆平杂交水稻 1973 三系配套·增 20%+)/诱变=基因突变(太空种子)/多倍体(无籽西瓜)/转基因；袁老两梦=禾下乘凉+覆盖全球。"),
    ("kp_card_southnorth",
     "南北方差异：秦岭淮河线",
     "人文通识知识点内容（人话接口）", "地理学",
     "秦岭—淮河一线是中国最重要的地理分界线，南北差异全面对比：①气温——1 月 "
     "0℃ 等温线（北冬河冻/南冬不冻）；②降水——800 毫米等降水量线；③温度带——"
     "暖温带与亚热带分界；④干湿区——半湿润与湿润区分界；⑤气候——温带季风与亚"
     "热带季风气候；⑥农业——旱地小麦杂粮 vs 水田水稻（「北麦南稻」）、水果苹果"
     "桃梨 vs 柑橘香蕉、作物熟制两年三熟 vs 一年两熟到三熟；⑦河流——结冰 vs 不"
     "结冰、流量小 vs 大；⑧植被——温带落叶阔叶林 vs 亚热带常绿阔叶林；⑨民居交"
     "通——平顶屋 vs 尖顶屋（排水）、陆运为主 vs 水运发达（「南船北马」）；⑩饮食"
     "——面食 vs 米饭。一线贯穿十多个省，是中国自然与人文差异的浓缩线。",
     ["南方和北方的分界线", "秦岭淮河一线的意义", "南稻北麦的原因",
      "南北方的气候差异", "秦岭淮河是几月等温线", "南船北马什么意思"],
     ["问秦岭生态屏障", "问南北饮食文化"],
     "atomic", "",
     "秦岭淮河线=1 月 0℃/800mm/暖温亚热界/湿润半湿润界：北旱麦平顶结冰 vs 南水田稻尖顶行船——气候农业植被民居交通饮食全面分异；「南船北马」。"),
]

QUESTIONS = [
    ("QB-473", "力的作用效果有哪些", "物理学", "技术直答",
     ["运动状态", "形状"], "通识拓展85"),
    ("QB-474", "哪些化学反应吸热", "化学", "技术直答",
     ["碳还原二氧化碳", "分解反应"], "通识拓展85"),
    ("QB-475", "杂交育种利用什么原理", "生物学", "技术直答",
     ["基因重组"], "通识拓展85"),
    ("QB-476", "南方和北方的分界线", "地理学", "技术直答",
     ["秦岭淮河"], "通识拓展85"),
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
                               "level:L2", "status:verified", "batch:通识拓展85"],
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
    bank["version"] = "v1.77"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
