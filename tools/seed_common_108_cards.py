# -*- coding: utf-8 -*-
"""seed_common_108_cards.py · 通识拓展批次108知识卡+题库（幂等）

108：物理学-宇宙探索/化学-煤的干馏/生物学-神经调节与体液调节
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_spaceexp",
     "中国宇宙探索：嫦娥探月与天问探火",
     "基础科学知识点内容（人话接口）", "物理学",
     "中国深空探测两大工程：①**嫦娥探月工程**——「绕、落、回」三步走：嫦娥一号"
     "绕月（2007）、嫦娥三号落月（玉兔号月球车）、嫦娥四号人类首次月背着陆"
     "（2019，鹊桥中继星）、嫦娥五号月球采样返回（2020，1731 克月壤）——中国成"
     "为第三个采回月壤的国家；②**天问一号探火**（2021）：一次实现火星环绕+着陆"
     "＋巡视（祝融号火星车），世界首次一次任务完成三步。后续：嫦娥六号月背采样"
     "（2024）、载人登月计划 2030 年前、天宫空间站（2022 建成）长期载人。行星探"
     "测意义：寻找水与生命痕迹、资源远景（月球氦-3）、技术带动。",
     ["中国的探月工程叫什么", "嫦娥五号的任务", "天问一号探测的是什么",
      "祝融号是什么", "嫦娥四号有什么突破", "中国载人登月什么时候"],
     ["问月球科研站计划", "问火星移民设想"],
     "atomic", "",
     "嫦娥探月=绕落回三步：嫦娥四首次月背着陆(鹊桥中继)·五号采回 1731g 月壤；天问一号 2021 一次实现环落巡(祝融号)；载人登月 2030 前；天宫空间站 2022 建成。"),
    ("kp_card_coalcarbon",
     "煤的干馏：化学变化",
     "基础科学知识点内容（人话接口）", "化学",
     "煤的干馏：煤隔绝空气加强热使之分解的过程——是**化学变化**（生成了新物"
     "质）。产物三种状态：①固态——焦炭（冶金炼铁的还原剂/燃料）；②液态——煤焦"
     "油（化工原料，可提取苯等）+粗氨水；③气态——焦炉煤气（H₂/CH₄/CO，可燃）。"
     "易混辨析：煤的干馏是化学变化；石油的分馏是**物理变化**（利用沸点不同分离，"
     "无新物质生成）——「干馏化学、分馏物理」是常考辨析点。煤的综合利用使「黑"
     "色石头」变成工业粮食：1 吨煤干馏可得约 700-750kg 焦炭。煤直接燃烧污染大、"
     "利用率低——综合利用（干馏/气化/液化）才是方向。",
     ["煤的干馏是化学变化还是物理变化", "煤干馏的产物", "焦炭有什么用途",
      "干馏和分馏的区别", "煤的综合利用有哪些", "焦炉煤气的主要成分"],
     ["问石油分馏产品复习", "问煤化工产业"],
     "atomic", "",
     "煤干馏=隔绝空气强热·**化学变化**：焦炭(固·炼铁)+煤焦油(液·化工)+焦炉煤气(气·可燃)；石油分馏=物理变化(沸点分离)；「干馏化学分馏物理」口诀。"),
    ("kp_card_neurohumor",
     "神经调节与体液调节",
     "基础科学知识点内容（人话接口）", "生物学",
     "人体两大调节机制：①**神经调节**——神经系统通过反射实现：反应**迅速、准确"
     "、短暂**（缩手反射/膝跳反射）；②**体液调节**——激素等化学物质通过血液运输"
     "：反应**较慢、作用范围广、持续时间长**（胰岛素调血糖/生长激素促发育）。两"
     "者关系：神经调节为主导，体液调节为辅助，相互配合——如恐惧时先心跳加速（神"
     "经）随后肾上腺素持续供应（体液）。内分泌失调疾病：糖尿病（胰岛素不足，注"
     "射治疗——口服会被消化分解成氨基酸失效）、甲亢（甲状腺激素过多）、侏儒症与"
     "巨人症（生长激素异常）。稳态：健康人各项指标（体温/血糖/pH）保持相对稳定"
     "——神经-体液-免疫三大调节网络共同维持。",
     ["神经调节和体液调节的区别", "人体有哪两大调节方式", "胰岛素为什么不能口服",
      "糖尿病的原因", "什么是内环境稳态", "神经调节的特点"],
     ["问反射弧复习", "问血糖调节机制"],
     "atomic", "",
     "神经调节=快准短(反射·主导)+体液调节=慢广久(激素·血液运输)：恐惧先神经后肾上腺素；胰岛素口服失效(被消化)须注射；稳态=神经-体液-免疫网络维持。"),
]

QUESTIONS = [
    ("QB-565", "中国的探月工程叫什么", "物理学", "技术直答",
     ["嫦娥"], "通识拓展108"),
    ("QB-566", "煤的干馏是化学变化还是物理变化", "化学", "技术直答",
     ["化学变化"], "通识拓展108"),
    ("QB-567", "神经调节和体液调节的区别", "生物学", "技术直答",
     ["快慢", "神经快"], "通识拓展108"),
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
                               "level:L2", "status:verified", "batch:通识拓展108"],
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
    bank["version"] = "v2.0"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
