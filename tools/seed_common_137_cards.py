# -*- coding: utf-8 -*-
"""seed_common_137_cards.py · 通识拓展批次137知识卡+题库（幂等）

137：历史学-五四运动/生活常识-运动损伤RICE处理/文学-中国四大民间传说
KCCS 四要素+题干原句触发词。三重预检通过（五四与新民主主义定义卡/文学革命卡
三方划界；RICE 与关节卡仅提及划界；四大民间传说双库零覆盖）。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_may4th",
     "五四运动",
     "人文通识知识点内容（人话接口）", "历史学",
     "五四运动：**1919 年 5 月 4 日**爆发于北京。**导火索**=巴黎和会上中国外交"
     "失败——列强无视中国战胜国地位，把德国在山东的权益转让给日本。口号：「外"
     "争主权，内除国贼」「誓死力争，还我青岛」。过程：学生是先锋（罢课游行火"
     "烧赵家楼）；**6 月 3 日后**上海工人罢工声援，工人阶级登上政治舞台，运动"
     "中心由北京转到上海。性质：一场彻底地反帝反封建的爱国运动；**意义**：是"
     "**新民主主义革命的开端**（领导阶级从资产阶级变为无产阶级），促进了马克"
     "思主义在中国的传播及其与工人运动的结合，为 1921 年中国共产党的成立做了"
     "思想上干部上的准备。5 月 4 日被定为**中国青年节**。",
     ["五四运动发生在哪一年", "五四运动的导火索", "巴黎和会外交失败",
      "新民主主义革命开端", "五四运动的意义", "中国青年节的由来"],
     ["问白话文运动（用五四文学革命卡）", "问新民主主义革命定义"],
     "atomic", "",
     "五四运动=1919.5.4 北京爆发，导火索=巴黎和会山东权益转让日本；「外争主权内除国贼」；6.3 后工人登上舞台中心移上海；彻底反帝反封建爱国运动=新民主主义革命开端，促马克思主义传播为建党准备；5.4=青年节。"),
    ("kp_card_sprainice",
     "运动损伤与RICE处理原则",
     "生活常识知识点内容（人话接口）", "生活常识",
     "急性扭伤（脚踝/手腕最常见）48 小时内按 **RICE 原则**处理：①**R**est 休"
     "息——立即停止运动，避免患肢负重；②**I**ce 冰敷——毛巾包裹冰袋敷 15-20"
     " 分钟（勿冰块直接触皮肤防冻伤），间隔 1-2 小时重复；③**C**ompression 加"
     "压——弹性绷带包扎消肿（勿过紧防缺血）；④**E**levation 抬高——患肢抬过"
     "心脏水平助回流。**关键禁忌：48 小时内禁止热敷、揉搓、贴活血化瘀膏药**——"
     "急性期血管破裂出血，热敷揉搓会加重出血肿胀；**48-72 小时后**肿胀稳定改"
     "为热敷，促进淤血吸收。出现畸形/剧痛无法活动/迅速肿胀提示**骨折**，应就地"
     "固定送医，不可乱揉乱动。预防：运动前热身 5-10 分钟+动态拉伸，佩戴护踝护"
     "膝，循序渐进加量。",
     ["脚踝扭伤冰敷还是热敷", "扭伤怎么处理", "RICE原则是什么",
      "扭伤48小时后热敷", "扭伤能揉吗", "运动前为什么要热身"],
     ["问骨折术后康复", "问慢性劳损治疗"],
     "atomic", "",
     "急性扭伤 48h 内 RICE=Rest 制动+Ice 冰敷(15-20 分/毛巾裹)+Compression 加压+Elevation 抬高；禁忌=热敷揉搓活血膏药（加重出血肿胀），48-72h 后才热敷促吸收；畸形剧痛疑骨折就地固定送医；预防=热身+拉伸+护具。"),
    ("kp_card_legends",
     "中国四大民间传说",
     "人文通识知识点内容（人话接口）", "文学",
     "中国四大民间传说（口耳相传的四大爱情故事）：①**牛郎织女**——织女下凡与"
     "牛郎结合被王母拆散，喜鹊七夕搭桥相会——**七夕节**（农历七月初七，乞巧"
     "节）的来源，今称「中国情人节」；②**孟姜女哭长城**——丈夫范喜良被抓修长"
     "城累死，孟姜女千里寻夫哭倒长城——反映秦代徭役之苦；③**梁山伯与祝英"
     "台**——祝英台女扮男装求学与梁山伯同窗三年，被逼嫁后双双化蝶，被誉为"
     "「东方的罗密欧与朱丽叶」，小提琴协奏曲《梁祝》即取材于此；④**白蛇传**——"
     "蛇仙白娘子与许仙断桥相恋，法海干预被镇雷峰塔，杭州西湖断桥、雷峰塔因此"
     "成名。四传说均以反抗封建礼教、追求自由爱情为主题。",
     ["四大民间传说是什么", "牛郎织女和七夕节", "梁祝化蝶",
      "孟姜女哭的什么长城", "白蛇传的断桥在哪里", "东方罗密欧与朱丽叶"],
     ["问西游记等四大名著（用名著卡）", "问聊斋志异"],
     "atomic", "",
     "四大民间传说=牛郎织女(七夕·鹊桥·乞巧节)+孟姜女哭长城(秦徭役之苦)+梁祝(化蝶·东方罗密欧朱丽叶·小提琴协奏曲)+白蛇传(断桥借伞·雷峰塔)；共同主题=反抗礼教追求自由爱情，均口头流传成非遗。"),
]

QUESTIONS = [
    ("QB-676", "五四运动发生在哪一年？它的导火索是什么事件？", "历史学", "技术直答",
     ["1919", "巴黎和会", "外交失败", "山东"], "通识拓展137"),
    ("QB-677", "脚踝扭伤后 48 小时内应该冰敷还是热敷？为什么不能揉搓伤处？", "生活常识", "技术直答",
     ["冰敷", "48", "热敷", "出血", "肿胀", "揉"], "通识拓展137"),
    ("QB-678", "中国四大民间传说分别是什么？七夕节与哪个传说有关？", "文学", "技术直答",
     ["牛郎织女", "孟姜女", "梁祝", "梁山伯", "白蛇", "七夕"], "通识拓展137"),
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
                               "level:L2", "status:verified", "batch:通识拓展137"],
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
    bank["version"] = "v4.10"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
