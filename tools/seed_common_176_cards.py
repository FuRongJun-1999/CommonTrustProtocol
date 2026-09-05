# -*- coding: utf-8 -*-
"""seed_common_176_cards.py · 通识拓展批次176知识卡+题库（幂等）

176：生活常识-久坐的危害/物理学-姆潘巴效应/生活常识-眼皮跳辟谣
KCCS 四要素+题干原句触发词。三重预检：三主题双库零覆盖（葡萄白霜与挑西瓜
卡重叠弃选）。执行前外文长词检测（Mpemba 加白名单）。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_sitting",
     "久坐的危害",
     "生活常识知识点内容（人话接口）", "生活常识",
     "久坐被一些研究者称为「新型慢性自杀」——即使定期健身也抵消不了长时间连"
     "续静坐的伤害（「久坐是独立的健康风险因素」）。连续静坐 1 小时以上：下肢"
     "血流减慢（静脉血栓风险↑）、腰肌持续受压（腰突/颈椎问题）、热量消耗降到"
     "极低、胰岛素敏感性下降（血糖波动）。**对策**：①**每坐 45-60 分钟起身活"
     "动 2-3 分钟**（接水/走动/拉伸——闹钟提醒）；②能站不坐：站立办公交替、"
     "接电话走动、楼梯代电梯；③坐姿：双脚踩实、腰靠椅背、屏幕与视线平（预防"
     "颈椎前倾）；④世卫组织建议成人每周 150 分钟中等强度运动——「练 1 小时"
     "救不了坐 10 小时」，减少连续静坐时长与运动同等重要。腰突急性期/痔疮患"
     "者尤需勤起身。",
     ["久坐有什么危害", "久坐多久起来活动", "久坐腰疼怎么办",
      "站立办公", "久坐血栓", "正确的坐姿"],
     ["问颈椎保健（用颈椎卡）", "问健身入门（用减重卡）"],
     "atomic", "",
     "久坐=独立健康风险（血栓/腰颈椎/胰岛素敏感性下降），健身也难抵消；对策=每 45-60 分钟起身 2-3 分钟+能站不坐+腰靠椅背屏幕平视；每周 150 分钟运动与减少静坐同等重要——练 1 小时救不了坐 10 小时。"),
    ("kp_card_mpemba",
     "姆潘巴效应",
     "基础科学知识点内容（人话接口）", "物理学",
     "**姆潘巴效应（Mpemba effect）**=在某些条件下，**热水比冷水先结冰**的反"
     "直觉现象。来历：1963 年坦桑尼亚中学生**埃拉斯托·姆潘巴**发现热冰淇淋液"
     "比冷的先冻住，追问老师被嘲笑；1969 年与物理学家共同发表论文后进入科学"
     "视野。**可能机理（至今未有公认定论）**：①热水**蒸发更快**——水量减少+"
     "汽化带走热量；②**对流**更强（热水温差大，热量更快到达表面散失）；③**"
     "溶解气体逸出**改变冰点与对流结构；④**过冷程度不同**（冷水更易「过度冷"
     "却」低于 0°C 才结冰，热水反而较早触发成核）；⑤容器/环境因素干扰。**科"
     "学态度的示范**：姆潘巴效应可复现性存在争议（不同实验条件结果不同）——"
     "科学界的处理不是强行解释，而是**承认「在何种条件下成立」仍未定论**，这"
     "正是科学面对未解现象的诚实姿态。",
     ["姆潘巴效应是什么", "热水比冷水先结冰", "热水冻得快是真的吗",
      "姆潘巴效应的原理", "科学未解现象"],
     ["问过冷水（水的新性质）", "问数字黑洞（趣味科学）"],
     "atomic", "",
     "姆潘巴效应=某些条件下热水先结冰的反直觉现象（1963 中学生姆潘巴发现）：候选机理=蒸发减量/强对流/溶气逸出/过冷差异——至今无定论且重现性有争议；科学界诚实承认未解而非强行解释=科学态度的示范。"),
    ("kp_card_eyelid",
     "眼皮跳的真相",
     "生活常识知识点内容（人话接口）", "生活常识",
     "「左眼跳财右眼跳灾」是迷信——眼皮跳=**眼轮匝肌不自主痉挛**（眼睑震颤），"
     "与运势无关。**诱因**：用眼过度疲劳、睡眠不足、精神紧张压力、咖啡因/浓茶"
     "过量、电解质（镁）流失、干眼刺激。**处理**：闭眼热敷放松、补足睡眠、减"
     "咖啡因、温和按摩眼周；多数几分钟到几天自行消失。**就医信号**：跳动**持"
     "续超过一周不缓解**、痉挛扩散到同侧面部肌肉（嘴角也抽——面肌痉挛）、伴"
     "眼睛红肿/下垂/视力变化——神经内科/眼科排查（极少数需要肉毒素或进一步"
     "检查）。眼保健操的「轮刮眼眶」、远眺放松对预防有效。",
     ["眼皮跳是什么原因", "左眼跳财右眼跳灾", "眼皮跳不停怎么办",
      "眼轮匝肌痉挛", "眼皮跳几天要就医"],
     ["问干眼症", "问面肌痉挛（就医）"],
     "atomic", "",
     "眼皮跳=眼轮匝肌不自主痉挛（疲劳/咖啡因/压力/缺镁诱因）与运势无关；处理=热敷+补眠+减咖啡因；就医信号=持续超一周/扩散到同侧面部（面肌痉挛）/伴红肿下垂视力变化。"),
]

QUESTIONS = [
    ("QB-778", "久坐对身体有哪些危害？应该每隔多久起身活动一次？", "生活常识", "技术直答",
     ["血栓", "腰椎", "胰岛素", "45", "60", "起身", "活动"], "通识拓展176"),
    ("QB-779", "姆潘巴效应指的是什么现象？为什么说它的机理至今没有定论？", "物理学", "技术直答",
     ["热水", "冷水", "先结冰", "蒸发", "过冷", "定论"], "通识拓展176"),
    ("QB-780", "眼皮跳的科学原因是什么？「左眼跳财右眼跳灾」有依据吗？", "生活常识", "技术直答",
     ["眼轮匝肌", "痉挛", "疲劳", "迷信", "就医"], "通识拓展176"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    whitelist = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba", "effect"}
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{6,}", content):
            if word not in whitelist:
                problems.append((node[0], f"长英文词: {word}"))
    if problems:
        raise SystemExit(f"外文长词检测报警: {problems}")


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
                               "level:L2", "status:verified", "batch:通识拓展176"],
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
    bank["version"] = "v4.49"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
