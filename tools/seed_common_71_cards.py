# -*- coding: utf-8 -*-
"""seed_common_71_cards.py · 通识拓展批次71知识卡+题库（幂等）

71：物理学-连通器/化学-碳循环/生物学-泌尿系统/历史-靖康之变
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞——本批预检命中
kp_card_induction（通识拓展07旧卡·电磁感应已覆盖），物理题改连通器。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_communicator",
     "连通器原理",
     "基础科学知识点内容（人话接口）", "物理学",
     "连通器：上端开口、底部连通的容器——**同一种液体静止时，各容器液面总保持"
     "相平**（与容器形状粗细无关）。原理：液体压强只与深度有关（p=ρgh），同一水"
     "平面深度相同则压强相同，若液面不平则会流动直到相平。应用：茶壶（壶嘴与壶"
     "身等高才装得满）、船闸（上下游闸门轮流开关，让船「爬楼梯」过大坝——三峡"
     "五级船闸）、水位计（锅炉/热水器侧面玻璃管显示内部水位）、下水道存水弯（U"
     "形管存水隔臭——隔绝下水道气体）、自动喂水器（养鸡场）。检验倾斜：若液面不"
     "平且液体未动，说明装置不连通或被堵。",
     ["连通器原理是什么", "茶壶嘴为什么要和壶身一样高", "船闸的工作原理",
      "下水道存水弯的作用", "哪些物品利用了连通器", "三峡五级船闸"],
     ["问液体压强公式推导", "问乳牛自动饮水器"],
     "atomic", "",
     "连通器=上开底通：同液静止液面必相平(p=ρgh 同深同压·与形状无关)；应用=茶壶/船闸(船爬楼梯)/水位计/U 形存水弯隔臭/自动喂水器。"),
    ("kp_card_carboncycle",
     "自然界的碳循环",
     "基础科学知识点内容（人话接口）", "化学",
     "碳在自然界循环往复：①光合作用把 CO₂+H₂O 变成有机物（把碳「锁」进植物"
     "体）——碳进入生物群落的主入口；②呼吸作用/动植物尸体分解/燃烧（煤石油天"
     "然气/森林火灾）把碳以 CO₂ 形式释放回大气；③海洋是巨大碳库（CO₂ 溶于水生"
     "成碳酸/碳酸氢盐，也形成贝壳珊瑚的碳酸钙）；④化石燃料是亿万年前的生物碳被"
     "地下封存——人类几百年来大量开采燃烧，把远古的碳快速还回大气，超出自然循环"
     "平衡→大气 CO₂ 浓度从约 280ppm 升到 420ppm+，导致温室效应增强（全球变暖）。"
     "「碳中和」=排放的碳与吸收的碳相抵（减排+植树+碳捕集）。温室气体除 CO₂ 还有"
     "甲烷（牛打嗝/稻田/冻土）、水蒸气等。",
     ["自然界的碳循环", "碳是怎么循环的", "温室效应的原因",
      "什么是碳中和", "化石燃料燃烧对碳循环的影响", "海洋能吸收二氧化碳吗"],
     ["问光合呼吸对比复习", "问碳达峰时间表"],
     "atomic", "",
     "碳循环：光合锁碳入生物·呼吸/分解/燃烧释 CO₂ 回大气·海洋溶碳·化石燃料=远古碳快速归还→CO₂ 280→420ppm 致暖；碳中和=排放与吸收抵消。"),
    ("kp_card_urinary",
     "泌尿系统与尿液的形成",
     "基础科学知识点内容（人话接口）", "生物学",
     "泌尿系统由肾脏（形成尿液）、输尿管（输送）、膀胱（暂存）、尿道（排出）组"
     "成。**肾脏**是形成尿液的器官（左右各一，像两颗蚕豆）：每个肾含约 100 万个"
     "肾单位（肾小球+肾小囊+肾小管）——尿的形成两步：①肾小球过滤：血液流经肾"
     "小球，除血细胞和大分子蛋白质外，水/无机盐/葡萄糖/尿素等滤到肾小囊成「原"
     "尿」（每天约 150 升）；②肾小管重吸收：全部葡萄糖、大部分水和部分无机盐被"
     "重新吸收回血液，剩下的形成尿液（每天约 1.5 升）。肾功能监测指标：尿蛋白"
     "（+号提示肾炎）、血肌酐。喝水多尿多、缺水时尿少色深（抗利尿激素调节）。",
     ["形成尿液的器官是什么", "尿液的形成过程", "什么是肾单位",
      "原尿和尿液的成分区别", "每天产生多少原尿", "尿蛋白阳性说明什么"],
     ["问透析机原理", "问水盐平衡调节"],
     "atomic", "",
     "泌尿=肾(成尿)+输尿管+膀胱+尿道；肾单位≈100 万个/肾：过滤(150L 原尿)→重吸收(葡萄糖全回·水大部回)→尿 1.5L；尿蛋白+=肾炎信号；透析=人工肾。"),
    ("kp_card_jingkang",
     "靖康之变",
     "人文通识知识点内容（人话接口）", "历史",
     "靖康之变（1127 年，靖康二年）：金军攻破北宋都城东京（开封），掳走宋徽宗、"
     "宋钦宗二帝及后妃宗室大臣三千余人北去，北宋灭亡——「靖康之耻」成为汉民族历"
     "史上的深痛记忆（岳飞《满江红》「靖康耻，犹未雪」）。背景：宋徽宗艺术天才"
     "（瘦金体/工笔画）却治国昏聩，联金灭辽（海上之盟）暴露军力虚弱；金灭辽后"
     "南下，两次围攻开封。徽宗闻讯禅位给钦宗仍未能免。后果：康王赵构（钦宗之"
     "弟）南渡即位（宋高宗），定都临安（杭州），史称南宋——「山外青山楼外楼，"
     "西湖歌舞几时休」讽刺偏安；岳飞韩世忠等抗金名将北伐，「直捣黄龙」未竟，岳"
     "飞以「莫须有」冤死于风波亭。",
     ["靖康之变发生在哪个朝代", "靖康之耻掳走了谁", "北宋是怎么灭亡的",
      "南宋是谁建立的", "岳飞满江红靖康耻", "瘦金体是谁创的"],
     ["问岳飞北伐始末", "问宋金和议条款"],
     "atomic", "",
     "靖康之变 1127：金破开封掳徽钦二帝·北宋亡；徽宗瘦金体治国昏聩·联金灭辽自weak；赵构南渡建南宋(临安)；岳飞「靖康耻犹未雪」·莫须有冤死风波亭。"),
]

QUESTIONS = [
    ("QB-417", "连通器原理是什么", "物理学", "技术直答",
     ["液面相平"], "通识拓展71"),
    ("QB-418", "温室效应的原因", "化学", "技术直答",
     ["二氧化碳", "碳循环"], "通识拓展71"),
    ("QB-419", "形成尿液的器官是什么", "生物学", "技术直答",
     ["肾脏"], "通识拓展71"),
    ("QB-420", "靖康之变发生在哪个朝代", "历史", "技术直答",
     ["北宋"], "通识拓展71"),
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
                               "level:L2", "status:verified", "batch:通识拓展71"],
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
    bank["version"] = "v1.63"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
