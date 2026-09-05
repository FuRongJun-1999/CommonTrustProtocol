# -*- coding: utf-8 -*-
"""seed_common_156_cards.py · 通识拓展批次156知识卡+题库（幂等）

156：生活常识-盲盒与理性消费/生活常识-果汁送药与药物相互作用/化学-烫发的化学原理
KCCS 四要素+题干原句触发词。三重预检：盲盒/果汁送药/烫发均双库零覆盖
（「药物」命中实为基因工程同名异物——读内容判定法再次生效）。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_blindbox",
     "盲盒与理性消费",
     "生活常识知识点内容（人话接口）", "生活常识",
     "盲盒机制与风险：①**为什么容易上瘾**——「不确定奖励」是行为心理学中最强"
     "的上瘾设计（斯金纳箱实验：**不定比例奖励**比固定奖励更让动物反复按杆）"
     "——拆盒前的期待感+未抽到隐藏款的不甘心=「再来一个」循环；②**监管要"
     "求**（2023 年国家市场监督管理总局《盲盒经营行为规范指引》）：公示**抽取"
     "概率**与隐藏款数量、不得向 **8 岁以下**未成年人销售、8 岁以上未成年人大"
     "额购买需监护人同意；③**投机陷阱**——「炒盲盒」二级市场价格由热度决定，"
     "热度退潮即崩盘（隐秘款溢价千元的神话只是头部故事）；④**理性定位**——"
     "设定娱乐预算（花完即止）、把概率当数学题算（隐藏款 1/144 意味着平均要"
     "买 144 个）、警惕「集齐全套」沉没成本绑架。",
     ["盲盒为什么让人上瘾", "盲盒概率公示规定", "未成年人买盲盒",
      "炒盲盒风险", "斯金纳箱原理", "隐藏款概率"],
     ["问彩票概率（用彩票卡）", "问游戏抽卡机制"],
     "atomic", "",
     "盲盒上瘾=不确定奖励（斯金纳箱不定比例强化最易成瘾）+隐藏款执念；监管=公示概率+8 岁下禁售+未成年大额需监护人同意；炒盒=热度泡沫崩盘即亏；理性=娱乐预算花完即止+算期望（1/144=平均买 144 个）。"),
    ("kp_card_meddrink",
     "用什么送药有讲究",
     "生活常识知识点内容（人话接口）", "生活常识",
     "服药最安全的液体=**温开水**（200ml 左右）。危险组合：①**西柚汁（葡萄"
     "柚）**——含呋喃香豆素**抑制肝药酶 CYP3A4**，使降压药（硝苯地平）、他汀"
     "类降脂药等代谢减慢、血药浓度骤升=药效过猛甚至中毒（效应可持续 24 小时"
     "以上，间隔吃也不保险）；②**牛奶**——钙与**四环素类、喹诺酮类**抗生素"
     "螯合沉淀，药效大减（补钙与吃药间隔 2 小时以上）；③**茶**——鞣酸与铁剂"
     "结合（贫血补铁别配茶）、影响部分镇静药；④**酒精+头孢类抗生素=双硫仑样"
     "反应**（面红心悸呼吸困难重可休克）——「头孢配酒说走就走」，停药后一周"
     "内都别沾酒；⑤咖啡因加剧某些药的心悸副作用。牢记：说明书「禁用/避免」"
     "条款认真读，拿不准就温开水。",
     ["用什么送药最安全", "西柚汁为什么不能和药一起吃", "头孢配酒",
      "牛奶送药可以吗", "茶水解药吗", "双硫仑样反应"],
     ["问药物储存方法", "问儿童用药剂量"],
     "atomic", "",
     "送药=温开水最安全；西柚汁抑 CYP3A4 使降压/他汀浓度骤升；牛奶钙螯合四环素喹诺酮（隔 2h）；茶鞣酸碍补铁；头孢+酒精=双硫仑样反应可休克（停药一周忌酒）；说明书禁忌认真读。"),
    ("kp_card_permchemistry",
     "烫发与染发的化学原理",
     "基础科学知识点内容（人话接口）", "化学",
     "头发≈角蛋白长链，链间靠**二硫键**（-S-S-，两个半胱氨酸氧化相连）等交联"
     "固定形状——这就是为什么头发「记性」很好。**烫卷原理（冷烫）**：①**还原"
     "剂**（巯基乙酸类药水）**打断二硫键**——头发变软可塑；②卷上烫发杠定型；"
     "③**氧化剂**（过氧化氢/溴酸盐「定型剂」）让半胱氨酸在**新位置重新氧化成"
     "新的二硫键**——形状被「焊死」成卷曲（拉直同理反向操作）；④染发——**氧"
     "化染料**小分子渗入发芯+双氧水氧化显色并「锁」在内部（所以会褪色、会长"
     "出黑根）。健康提示：药水碱性+双氧水会使**毛鳞片张开、蛋白流失**——频繁"
     "烫染=干枯分叉易断（烫染间隔至少 3-6 个月、用护发素闭合毛鳞片）；对苯二"
     "胺等染料成分可能致敏——染前 48 小时做**皮肤过敏测试**。",
     ["烫发的化学原理", "二硫键和头发卷曲", "冷烫怎么起作用",
      "染发为什么会褪色", "频繁烫染的伤害", "染发过敏测试"],
     ["问天然植物染发剂", "问脱发治疗（就医）"],
     "atomic", "",
     "烫发=还原剂打断角蛋白二硫键→卷杠定型→氧化剂新位置重组键「焊死」形状（拉直反向）；染发=氧化染料渗入+双氧水显色（褪色+长黑根）；碱性药水+双氧水伤毛鳞片——间隔 3-6 月；对苯二胺致敏染前 48h 皮试。"),
]

QUESTIONS = [
    ("QB-724", "盲盒为什么容易让人上瘾？国家对盲盒经营有哪些保护未成年人的规定？", "生活常识", "技术直答",
     ["不确定", "斯金纳", "概率公示", "8岁", "监护人"], "通识拓展156"),
    ("QB-725", "为什么吃降压药、他汀类药物时不能喝西柚汁？头孢类药物为什么不能配酒？", "生活常识", "技术直答",
     ["西柚", "葡萄柚", "CYP3A4", "浓度", "双硫仑", "头孢"], "通识拓展156"),
    ("QB-726", "烫发是怎么让头发「记住」卷曲形状的？涉及什么化学键的变化？", "化学", "技术直答",
     ["二硫键", "角蛋白", "还原", "氧化", "重组", "定型"], "通识拓展156"),
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
                               "level:L2", "status:verified", "batch:通识拓展156"],
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
    bank["version"] = "v4.29"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
