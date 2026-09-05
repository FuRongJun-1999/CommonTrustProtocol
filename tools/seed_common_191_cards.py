# -*- coding: utf-8 -*-
"""seed_common_191_cards.py · 通识拓展批次191知识卡+题库（幂等）

191：生物学-猫头鹰为什么能转头270度/物理学-潜艇如何上浮下潜/生活常识-手术服为什么是绿色的
KCCS 四要素+题干原句触发词。三重预检：三主题双库零覆盖（潜艇在超声波卡仅
声呐应用提及——浮沉原理角度划界）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_owlturn",
     "猫头鹰为什么能转头270度",
     "基础科学知识点内容（人话接口）", "生物学",
     "猫头鹰能把头转约 **270 度**（人类只能约 90 度而不伤身体），三大结构支"
     "持：①**颈椎 14 块**（人类只有 7 块）——更多的「关节段」让转动范围成倍"
     "增加；②**血管预留冗余**——颌骨下方血管孔径宽大、且椎动脉间有**吻合支**"
     "（备用通路），转头时脑部供血不中断（人类剧烈转头会扭到血管）；③**眼睛"
     "是管状固定眼**——猫头鹰眼球呈管状无法在眼窝里转动，看侧面必须转头，这"
     "是「被迫进化」出的超能力。附加彩蛋：猫头鹰羽毛边缘呈**锯齿梳状**，飞"
     "行时打破气流湍流——**几乎无声飞行**（伏击猎物的利器）；耳朵不对称（一"
     "高一低）用于立体定位声源。",
     ["猫头鹰为什么能转头270度", "猫头鹰颈椎", "猫头鹰无声飞行",
      "为什么猫头鹰眼睛不会转", "猫头鹰耳朵不对称"],
     ["问动物夜视（用鸟类视觉）", "问猫头鹰保护"],
     "atomic", "",
     "猫头鹰转头 270°=颈椎 14 块(人 7 块)+血管冗余吻合支供血不断+管状固定眼被迫转头补偿；羽毛锯齿缘消音=无声飞行；耳朵不对称立体定位声源——夜行伏击全套装备。"),
    ("kp_card_submerge",
     "潜艇如何上浮下潜",
     "基础科学知识点内容（人话接口）", "物理学",
     "潜艇靠**改变自身重力**实现上浮下潜（阿基米德浮力不变的前提下）：①艇体"
     "有**主压载水舱**——下潜时打开通海阀**注水**（重力>浮力→下沉）；上浮"
     "时用**压缩空气把水排出**（重力<浮力→上浮）；②精密潜航状态用**深浅水"
     "舱微调**配平；③与鱼对比：鱼靠**鱼鳔充放气改变自身体积**（改变浮力），"
     "潜艇靠**改变重量**——殊途同归都是打破浮力与重力的平衡。**深潜挑战**："
     "每下潜 10 米增加约 1 个大气压——深海潜艇（如「奋斗者号」10909 米）需"
     "球形耐压舱+新型钛合金/新材料对抗水压。",
     ["潜艇为什么能上浮下潜", "潜艇水舱原理", "潜艇和鱼上浮下潜的区别",
      "阿基米德原理潜艇", "深潜器耐压"],
     ["问阿基米德原理计算", "问载人深潜工程"],
     "atomic", "",
     "潜艇=改变自身重力（主压载水舱注水下潜/压缩空气排水上浮）打破浮力平衡；鱼=鱼鳔改变体积改变浮力——殊途同归；深潜每 10 米+1 大气压，万米级需球形耐压舱+钛合金（奋斗者号 10909m）。"),
    ("kp_card_greenscrubs",
     "手术服为什么是绿色的",
     "基础科学知识点内容（人话接口）", "生活常识",
     "手术服/手术巾从白改**蓝绿色**是视觉科学：①**视觉残像**——长时间盯着红"
     "色（血液与内脏），视网膜上对红光疲劳的感光细胞会「余像」出**蓝绿色的补"
     "色**残影；视线一移到白色（工作服/白墙）上，蓝绿色斑块干扰视线——改用"
     "**蓝绿色（红的互补色）**环境，残像被环境吸收，视线「归零」更稳；②**降"
     "低血迹视觉刺激**——红色对红色的对比刺眼易引起视觉疲劳与紧张，蓝绿底色"
     "上血迹对比柔和；③补色原理：色轮上相对的两色（红-绿、蓝-橙）互为互补"
     "色。同类应用：雷雨天看闪电后再看灯会出绿色残像、老电视雪花屏后像。",
     ["手术服为什么是绿色的", "视觉残像", "互补色", "手术衣颜色",
      "为什么医生穿蓝绿色"],
     ["问色盲原理", "问医院标识色"],
     "atomic", "",
     "手术服蓝绿色=长时间盯红色血液后视网膜红敏感细胞疲劳产生蓝绿补色残像，移视白色干扰视线——蓝绿环境吸收残像稳视线+柔化血迹刺激；互补色=色轮对角红-绿蓝-橙。"),
]

QUESTIONS = [
    ("QB-809", "猫头鹰为什么能把头转约 270 度？它的眼睛结构有什么特殊性？", "生物学", "技术直答",
     ["颈椎", "14块", "血管", "管状", "固定眼", "转头"], "通识拓展191"),
    ("QB-810", "潜艇是靠什么原理实现上浮和下潜的？它和鱼的浮沉方式有什么不同？", "物理学", "技术直答",
     ["压载水舱", "注水", "排水", "重力", "浮力", "鱼鳔", "体积"], "通识拓展191"),
    ("QB-811", "手术室里医生穿的衣服为什么是蓝绿色而不是白色？", "生活常识", "技术直答",
     ["视觉残像", "互补色", "红色", "疲劳", "对比"], "通识拓展191"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{6,}", content):
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
                               "level:L2", "status:verified", "batch:通识拓展191"],
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
    bank["version"] = "v4.64"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
