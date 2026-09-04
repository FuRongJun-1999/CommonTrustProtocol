# -*- coding: utf-8 -*-
"""seed_common_69_cards.py · 通识拓展批次69知识卡+题库（幂等）

69：物理学-自行车上的物理/化学-纯净物与混合物/生物学-真菌/地理学-地震避险
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞——本批预检命中
kp_card_quake（候选域梯队旧卡·主题=震级烈度），避险常识改用新 id kp_card_quakesafe。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_bikephys",
     "自行车上的物理知识",
     "基础科学知识点内容（人话接口）", "物理学",
     "自行车是「物理原理移动展」：①轴承滚珠——滚动代替滑动减小摩擦（与轮胎花"
     "纹增大摩擦相对照）；②车把手/脚踏板——轮轴省力（动力作用在大轮上）；③刹"
     "车——增大压力增大摩擦力（捏闸越紧停得越快）；④轮胎有花纹——增大接触面粗"
     "糙程度防滑；⑤车座宽大——增大受力面积减小压强（坐得舒服）；⑥尾灯（无电源"
     "角反射器）——把后方车灯的光沿原方向反射回去警示；⑦铃铛——振动发声；⑧"
     "骑行时车不倒——车轮转动产生定轴性（角动量守恒）+动态平衡修正。综合：自行"
     "车体现了「摩擦调控」「简单机械」「压强」「光学」多领域原理。",
     ["自行车哪些地方用了物理知识", "自行车轴承的作用", "自行车刹车原理",
      "自行车尾灯为什么不用电池", "车座为什么宽大", "自行车为什么骑着不倒"],
     ["问角动量守恒科普", "问摩擦力方向判断复习"],
     "atomic", "",
     "自行车物理：轴承滚珠(减摩)+把手轮轴(省力)+刹车(增压增摩)+花纹(增糙防滑)+宽座(减 p)+角反射尾灯+转动定轴性(不倒)——多原理集成。"),
    ("kp_card_puremix",
     "纯净物与混合物",
     "基础科学知识点内容（人话接口）", "化学",
     "物质分类：①纯净物——由一种物质组成，有固定组成与性质（蒸馏水 H₂O、氧气"
     "O₂、铁 Fe、二氧化碳）；纯净物再分单质（同种元素：O₂/Fe）与化合物（不同种"
     "元素：H₂O/CO₂/NaCl）。②混合物——由两种或多种物质混合而成，各成分保持各"
     "自性质、没有固定配比（空气、海水、矿泉水、合金、溶液、石灰石）。易错点："
     "冰水混合物其实是**纯净物**（只有 H₂O 一种物质，只是状态不同）；「洁净」的"
     "空气仍是混合物；高纯硅（99.999999999%）严格说仍是混合物（杂质≠零）。纯净"
     "物有固定熔沸点，混合物没有（可用测熔沸点判断纯度）。",
     ["纯净物和混合物怎么区分", "冰水混合物是纯净物吗", "空气是纯净物吗",
      "单质和化合物怎么分", "合金是纯净物吗", "自来水是混合物吗"],
     ["问元素周期表衔接", "问分离混合物方法"],
     "atomic", "",
     "纯净物=一种物质(固定组成性质·有固定熔沸点)：单质(O₂ Fe)+化合物(H₂O CO₂)；混合物=多物质各保持性质(空气/海水/合金)；冰水混合物=纯净物(同 H₂O)。"),
    ("kp_card_fungi",
     "真菌：蘑菇不是植物",
     "基础科学知识点内容（人话接口）", "生物学",
     "蘑菇、酵母菌、霉菌都是**真菌**——不是植物：真菌细胞没有叶绿体，不能光合"
     "作用，靠分解现成有机物生活（异养——腐生或寄生），这与动物「吃现成」一致，"
     "所以真菌自成一类（与植物/动物/细菌并列）。真菌细胞有细胞壁（成分几丁质，"
     "不同于植物纤维素）和成形的细胞核（真核生物——与细菌的 major 区别：细菌无"
     "成形细胞核属原核生物）。真菌与人类：酵母菌（酿酒烘焙）、霉菌（制酱/青霉素"
     "——弗莱明发现第一种抗生素）、食用菌（香菇/木耳）；有害面：脚气（足癣=真"
     "菌感染，与「脚气病」维生素B1 缺乏是两码事）、粮食霉变（黄曲霉素强致癌）。"
     "生态角色：分解者——把枯枝落叶分解回归自然。",
     ["蘑菇是植物吗", "真菌和植物的区别", "脚气和脚气病是一回事吗",
      "青霉素是谁发现的", "细菌和真菌的区别", "真菌在生态系统中是什么角色"],
     ["问抗生素耐药性", "问原核真核对比"],
     "atomic", "",
     "真菌(蘑菇/酵母/霉菌)=真核·有细胞壁(几丁质)·无叶绿体异养分——非植物；青霉素=弗莱明；脚气(足癣·真菌)≠脚气病(B1 缺乏)；生态=分解者。"),
    ("kp_card_quakesafe",
     "地震时的避险常识",
     "生活常识知识点内容（人话接口）", "生活常识",
     "地震避险原则「伏地、遮挡、手抓牢」（Drop, Cover, Hold on）：室内——迅速"
     "躲到坚固桌子下/承重墙内角，护住头颈，抓稳桌腿；远离窗户/吊灯/外墙玻璃/高"
     "柜；**不要**跳楼、不乘电梯（断电被困）；摇晃约持续几十秒，晃动停止后再迅"
     "速走楼梯撤到开阔地。室外——远离楼房/电线杆/广告牌，跑向开阔地蹲下护头；"
     "山区防滑坡滚石。被困废墟：保存体力、敲击管道发出声音求救（哨声更佳）、不"
     "盲目呼喊消耗体力、用衣物护住口鼻防尘。震后注意：主震后有余震、不返回受损"
     "建筑、用手机短信而非打电话（保通信容量）。预防性准备：家庭应急包（水/食"
     "物/手电/哨子/常用药）、知道自家燃气总阀位置。",
     ["地震时在室内怎么办", "地震避险三原则", "地震能坐电梯吗",
      "被废墟掩埋怎么求救", "地震后还要注意什么", "家庭应急包装什么"],
     ["问抗震设防标准", "问预警系统秒级原理"],
     "atomic", "",
     "地震避险=伏地·遮挡·手抓牢：室内躲桌下/内角护头颈·禁跳楼禁电梯；室外开阔地护头；被困=省体力敲管道求救；震后防余震·短信联络；常备应急包。"),
]

QUESTIONS = [
    ("QB-409", "自行车哪些地方用了物理知识", "物理学", "技术直答",
     ["摩擦", "轮轴", "压强"], "通识拓展69"),
    ("QB-410", "纯净物和混合物怎么区分", "化学", "技术直答",
     ["一种物质", "多种物质"], "通识拓展69"),
    ("QB-411", "蘑菇是植物吗", "生物学", "技术直答",
     ["不是", "真菌"], "通识拓展69"),
    ("QB-412", "地震时在室内怎么办", "生活常识", "技术直答",
     ["伏地", "遮挡", "护头"], "通识拓展69"),
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
                               "level:L2", "status:verified", "batch:通识拓展69"],
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
    bank["version"] = "v1.61"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
