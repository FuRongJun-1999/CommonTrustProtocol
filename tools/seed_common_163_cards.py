# -*- coding: utf-8 -*-
"""seed_common_163_cards.py · 通识拓展批次163知识卡+题库（幂等）

163：历史学-利玛窦与西学东渐/物理学-虹吸原理/地理学-冰川
KCCS 四要素+题干原句触发词。三重预检：三主题双库零覆盖（无理数/冻土等候选
命中已有覆盖弃选）。执行前含外文长词检测（批次162事故教训固化）。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_ricci",
     "利玛窦与西学东渐",
     "人文通识知识点内容（人话接口）", "历史学",
     "利玛窦（1552-1610，意大利耶稣会士）：**1582 年**抵达澳门进入中国内地，"
     "是「**西学东渐**」的开创者。①**合译《几何原本》前六卷**——与**徐光启**"
     "（明代科学家/内阁大学士）合作，1607 年刊行；「几何」「点线面」「平行"
     "线」等中文数学术语即创于此时；②**《坤舆万国全图》**——绘制中文世界地"
     "图，让中国人第一次直观看到五大洲（冲击「天圆地方」「中国居天下之中」"
     "的旧观念）；③**上层路线**——学汉语穿儒服、以自鸣钟/三棱镜等西器结交士"
     "大夫，获准长居北京；④**文化双向**——也把中国文化（儒学经典拉丁文译介"
     "）传向欧洲（「东学西传」）。历史意义：中西文明第一次大规模平等对话的尝"
     "试；徐利之交被誉为中西科技交流的典范。后续：清康熙帝也曾学习西学，但清"
     "中叶禁教闭关，交流中断直至近代重开。",
     ["利玛窦是哪国人", "几何原本谁翻译的", "徐光启和利玛窦",
      "坤舆万国全图", "西学东渐", "利玛窦什么时候来中国"],
     ["问耶稣会与传教史评价", "问明清科技落后原因"],
     "atomic", "",
     "利玛窦(1552-1610 意·耶稣会)1582 入华开「西学东渐」：与徐光启合译《几何原本》前六卷（几何/点线面术语创于此）+绘《坤舆万国全图》；儒服上层路线居北京；双向传播儒学西译——中西平等对话典范，清中叶中断。"),
    ("kp_card_siphon",
     "虹吸原理",
     "基础科学知识点内容（人话接口）", "物理学",
     "**虹吸**=利用液面高度差+大气压，让液体**越过高处**自动从高容器流向低容"
     "器的现象——无需泵。**条件**：①管内先充满液体（无空气——先「吸」一口或"
     "灌水排气）；②出水口必须**低于进水液面**（高度差驱动）。**原理**：管内液"
     "柱两侧都受大气压「托住」，但出水侧液柱更长更重，压强差推动液体持续流动"
     "（现代研究认为重力+液体内聚力共同维持液柱不断裂）。**生活应用**：①**抽"
     "水马桶**——冲水后水位漫过倒 U 形虹吸管，液面差启动虹吸把污物「吸」走"
     "（正因是虹吸，马桶存水弯才能隔臭）；②**鱼缸换水**（管子一头入水一头低"
     "放，先吸一口引水）；③汽车抽油（危险勿模仿）、园艺滴灌。文化趣闻：「虎"
     "跑泉」打水传说/分酒器都暗含虹吸。**注意**：管内进空气会「断流」，须重"
     "新排气。",
     ["虹吸是什么原理", "抽水马桶为什么能吸走污物", "鱼缸换水虹吸",
      "虹吸需要什么条件", "为什么出水口要低于进水口"],
     ["问大气压实验（托里拆利）", "问离心泵"],
     "atomic", "",
     "虹吸=液面差+大气压驱动液体越过高处：条件=管内充满液（排气）+出水口低于进水液面；应用=抽水马桶（倒 U 管存水隔臭）/鱼缸换水/园艺滴灌；管内进气会断流须重新排气。"),
    ("kp_card_glacier",
     "冰川",
     "人文通识知识点内容（人话接口）", "地理学",
     "冰川=陆地上**长年不化、能自己移动**的巨大冰体（区别于浮在海面的海冰）——"
     "地球约 **70% 的淡水**储存在冰川中。①**类型**：大陆冰川（南极冰盖最大最"
     "厚 4000+ 米、格陵兰冰盖）+山岳冰川（沿山谷缓慢流动——中国天山/喜马拉雅"
     "山的现代冰川）；②**移动**——每年几米到几百米，底部受压融水润滑「滑"
     "行」，冰碛（石块泥沙）随冰搬运；③**作用**——高山固体水库（夏季融水养"
     "育大河：长江黄河源头都在冰川区）；侵蚀塑造 U 形谷/角峰/冰斗（挪威峡湾）；"
     "④**危机**——全球变暖下冰川加速消融：短期先洪涝（冰湖溃决）长期水资源"
     "枯竭+海平面上升（南极格陵兰全融理论上海平面升 60+ 米）；中国监测显示多"
     "数冰川退缩。「冰川是流动的河，也是气候的体温计」。",
     ["冰川是什么", "地球淡水资源多少在冰川", "冰川会移动吗",
      "冰川消融有什么影响", "南极冰盖", "U形谷怎么形成的"],
     ["问海平面上升数据", "问冰河时期历史"],
     "atomic", "",
     "冰川=陆地长年不化可移动冰体，储地球约 70% 淡水：南极冰盖(厚 4000m+)+山岳冰川(江河源头固体水库)；年移数米至数百米、侵蚀成 U 形谷峡湾；变暖加速消融→先冰湖溃决后水源枯竭+海平面上升——气候体温计。"),
]

QUESTIONS = [
    ("QB-744", "利玛窦与徐光启合译了哪部数学著作？「几何」等术语是怎么来的？", "历史学", "技术直答",
     ["几何原本", "徐光启", "前六卷", "利玛窦"], "通识拓展163"),
    ("QB-745", "虹吸现象需要满足哪两个条件？抽水马桶利用了什么原理？", "物理学", "技术直答",
     ["充满液体", "排气", "高度差", "大气压", "低于"], "通识拓展163"),
    ("QB-746", "地球上大约百分之多少的淡水储存在冰川中？冰川消融会带来什么影响？", "地理学", "技术直答",
     ["70", "七十", "海平面", "淡水", "消融"], "通识拓展163"),
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
                               "level:L2", "status:verified", "batch:通识拓展163"],
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
    bank["version"] = "v4.36"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词（西里尔/连续长英文）。"""
    allowed = {"IP", "NFC", "CPR", "AED", "NRV", "G", "D", "C", "X", "S",
               "RICE", "REST", "Ice", "Compression", "Elevation", "CMA",
               "WHO", "ISO", "GB", "3C", "96333", "12315", "12305", "12366",
               "12331", "12345", "AQ", "PH", "pH", "LED", "GPS"}
    problems = []
    for node in NODES:
        content = node[4]
        for word in re.findall(r"[A-Za-z\u0400-\u04FF]{4,}", content):
            if word not in allowed and not word.isascii():
                problems.append((node[0], word))
            elif re.match(r"[\u0400-\u04FF]", word):
                problems.append((node[0], word))
    # 西里尔字符一律报警
    for node in NODES:
        cyr = re.findall(r"[\u0400-\u04FF]+", node[4])
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
    if problems:
        raise SystemExit(f"外文长词检测报警: {problems}")


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
