# -*- coding: utf-8 -*-
"""seed_common_74_cards.py · 通识拓展批次74知识卡+题库（幂等）

74：物理学-托盘天平/生活常识-灭火器种类/生物学-干细胞/地理学-北斗导航
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_balanceuse",
     "托盘天平的使用",
     "基础科学知识点内容（人话接口）", "物理学",
     "托盘天平测质量的步骤：①放——把天平放在**水平台面**上；②调游码归零；③"
     "调平衡——调节平衡螺母使指针指在分度盘中央（左偏右调、右偏左调）；④称量"
     "——**「左物右码」**（物体放左盘、砝码放右盘），用镊子夹取砝码（从大到小"
     "试加）最后移动游码至平衡；⑤读数——物体质量=砝码总质量+游码示数（读游码"
     "**左侧**边缘对应的刻度）。禁忌：不能测超过量程的物体、不能测潮湿/化学药品"
     "（用烧杯垫着称）。颠倒错放（左码右物）时：物体质量=砝码-游码。质量单位："
     "千克（kg）是 SI 基本单位，常用 g/mg/t；质量是物体属性不随位置形状状态改"
     "变（宇航员到月球质量不变、重量变轻）。",
     ["托盘天平的使用步骤", "天平为什么左物右码", "游码怎么读数",
      "砝码不能用什么夹取", "天平左码右物怎么算", "质量和重量的区别"],
     ["问质量属性判断题", "问特殊天平测量法"],
     "atomic", "",
     "天平五步=放水平台/游码归零/调平衡(左偏右调)/左物右码(镊子夹·从大到小)/读数(码+游码左缘)；错放=码-游码；质量=属性不随位置形状变(月球质量不变)。"),
    ("kp_card_extinguisher",
     "灭火器的种类与适用",
     "生活常识知识点内容（人话接口）", "生活常识",
     "常见灭火器与适用火灾：①干粉灭火器（最常见，ABC 类通用——固体/液体/气体"
     "火灾，家用车用首选；粉雾覆盖隔绝氧气，会留粉尘）；②二氧化碳灭火器——适"
     "用于精密仪器/图书档案（不留残迹），注意手握喇叭筒根部防冻伤（喷出干冰温"
     "度极低）；③水基型（水雾）灭火器——可扑灭油类火且能喷在身上逃生（新型家"
     "用友好），但电器带电火先断电；④泡沫灭火器——适用于油类，不能用于电器（导"
     "电）。火灾分类常识：电器火先断电；油锅火盖锅盖（禁水）；汽油火禁水（浮面"
     "扩散）用干粉/泡沫。使用口诀「提、拔、握、压」：提起、拔保险销、握喷管对准"
     "火焰根部、压下压把——对**根部**喷射而非火苗。有效期：压力表指针在绿区才"
     "有效。",
     ["干粉灭火器适用于什么火灾", "灭火器怎么使用提拔握压", "二氧化碳灭火器注意什么",
      "油锅起火用什么灭火器", "灭火器压力表怎么看", "精密仪器火灾用什么灭火器"],
     ["问火灾分类 ABCDEF", "问家用消防器材清单"],
     "atomic", "",
     "灭火器：干粉(ABC 通用·家用首选)/CO₂(精密仪器·握根部防冻伤)/水基(油火+逃生·断电前禁电器)/泡沫(油火禁电)；口诀提拔握压·喷火焰**根部**；压力表绿区有效。"),
    ("kp_card_stemcell",
     "干细胞：再生医学的种子",
     "基础科学知识点内容（人话接口）", "生物学",
     "干细胞是具有**自我更新**和**分化潜能**的「原始细胞」——能不断分裂，也能"
     "分化成各种 specialized 细胞。分类：①全能性递减——胚胎干细胞（全能性最强，"
     "可分化成几乎所有细胞，来自早期胚胎，伦理争议大）；②成体干细胞（骨髓造血"
     "干细胞——移植治白血病；间充质干细胞——骨髓/脂肪中）；③诱导多能干细胞"
     "（iPS 细胞，山中伸弥 2006 年把皮肤细胞「逆转」回干细胞，2012 年诺奖——绕"
     "开胚胎伦理）。应用前景：器官再生/帕金森与糖尿病治疗/药物测试；中国 2021 "
     "年用-induced 干细胞治愈一位帕金森动物模型领先临床研究。造血干细胞移植（骨"
     "髓移植）已成熟——捐献类似献血，加入中华骨髓库是善举。",
     ["干细胞有什么用", "什么是iPS细胞", "骨髓移植捐的是什么",
      "胚胎干细胞的伦理问题", "山中伸弥的贡献", "干细胞能治什么病"],
     ["问克隆技术关联", "问器官打印前沿"],
     "atomic", "",
     "干细胞=自我更新+分化潜能：胚胎干(全能·伦理争议)/成体干(造血干→治白血病)/iPS(山中伸弥 2006 皮肤逆转·2012 诺奖·绕开伦理)；前景=再生医学。"),
    ("kp_card_beidou",
     "北斗卫星导航系统",
     "人文通识知识点内容（人话接口）", "地理学",
     "北斗卫星导航系统（BDS）是中国自主建设的全球卫星导航系统：1994 年立项三步"
     "走（北斗一号区域试验→二号覆盖亚太→三号 2020 年 7 月 31 日正式开通全球服"
     "务），与美国 GPS、俄罗斯 GLONASS、欧盟伽利略并列全球四大导航系统。特色功能"
     "（GPS 没有的）：①**短报文通信**——无信号区域可发短消息求救（渔船/救援"
     "刚需）；②高精度授时（电力/金融系统依赖）；③毫米级增强定位（地基增强，用"
     "于精准农业/桥梁监测/共享单车电子围栏）。星座：30 颗左右混合轨道（GEO+IGSO"
     "+MEO）。日常应用已无处不在：手机导航、共享单车定位、外卖轨迹、地震预警秒"
     "级报文。GPS 是先行者（24 星），北斗独有短报文+混合星座设计。",
     ["中国的全球定位系统叫什么", "北斗和GPS有什么区别", "短报文通信是什么",
      "北斗三号哪一年开通全球服务", "四大卫星导航系统", "北斗有什么特色功能"],
     ["问 GPS 定位原理", "问授时与电力安全"],
     "atomic", "",
     "北斗 BDS：2020 全球开通(三步走)，四大导航之一(GPS/GLONASS/伽利略)；特色=短报文求救+高精度授时+毫米级增强；星座 GEO+IGSO+MEO 约 30 星；应用=导航/共享单车/地震预警。"),
]

QUESTIONS = [
    ("QB-429", "托盘天平的使用步骤", "物理学", "技术直答",
     ["左物右码", "游码"], "通识拓展74"),
    ("QB-430", "干粉灭火器适用于什么火灾", "生活常识", "技术直答",
     ["ABC", "通用"], "通识拓展74"),
    ("QB-431", "干细胞有什么用", "生物学", "技术直答",
     ["分化", "再生", "移植"], "通识拓展74"),
    ("QB-432", "中国的全球定位系统叫什么", "地理学", "技术直答",
     ["北斗"], "通识拓展74"),
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
                               "level:L2", "status:verified", "batch:通识拓展74"],
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
    bank["version"] = "v1.66"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
