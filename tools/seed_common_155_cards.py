# -*- coding: utf-8 -*-
"""seed_common_155_cards.py · 通识拓展批次155知识卡+题库（幂等）

155：生活常识三连——海姆立克急救法/手机进水处理/流鼻血的正确处理
KCCS 四要素+题干原句触发词。三重预检：三主题双库零覆盖（CPR 卡无海姆立克
内容；烫伤/隔夜菜等候选命中已有覆盖弃选）。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_heimlich",
     "海姆立克急救法",
     "生活常识知识点内容（人话接口）", "生活常识",
     "气道异物梗阻（吃饭说笑呛入食物）的识别：**不能说话/咳嗽/面色青紫、双手"
     "掐脖子「V 形手势」**——此时拍背灌水都无效且危险，立即用海姆立克法。**成"
     "人腹部冲击**（站位）：从背后环抱患者，一手握拳、拳眼置于**肚脐上两横指"
     "（剑突下）**，另一手包住，快速向**内向上**猛力冲击——利用腹压把异物「顶"
     "」出来（口诀「剪刀石头布」：剪刀=定位两指、石头=握拳放定位处、布=另一"
     "手包拳冲击）；**自救**：椅背/桌角对准上腹快速顶压；**孕妇与肥胖者**改胸"
     "部冲击（胸骨下半段）；**1 岁以下婴儿**：禁腹部冲击（伤内脏）——5 次拍背"
     "（头低脚高面朝下）+5 次胸部按压交替。异物排出后仍建议就医（冲击可能伤"
     "内脏）。预防：吃饭不笑闹、幼儿勿食整颗坚果果冻。",
     ["海姆立克急救法怎么做", "被食物噎住怎么办", "气道梗阻的识别",
      "婴儿呛噎怎么急救", "自己被噎住怎么自救", "剪刀石头布定位"],
     ["问心脏骤停 CPR（用心肺复苏卡）", "问溺水急救流程"],
     "atomic", "",
     "海姆立克=气道异物梗阻（不能说话咳嗽+V 形手势）：成人脐上两横指向内上猛冲击（剪刀石头布口诀）/自救椅背顶上腹/孕妇肥胖改胸部冲击/1 岁内婴儿拍背+压胸交替禁腹部冲击；排出后仍就医防内脏伤；预防=吃饭不笑闹。"),
    ("kp_card_phoneinwater",
     "手机进水怎么办",
     "生活常识知识点内容（人话接口）", "生活常识",
     "手机落水四步：①**立即捞出关机断电**（短路是最大杀手——通电状态下进水"
     "会烧主板）；②**擦干表面**、取出 SIM 卡托；③**干燥处理**：放入密封袋+干"
     "燥剂（鞋盒里的硅胶包最佳）**静置 24-48 小时**；④**送修**——拆机清洗检"
     "测最稳妥。**三个「不要」**：❶**不要立即开机/充电测试**（残留水分通电=短"
     "路扩大损伤）；❷**不要用吹风机热风吹**（高温伤元件、还把水汽往里推）；"
     "❸**米缸传说效果很差**（大米间隙粉尘还可能入孔，远不如干燥剂）。另：标"
     "称 IP68 防水（1.5 米 30 分钟）也**不保液体损坏**——多数厂商进水不保修"
     "（防水性能随老化衰减）；海水/奶茶比清水腐蚀性强，尽快淡水冲洗外部（关"
     "机前提下）并送修。",
     ["手机进水了怎么办", "手机进水放米缸有用吗", "进水后能马上充电吗",
      "IP68防水是什么", "手机掉水里第一时间", "吹风机吹手机行吗"],
     ["问官方售后检测", "问数据恢复"],
     "atomic", "",
     "手机进水=立即关机断电+擦干+干燥剂密封袋 24-48h+送修拆洗；三不要=勿开机充电（短路烧主板）/勿热风吹（伤件推水汽）/米缸效果差不如干燥剂；IP68 也不保液体损坏多不保修；海水奶茶腐蚀强尽快送修。"),
    ("kp_card_nosebleed",
     "流鼻血的正确处理",
     "生活常识知识点内容（人话接口）", "生活常识",
     "流鼻血（鼻出血）常见于鼻中隔前下区（黎氏区）黏膜小血管破裂——抠鼻/干"
     "燥/碰撞/擤鼻过猛。**正确做法**：①身体**微微前倾坐低**（不是仰头！）；②"
     "用手指**捏紧两侧鼻翼**（软鼻部分）持续 **10-15 分钟**压迫止血，用嘴呼"
     "吸；③冷敷鼻梁/额头帮助血管收缩；④可用干净棉球/纸巾轻度填塞前鼻孔。**"
     "为什么不能仰头**：仰头血会倒流入咽喉——呛咳误吸（危险）+咽入胃刺激胃"
     "黏膜呕吐，且无法判断出血量（「看起来止住了」其实还在流）。**就医信号**"
     "：压迫 20 分钟不止血、反复频繁出血、外伤后大出血、伴其他部位瘀斑（排查"
     "血液病）——耳鼻喉科可做电凝/填塞。预防：干燥季节鼻腔涂少量凡士林/生理"
     "海水喷雾保湿，勤剪指甲改掉抠鼻习惯。",
     ["流鼻血仰头对吗", "流鼻血怎么处理", "鼻血止不住怎么办",
      "流鼻血要低头还是仰头", "孩子流鼻血", "经常流鼻血查什么"],
     ["问鼻中隔偏曲手术", "问血液病筛查"],
     "atomic", "",
     "流鼻血=黎氏区小血管破裂：前倾坐低+捏紧鼻翼 10-15 分钟+冷敷，可轻填塞；仰头=血流咽喉呛咳误吸+看不出出血量（流传最广的错误！）；20 分钟不止/反复出血/外伤大出血就医；预防=鼻腔保湿+不抠鼻。"),
]

QUESTIONS = [
    ("QB-721", "有人吃饭被食物噎住气道梗阻，怎么识别？海姆立克急救法成人的操作要点是什么？", "生活常识", "技术直答",
     ["V形手势", "不能说话", "肚脐上", "两横指", "向内向上", "冲击"], "通识拓展155"),
    ("QB-722", "手机掉进水里第一时间应该做什么？为什么不能马上开机充电？", "生活常识", "技术直答",
     ["关机", "断电", "短路", "干燥剂", "送修"], "通识拓展155"),
    ("QB-723", "流鼻血时应该仰头还是低头？正确的止血方法是什么？", "生活常识", "技术直答",
     ["低头", "前倾", "捏鼻翼", "10-15分钟", "仰头错误", "呛咳"], "通识拓展155"),
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
                               "level:L2", "status:verified", "batch:通识拓展155"],
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
    bank["version"] = "v4.28"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
