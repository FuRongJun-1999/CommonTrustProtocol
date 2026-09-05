# -*- coding: utf-8 -*-
"""seed_common_165_cards.py · 通识拓展批次165知识卡+题库（幂等）

165：生活常识-春困秋乏/生物学-猫从高处摔下/生活常识-飞机舷窗为什么是圆的
KCCS 四要素+题干原句触发词。三重预检：三主题双库零覆盖（天空蓝散射/苹果
褐变等候选命中已有覆盖弃选）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_springsleepy",
     "春困秋乏的科学",
     "生活常识知识点内容（人话接口）", "生活常识",
     "「春困秋乏夏打盹，睡不醒的冬三月」——季节性倦怠的科学解释：①**春困**="
     "冬季血管收缩，春季气温回升**血管扩张**、体表供血增加，大脑供血相对调整"
     "过渡期→犯困；加上日照变长打乱褪黑素节律。②**秋乏**=夏季高消耗（出汗/"
     "睡眠差）后身体进入**自我修整期**，代谢回调的自然保护反应。都是**生理性"
     "季节适应**，不是疾病——1-2 周内自行适应。**应对**：规律作息（比冬天晚"
     "睡早起顺应日照，但保证 7-8 小时）+午睡 20 分钟+适度运动促循环+多喝水；"
     "饮食清淡少油腻（油腻加重餐后困倦）。**警觉线**：若嗜睡持续超过 2-3 周、"
     "伴随情绪低落（春季也是抑郁/双相高发季）或鼾声如雷白天困倦（睡眠呼吸暂"
     "停），就不是「春困」而应就医。",
     ["春困是怎么回事", "秋乏的原因", "季节性犯困正常吗",
      "春困怎么缓解", "总是睡不醒怎么回事"],
     ["问失眠治疗", "问贫血导致的疲倦（就医排查）"],
     "atomic", "",
     "春困=血管扩张大脑供血调整+日照打乱褪黑素节律；秋乏=夏耗后自我修整保护反应；均为生理性季节适应 1-2 周自愈；应对=规律作息+午睡 20min+运动+清淡饮食；持续嗜睡>2-3 周或伴情绪低落/鼾症应就医。"),
    ("kp_card_catfall",
     "猫从高处摔下为什么不容易死",
     "基础科学知识点内容（人话接口）", "生物学",
     "猫的「高空生存能力」来自三重天赋：①**正位反射（翻正反射）**——内耳前庭"
     "感知失衡→脊柱柔韧（椎骨间宽松连接）→在**0.1 秒内扭转身体**四脚朝下落"
     "地；②**肉垫缓冲**——厚肉垫+可折叠的前肢像减震器分散冲击；③**体小表"
     "面积大**——下落时承受的冲击压强相对小。研究趣闻（兽医统计）：坠落楼层"
     "在 **2-6 层受伤率随高度上升**，但 **7 层以上反而略降**——因为坠落时间"
     "够长（超过 0.5 秒）猫能完成翻正并**伸展四肢增大风阻**达到终端速度后放"
     "松（未证实但有「缓降假说」）。**重要提醒**：猫不是摔不死——高楼坠落伤"
     "（「高层综合征」）常见骨折/气胸/内脏伤，死亡率不低；**养猫家庭必须封窗"
     "封阳台**（发情/捕鸟冲动下坠楼高发），勿抱侥幸心理。",
     ["猫为什么摔不死", "猫的正位反射", "猫从楼上掉下来会死吗",
      "高层综合征", "养猫为什么要封窗"],
     ["问猫的绝育与健康", "问其他动物夜视/平衡能力"],
     "atomic", "",
     "猫摔不死=正位反射（内耳+柔韧脊柱 0.1 秒翻正）+肉垫减震+体小压强分散；趣闻=7 层以上受伤率反降（缓降假说）；但高层综合征骨折气胸死亡率不低——养猫必须封窗封阳台。"),
    ("kp_card_porthole",
     "飞机舷窗为什么是圆的",
     "基础科学知识点内容（人话接口）", "物理学",
     "舷窗圆形/圆角的原因=**应力集中**管理：①客舱是**增压舱**（巡航时舱内气"
     "压≈海拔 2400 米而舱外≈万米高空），每一次起降窗框都要承受一次**压差循环"
     "载荷**；②**方窗的直角是应力集中点**——压力在尖角处放大数倍，反复循环会"
     "萌生疲劳裂纹并扩展；③血的教训：**1954 年英国「彗星」客机（de Havilland "
     "Comet，世界首款喷气客机）连续两架空中解体**——事后残骸水槽实验复现："
     "裂纹正是从方形舷窗**铆钉孔直角处**萌生的金属疲劳扩展所致。此后航空器舷"
     "窗一律**圆形或大圆角**（裂纹绕开尖角不易扩展），舱门/检修口也用圆角+止"
     "裂设计。工程格言：「**细节决定安全**」——一个圆角救了整个喷气航空业。",
     ["飞机窗户为什么是圆的", "应力集中是什么", "彗星客机空难",
      "疲劳裂纹", "舷窗设计"],
     ["问飞机安全问题", "问材料力学入门"],
     "atomic", "",
     "舷窗圆=增压舱压差循环载荷下方窗直角应力集中易萌生疲劳裂纹——1954 彗星客机两连坠的事故根源；圆角让裂纹绕行不易扩展，舱门同理；一个圆角救了喷气航空业——细节决定安全。"),
]

QUESTIONS = [
    ("QB-750", "「春困秋乏」有没有科学道理？出现什么情况就不是单纯的春困了？", "生活常识", "技术直答",
     ["血管扩张", "供血", "褪黑素", "生理", "适应", "就医"], "通识拓展165"),
    ("QB-751", "猫从高处坠落为什么常常能幸存？养猫家庭为什么要封窗？", "生物学", "技术直答",
     ["正位反射", "翻正", "内耳", "肉垫", "封窗", "高层综合征"], "通识拓展165"),
    ("QB-752", "飞机舷窗为什么设计成圆形？历史上哪起空难与方形舷窗有关？", "物理学", "技术直答",
     ["应力集中", "增压", "疲劳裂纹", "彗星", "圆角"], "通识拓展165"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    whitelist = {"Havilland"}  # 正当专名（de Havilland 彗星客机制造商）
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
                               "level:L2", "status:verified", "batch:通识拓展165"],
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
    bank["version"] = "v4.38"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
