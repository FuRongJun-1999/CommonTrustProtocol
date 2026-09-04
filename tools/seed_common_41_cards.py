# -*- coding: utf-8 -*-
"""seed_common_41_cards.py · 通识拓展批次41知识卡+题库（幂等）

41：物理学-铜做电线/地理学-地球五带/生物学-血液的成分/艺术-敦煌莫高窟
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_copperwire",
     "为什么用铜做电线",
     "基础科学知识点内容（人话接口）", "物理学",
     "导电性最好的金属是银（其次铜、金、铝），但电线用铜不用银——成本：银太贵"
     "（只用于精密触点/高端镀层），铜导电性接近银且价格适中、延展性好（拉成细丝"
     "不断）、耐腐蚀，是性能与成本的平衡点。高压远距离输电常用铝线（更轻更便宜，"
     "加钢芯增强——钢芯铝绞线）。超导材料零电阻是未来方向（需极低温，成本高）。"
     "与「为什么用铜」相对的考点：保险丝用电阻率大熔点低的铅锑合金、电热丝用电阻"
     "大的镍铬合金——不同用途选不同材料，导电好≠什么都好。",
     ["为什么用铜做电线", "导电性最好的金属是什么", "高压线为什么用铝线",
      "钢芯铝绞线是什么", "超导材料能做电线吗", "电热丝为什么用镍铬合金"],
     ["问电阻率表", "问半导体与绝缘体"],
     "atomic", "",
     "导电排名=银>铜>金>铝；电线用铜=性能成本平衡(延展/耐蚀)；高压线=钢芯铝绞线(轻廉)；保险丝/电热丝反其道用高电阻率材料。"),
    ("kp_card_fivezones",
     "地球的五带划分",
     "人文通识知识点内容（人话接口）", "地理学",
     "地球按太阳热量分布分五带，界线是回归线（南北纬 23.5°）和极圈（南北纬 66."
     "5°）：①热带（南北回归线之间）——终年太阳直射或近直射，终年炎热；②北温带/"
     "③南温带（回归线到极圈之间）——四季分明，是人口和文明最集中的地带；④北寒"
     "带/⑤南寒带（极圈以内）——有极昼极夜现象，终年严寒。划分依据是太阳照射的"
     "角度：黄赤交角 23.5° 使太阳直射点在南北回归线之间往返（周年移动），造成四"
     "季更替；极圈内夏季有极昼、冬季有极夜。中国大部分位于北温带，南部小部分在"
     "热带（海南/雷州半岛/云南南部/台湾南部）。",
     ["地球五带怎么划分", "热带和温带的分界线", "什么是极昼极夜",
      "四季更替的原因是什么", "中国在哪个温度带", "回归线的纬度是多少"],
     ["问黄赤交角天文细节", "问各带代表气候类型"],
     "atomic", "",
     "五带界线=回归线(23.5°)+极圈(66.5°)：热带(直射·炎热)/南北温带(四季分明)/南北寒带(极昼极夜)；成因=黄赤交角 23.5°·直射点周年移动；中国主体北温带。"),
    ("kp_card_blood",
     "血液的成分",
     "基础科学知识点内容（人话接口）", "生物学",
     "血液由血浆和血细胞组成：血浆（约55%，淡黄色液体）主要含水+血浆蛋白，负责"
     "运载血细胞、运输营养与废物；血细胞（约45%）三种——①红细胞（最多，含血红"
     "蛋白，运氧/运部分CO₂，缺铁或失血多会贫血）；②白细胞（免疫防御，发炎时升"
     "高吞噬病菌）；③血小板（最小，止血凝血——伤口结的痂就有它）。ABO 血型按红"
     "细胞表面抗原图（A/B/AB/O）。献血与健康：一次献血 200-400 毫米（ml）可较快"
     "恢复；化验单「白细胞升高」常提示感染，是体检常见指标。",
     ["血液里有什么", "红细胞的作用是什么", "白细胞升高说明什么",
      "血小板有什么用", "贫血缺什么", "血浆和血细胞的区别"],
     ["问血常规解读", "问造血干细胞"],
     "atomic", "",
     "血液=血浆(55%·运载+运养料废物)+血细胞：红细胞(血红蛋白运氧·缺铁贫血)/白细胞(免疫·升高提示感染)/血小板(止血凝血)。"),
    ("kp_card_mogao",
     "敦煌莫高窟",
     "人文通识知识点内容（人话接口）", "艺术",
     "敦煌莫高窟俗称千佛洞：位于甘肃敦煌鸣沙山东麓，始建于十六国前秦时期（366 "
     "年，僧人乐僔开凿第一窟），历经十六国、北朝、隋、唐、五代、西夏、元等十几个"
     "朝代持续营建千年，现存洞窟 735 个、壁画 4.5 万平方米、彩塑 2400 余尊——是"
     "世界上现存规模最大、内容最丰富的佛教艺术地，1987 年入选中国首批世界文化遗"
     "产。藏经洞（1900 年王圆箓发现，5 万余件文书）催生了国际显学「敦煌学」——"
     "也因清末流散海外成为文化伤痛记忆。壁画题材：飞天（不长翅膀、凭飘带凌空）"
     "是敦煌艺术名片；九色鹿故事画出自北魏第 257 窟。",
     ["敦煌莫高窟以什么闻名", "莫高窟是哪个朝代开始建造的", "藏经洞是谁发现的",
      "什么是敦煌学", "飞天是哪里的艺术形象", "莫高窟有多少个洞窟"],
     ["问云冈龙门石窟对比", "问丝路佛教东传"],
     "atomic", "",
     "莫高窟=甘肃敦煌·366 年前秦始凿·千年营建：735 窟/4.5 万m²壁画/2400 彩塑，世界最大佛教艺术地·首批世遗；藏经洞(1900)→敦煌学；飞天=名片。"),
]

QUESTIONS = [
    ("QB-297", "为什么用铜做电线", "物理学", "技术直答",
     ["导电性", "延展性"], "通识拓展41"),
    ("QB-298", "地球五带怎么划分", "地理学", "技术直答",
     ["回归线", "极圈"], "通识拓展41"),
    ("QB-299", "血液里有什么", "生物学", "技术直答",
     ["血浆", "红细胞", "白细胞", "血小板"], "通识拓展41"),
    ("QB-300", "敦煌莫高窟以什么闻名", "艺术", "技术直答",
     ["壁画", "彩塑", "佛教艺术"], "通识拓展41"),
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
                               "level:L2", "status:verified", "batch:通识拓展41"],
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
    bank["version"] = "v1.33"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
