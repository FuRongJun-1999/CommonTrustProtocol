# -*- coding: utf-8 -*-
"""seed_common_161_cards.py · 通识拓展批次161知识卡+题库（幂等）

161：历史学-天干地支与十二生肖/数学-阿拉伯数字的起源/生活常识-筷子使用禁忌
KCCS 四要素+题干原句触发词。三重预检：三主题双库零覆盖（筷子在折射卡仅物理
现象提及——礼仪文化角度划界；闰年/金属活动等候选命中已有覆盖弃选）。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_stemsbranches",
     "天干地支与十二生肖",
     "人文通识知识点内容（人话接口）", "历史学",
     "**天干地支**=中国古代纪年法：**十天干**——甲、乙、丙、丁、戊、己、庚、"
     "辛、壬、癸；**十二地支**——子、丑、寅、卯、辰、巳、午、未、申、酉、"
     "戌、亥。干支相配（阳配阳阴配阴）**60 年一循环**，称「**六十甲子**」（"
     "所以 60 岁称「花甲」）。**十二生肖**=十二地支配十二种动物：**子鼠、丑"
     "牛、寅虎、卯兔、辰龙、巳蛇、午马、未羊、申猴、酉鸡、戌狗、亥猪**——地"
     "支纪年即生肖年（属相）。举例：2024 甲辰（龙）年→2025 乙巳（蛇）年→"
     "**2026 丙午（马）年**。注意：生肖按**农历（立春/春节）**切换，不是公历"
     "元旦——元旦出生的孩子属相还算前一年的。时辰：一天 12 时辰，子时=23-1"
     "点（故「半夜三更」）、午时=11-13 点（「午时三刻问斩」）。",
     ["天干地支怎么算", "十二生肖顺序", "2026年是什么年", "六十甲子",
      "花甲为什么是60岁", "子时是什么时候"],
     ["问二十四节气（用节气卡）", "问星座与黄道"],
     "atomic", "",
     "天干地支=十天干甲乙丙丁戊己庚辛壬癸+十二地支子丑寅卯辰巳午未申酉戌亥配 60 甲子（60 岁=花甲）；生肖=子鼠丑牛寅虎卯兔辰龙巳蛇午马未羊申猴酉鸡戌狗亥猪；2026 丙午马年；生肖按农历切、元旦出生属前一年；子时=23-1 点。"),
    ("kp_card_arabicnum",
     "阿拉伯数字的起源",
     "基础科学知识点内容（人话接口）", "数学",
     "「阿拉伯数字」其实是**印度人发明、阿拉伯人传播**的——名字是个历史误会："
     "①**起源**：约公元 3-7 世纪印度婆罗米数字演化而来，印度人的伟大贡献是**"
     "「0」的符号与十进位值制**（用 0-9 十个符号，靠「位置」表示大小——523 "
     "中 5 代表 500，比罗马数字 I V X L C 累加制先进太多）；②**传播**：阿拉伯"
     "帝国学者（如花剌子米）吸收并推广到西亚北非，**12 世纪经西班牙/北非传入"
     "欧洲**（翻译运动）——欧洲人从阿拉伯人那里学来，故称「阿拉伯数字」；"
     "③**定型**：16 世纪欧洲印刷术普及后字形才固定成今天的 0-9。对比：中文「"
     "一二三」也很早使用十进制（甲骨文已有），但算筹/珠算体系让位给更便于笔算"
     "的阿拉伯数字。冷知识：阿拉伯国家自己的数字写法（٠١٢٣）与「阿拉伯数字"
     "」还不完全一样。",
     ["阿拉伯数字是谁发明的", "数字0是哪个国家发明的", "为什么叫阿拉伯数字",
      "十进位值制", "罗马数字为什么被淘汰"],
     ["问圆周率计算史（用圆周率卡）", "问二进制与计算机"],
     "atomic", "",
     "阿拉伯数字=印度人发明（0 符号+十进位值制是核心贡献）→阿拉伯帝国吸收推广→12 世纪传入欧洲得名「阿拉伯」；16 世纪定型 0-9；位值制 523 中 5=500 优于罗马累加制；甲骨文已见十进制；阿拉伯本国写法 ٠١٢٣ 与通行体不同。"),
    ("kp_card_chopsticks",
     "筷子的文化与禁忌",
     "人文通识知识点内容（人话接口）", "生活常识",
     "筷子起源传说：大禹治水时折树枝夹食（「折枝为箸」）；有文字可考至少 **"
     "3000 多年**（商代纣王已用象牙箸——《韩非子》「纣为象箸而箕子怖」），"
     "先秦称「梜」、汉代称「箸」，明代因避讳「箸≈住（停船）」改称「**筷**（"
     "快）」。**餐桌禁忌**（多为谐音避讳或礼仪）：①**不插在饭上**——形似上香"
     "祭奠，大忌；②**不敲碗盘**——旧时乞丐乞食动作；③**不指人**——不敬；④"
     "**不在菜盘里翻拣**（「迷箸刨坟」）、不含叼筷子、不用筷子指菜犹豫；⑤"
     "夹菜用公筷更卫生。**世界之最**：筷子=东亚饮食文化圈标志（中/日/韩/越），"
     "标准长度七寸六分（约 22-24cm，寓意七情六欲——民俗说法）。正确握姿：上"
     "动下不动——下面一根固定、上面一根动手指夹取。",
     ["筷子不能插在饭上为什么", "筷子有哪些禁忌", "筷子的起源",
      "为什么叫筷子不叫箸", "筷子多长", "正确拿筷子"],
     ["问西餐刀叉礼仪", "问各国饮食文化"],
     "atomic", "",
     "筷子=大禹折枝传说+商代象牙箸 3000 余年；明避讳「箸≈住」改「筷」；禁忌=不插饭上(似上香)/不敲碗(乞丐)/不指人/不翻拣菜；七寸六分长约 22-24cm；握姿=下固定上动指；东亚饮食圈标志。"),
]

QUESTIONS = [
    ("QB-738", "天干地支各有哪些？为什么 60 岁被称为「花甲之年」？", "历史学", "技术直答",
     ["甲乙丙丁", "子丑寅卯", "60", "六十年", "循环"], "通识拓展161"),
    ("QB-739", "阿拉伯数字是阿拉伯人发明的吗？数字「0」最早由哪个文明使用？", "数学", "技术直答",
     ["印度", "发明", "阿拉伯", "传播", "0"], "通识拓展161"),
    ("QB-740", "筷子为什么不能插在米饭上？使用筷子还有哪些餐桌禁忌？", "生活常识", "技术直答",
     ["上香", "祭奠", "敲碗", "指人", "翻拣"], "通识拓展161"),
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
                               "level:L2", "status:verified", "batch:通识拓展161"],
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
    bank["version"] = "v4.34"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
