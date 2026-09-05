# -*- coding: utf-8 -*-
"""seed_common_111_cards.py · 通识拓展批次111知识卡+题库（幂等）

111：物理学-电磁铁与电磁继电器/化学-常见物质燃烧的现象/地理学-天气预报
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_electromag",
     "电磁铁与电磁继电器",
     "基础科学知识点内容（人话接口）", "物理学",
     "电磁铁：通电产生磁性的装置——螺线管+软铁芯（磁化增强磁性）。三大优点：①"
     "磁性有无可由电流通断控制；②磁性强弱可由电流大小、线圈匝数调节；③磁极方"
     "向可由电流方向变换。**电磁继电器**是电磁铁的核心应用：利用低电压弱电流电"
     "路的通断，控制高电压强电流工作电路的「自动开关」——人只需操作低压控制电"
     "路就能安全操控高压设备（机床/电梯/电力系统远程控制）。其他应用：电铃（电"
     "磁铁吸引小锤敲铃）、磁悬浮列车、电磁选矿机。影响电磁铁磁性强弱的因素：电"
     "流大小、线圈匝数、有无铁芯（插铁芯磁性大增）。",
     ["电磁铁与电磁继电器", "电磁铁的磁性强弱与什么有关", "电磁继电器的作用",
      "电铃的工作原理", "电磁铁有什么优点", "电磁铁的铁芯为什么用软铁"],
     ["问扬声器原理", "问水位自动报警器"],
     "atomic", "",
     "电磁铁=螺线管+软铁芯：磁性有无由电流控·强弱由电流匝数调·方向由电流向变；电磁继电器=低压控高压的自动开关(机床/电梯/远程)；电铃=电磁铁+小锤。"),
    ("kp_card_burnphen",
     "常见物质在氧气中燃烧的现象",
     "基础科学知识点内容（人话接口）", "化学",
     "常见物质在氧气中燃烧现象对比（中考高频考点）：①木炭——发出白光，生成使"
     "澄清石灰水变浑浊的气体；②硫——明亮的蓝紫色火焰（空气中淡蓝色），生成刺"
     "激性气味气体（SO₂）；③铁丝——剧烈燃烧、**火星四射**，生成黑色固体"
     "（Fe₃O₄），瓶底放水防炸裂；④镁条——剧烈燃烧，发出耀眼白光，生成白色固体"
     "（MgO）；⑤磷——产生大量**白烟**（P₂O₅ 白色固体小颗粒）；⑥蜡烛——发白"
     "光，瓶壁有水雾、生成使石灰水变浑浊的气体。辨析：白烟=白色固体小颗粒（磷燃"
     "烧），白雾=小液滴（水蒸气液化）——「烟是固、雾是液」。火焰是气体燃烧的特"
     "征，铁等固体直接燃烧无火焰只有火星光。",
     ["常见物质在氧气中燃烧的现象", "铁丝在氧气中燃烧的现象", "硫在氧气中燃烧",
      "磷燃烧的白烟是什么", "烟和雾的区别", "镁条燃烧的现象"],
     ["问火焰温度分层复习", "问生成物检验方法"],
     "atomic", "",
     "燃烧现象对比：木炭白光/硫蓝紫火焰刺鼻/铁火星四射黑固(瓶底放水)/镁耀眼白光/磷大量白烟(固粒)/蜡烛白光+水雾；烟=固粒·雾=液滴·火焰=气体燃烧特征。"),
    ("kp_card_weatherfc",
     "天气预报的主要内容",
     "人文通识知识点内容（人话接口）", "地理学",
     "天气预报的主要内容包括：①气温（最高温/最低温）；②风向和风力（风杆风尾符"
     "号——一道风尾 4m/s，风力 0-12 级及 12 级以上）；③降水概率（下雨可能性百"
     "分比）与降水量（mm）；④云量（晴/多云/阴——云量少于 30% 为晴，多于 70% 为"
     "阴）；⑤空气质量、湿度、紫外线指数等生活指数。天气符号：晴☀、多云⛅、阴"
     "☁、雨💧、雷阵雨⚡、雪❄、雾☰。获取渠道：电视/手机 APP/网站（中央气象台"
     "）。数值天气预报原理：超级计算机求解大气运动方程组+卫星雷达地面观测资料同"
     "化——准确率随预报时效延长而下降（3 天内较准，7 天后参考性下降）。「蝴蝶效"
     "应」概念就源于气象预报（洛伦兹）。",
     ["天气预报的主要内容", "风力等级怎么表示", "降水概率是什么意思",
      "晴天多云阴天怎么划分", "天气预报是怎么做出来的", "什么是蝴蝶效应"],
     ["问气象观测站网", "问数值预报模式"],
     "atomic", "",
     "天气预报=气温+风向风力(风尾 4m/s·0-12 级)+降水概率+云量(晴<30%/阴>70%)+生活指数；原理=超级计算机解大气方程+卫星雷达同化；3 天内较准·蝴蝶效应源于此。"),
]

QUESTIONS = [
    ("QB-592", "电磁铁的磁性强弱与什么有关", "物理学", "技术直答",
     ["电流", "匝数", "铁芯"], "通识拓展111"),
    ("QB-593", "铁丝在氧气中燃烧的现象", "化学", "技术直答",
     ["火星四射", "黑色固体"], "通识拓展113"),
    ("QB-594", "天气预报的主要内容", "地理学", "技术直答",
     ["气温", "降水", "风力"], "通识拓展113"),
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
                               "level:L2", "status:verified", "batch:通识拓展111"],
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
    bank["version"] = "v2.7"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
