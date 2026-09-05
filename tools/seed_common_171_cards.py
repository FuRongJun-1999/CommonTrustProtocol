# -*- coding: utf-8 -*-
"""seed_common_171_cards.py · 通识拓展批次171知识卡+题库（幂等）

171：地理学-降水三类型/数学-抽屉原理/物理学-下雪不冷化雪冷
KCCS 四要素+题干原句触发词。三重预检：降水三类型双库零覆盖（梅雨卡是锋面
雨实例、raindist 卡是分布角度）；抽屉原理/化雪冷零覆盖（喷嚏命中感冒卡弃）。
执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_raintypes",
     "降水的三种主要类型",
     "人文通识知识点内容（人话接口）", "地理学",
     "按空气**抬升原因**分四种降水：①**对流雨**——地面受热强烈，空气对流上"
     "升冷却致雨：赤道地区常年对流雨、温带**夏季午后雷阵雨**（来得猛去得快，"
     "「东边日出西边雨」）；②**地形雨**——湿润气流遇山**被迫抬升**，迎风坡多"
     "雨（世界雨极乞拉朋齐就在迎风坡）、背风坡少雨干燥（「雨影区」）；③**锋"
     "面雨**——**冷暖气团相遇**，暖空气被抬到锋面上冷却凝结：我国东部大部分"
     "降水属此（江淮**梅雨**=冷暖气团在长江流域拉锯形成的准静止锋雨）；④**台"
     "风雨**——热带气旋（台风）带来的狂风暴雨（夏秋季东南沿海）。判别思路："
     "看是什么**把空气抬上去**的——热（对流）/山（地形）/锋面（气团相遇）/气"
     "旋（台风）。",
     ["降水有哪几种类型", "对流雨地形雨锋面雨", "迎风坡为什么多雨",
      "梅雨是怎么形成的", "台风雨", "东边日出西边雨是什么雨"],
     ["问梅雨详情（用梅雨卡）", "问人工降雨原理"],
     "atomic", "",
     "降水按抬升原因四类：对流雨（赤道常年+温带午后雷阵雨）/地形雨（迎风坡多雨背风坡雨影）/锋面雨（冷暖气团相遇·我国东部主体·梅雨=准静止锋）/台风雨；判别=看什么把空气抬上去。"),
    ("kp_card_pigeonhole",
     "抽屉原理",
     "基础科学知识点内容（人话接口）", "数学",
     "**抽屉原理（鸽笼原理）**：把 **n+1** 件物品放进 **n** 个抽屉，必有一个"
     "抽屉里至少 **2** 件。一般形式：kn+1 件物品放 n 个抽屉，必有一个抽屉至少"
     "k+1 件。**经典应用**：①**13 个人中必有两人同月出生**（12 个月=12 个抽"
     "屉）；②**367 人中必有两人同一天过生日**（平年 365+闰年 366 天=最多 "
     "366 个抽屉）；③**从 1-10 中任取 6 个数，必有两个数之和是 11**（配对 "
     "(1,10)(2,9)(3,8)(4,7)(5,6) 只有 5 组，取 6 个数必取全一对）；④任取无限"
     "多只袜子混放黑白色，拿 3 只必有同色一双。**精髓**：它只证明「**存在**"
     "」（保证有），不告诉你**是哪两个/在哪**——这种「不用找出来就确定存在」"
     "的证明方式是数学思维独特之处。物理学史趣闻：能量均分定理曾被称为「抽屉"
     "原理的物理版」。",
     ["抽屉原理是什么", "鸽笼原理", "13个人生日同月", "抽屉原理例题",
      "存在性证明"],
     ["问概率基础（用彩票卡）", "问容斥原理"],
     "atomic", "",
     "抽屉原理=n+1 件放 n 抽屉必有抽屉≥2（一般形式 kn+1→k+1）：13 人必有同月生/367 人必有同天生日/取 6 数必有和 11 的对；只证存在不告诉位置=存在性证明的思维精髓。"),
    ("kp_card_snowmelt",
     "下雪不冷化雪冷",
     "基础科学知识点内容（人话接口）", "物理学",
     "「下雪不冷化雪冷」有真实物理内核：①**下雪时**——水汽**凝华**成雪是**放"
     "热**过程（释放潜热），且下雪常伴随暖湿气流、云层像被子保温，所以体感「"
     "不太冷」；②**化雪时**——雪**熔化要吸收大量热**（熔化热 334 kJ/kg，从周"
     "围空气/地面/物体吸热），把环境温度「抽」下来；③化雪多伴随**晴空辐射+冷"
     "空气控制**，夜间降温剧烈；④融雪使空气**湿度大增**——潮湿空气导热快+衣"
     "物受潮保暖性下降，**体感温度**更低（风一吹像「往骨头里钻」）。所以这句"
     "谚语的正确理解：不是化雪让气温一定更低，而是**熔化吸热+辐射降温+湿冷加"
     "成**三者叠加。对应生活：雪后撒盐融冰——盐降低冰点让雪在零下也能熔化"
     "（熔化吸热还会进一步降温，所以盐冰混合物可做简易冷媒）。",
     ["下雪不冷化雪冷", "化雪为什么冷", "熔化吸热", "雪后为什么更冷",
      "撒盐融冰原理"],
     ["问凝华放热（物态变化）", "问融雪剂危害"],
     "atomic", "",
     "下雪不冷=凝华放热+云层保温；化雪冷=熔化吸热(334kJ/kg 抽环境热)+晴空辐射降温+湿冷导热快体感更低；盐融冰=降冰点+吸热（盐冰简易冷媒）——谚语背后是三重物理叠加。"),
]

QUESTIONS = [
    ("QB-764", "降水按空气抬升原因分为哪几种类型？我国东部的大部分降水属于哪种？", "地理学", "技术直答",
     ["对流雨", "地形雨", "锋面雨", "台风雨", "锋面"], "通识拓展171"),
    ("QB-765", "13 个人中为什么一定至少有两人生日在同一个月？这用了什么数学原理？", "数学", "技术直答",
     ["抽屉原理", "鸽笼", "12", "存在"], "通识拓展171"),
    ("QB-766", "为什么说「下雪不冷化雪冷」？化雪的时候热量从哪里来？", "物理学", "技术直答",
     ["熔化", "吸热", "凝华", "放热", "湿冷", "潜热"], "通识拓展171"),
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
                               "level:L2", "status:verified", "batch:通识拓展171"],
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
    bank["version"] = "v4.44"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
