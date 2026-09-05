# -*- coding: utf-8 -*-
"""seed_common_126_cards.py · 通识拓展批次126知识卡+题库（幂等）

126：地理学-中国新能源分布/生活常识-电器火灾预防/生活常识-网络成瘾预防/生物学-生物技术的前景与风险
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_newenergydist",
     "中国新能源的分布",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国新能源分布与资源禀赋高度相关：①**风电**——「三北」地区（新疆/甘肃/内"
     "蒙古/河北北部）陆上风资源丰富（靠近冬季风源地）；海上风电集中在东南沿海"
     "（广东/福建/江苏——台风间隙风稳）；②**光伏**——西北（青海塔拉滩/新疆/宁"
     "夏）光照强荒漠广，特高压输电东送；东部分布式屋顶光伏（整县推进）；③**水"
     "电**——西南（长江/雅鲁藏布江/大渡河落差大：三峡/白鹤滩/乌东德）；④**核电"
     "**——沿海（广东大亚湾/浙江秦山/江苏田湾/海南昌江——需大量冷却水+远离内"
     "陆人口密集区）。问题：风光资源在西部、用电负荷在东部——特高压输电（±1100"
     "kV）+储能配套（抽水蓄能/电化学储能）是关键。",
     ["中国风电主要分布在哪里", "中国光伏发电基地", "中国水电集中在哪些河流",
      "中国核电站分布在哪些省份", "特高压输电是什么", "为什么西部适合发展新能源"],
     ["问风光储一体化", "问分布式能源"],
     "atomic", "",
     "中国新能源分布=三北风电+东南海上风电/西北光伏+东部分布式/西南水电(三峡白鹤滩)/沿海核电；资源在西用电在东→特高压+储能是关键。"),
    ("kp_card_elecfire",
     "电器火灾的预防与处置",
     "生活常识知识点内容（人话接口）", "生活常识",
     "电器火灾预防：①不超负荷——插板额定功率有限（一般 2500W），空调+电暖器+"
     "电磁炉同插必过载；②及时更换老化电线（绝缘层开裂发硬）；③人走断电（充电"
     "器/电热毯/小太阳不过夜）；④电动车**不进楼不入户**充电（锂电池热失控 30 秒"
     "爆燃，楼道充电致死案例多发）。电器火灾处置：**先断电**再灭火——断电前不能"
     "用水（水导电会触电）；用干粉灭火器或二氧化碳灭火器；火势大立即撤离报"
     "警 119。消防「四懂四会」：懂火灾危险性、懂预防措施、懂扑救方法、懂逃生方"
     "法；会报警、会使用灭火器、会扑救初起火灾、会逃生自救。",
     ["电器火灾怎么预防", "电动车为什么不能在楼道充电", "电器着火能用水扑灭吗",
      "插板为什么会起火", "电器火灾用什么灭火器", "什么是四懂四会"],
     ["问锂电池火灾特性", "问消防疏散演练"],
     "atomic", "",
     "电器火灾预防=不过载+换老化线+人走断电+电动车不进楼(锂电 30s 爆燃)；处置=先断电禁水泼·用干粉 CO₂；四懂四会；火大撤离 119。"),
    ("kp_card_netaddict",
     "网络成瘾的预防",
     "生活常识知识点内容（人话接口）", "生活常识",
     "网络成瘾（WHO 列入 ICD-11 疾病分类）：无法控制地使用网络，明知危害仍持"
     "续、时间失控优先级压倒其他。危害：视力下降（近视）、睡眠障碍（蓝光抑制褪"
     "黑素）、颈椎腰椎问题、社交能力退化、学业工作受损、抑郁焦虑风险升高。预"
     "防与管理：①时间管理——设定使用时长（手机屏幕使用时间统计）、睡前 1 小时"
     "不用手机；②替代活动——运动/阅读/线下社交；③家长策略——以身作则、共同约"
     "定规则（而非没收）、培养其他兴趣；④游戏防沉迷——未成年人仅周五六日+法定"
     "节假日 20-21 时可玩 1 小时（antiction 呼应）。戒断：循序渐进减量而非一刀"
     "切，必要时寻求心理咨询。",
     ["网络成瘾的危害有哪些", "怎么预防网络成瘾", "手机成瘾怎么戒",
      "蓝光对睡眠的影响", "青少年游戏防沉迷规定", "网络成瘾是疾病吗"],
     ["问多巴胺与即时反馈", "问数字排毒"],
     "atomic", "",
     "网络成瘾(WHO ICD-11)=失控使用压倒其他：危害=近视睡眠颈椎社交抑郁；预防=时间管理(睡前1h不用)+替代活动+家长以身作则共同约定；戒断=渐进减量可求心理咨询。"),
    ("kp_card_biotechrisk",
     "生物技术的前景与风险",
     "基础科学知识点内容（人话接口）", "生物学",
     "现代生物技术双刃剑。**前景**：基因治疗（根治遗传病——CRISPR 修复致病基"
     "因）、精准医疗（基因检测定制方案）、mRNA 技术（新冠疫苗后拓展至癌症治"
     "疗）、合成生物学（人造淀粉/人造蛋白——中科院 CO₂ 合成淀粉 2021）、细胞治"
     "疗（CAR-T 治白血病）。**风险与伦理**：基因编辑婴儿（2018 贺建奎事件——违"
     "反伦理被判刑，生殖系编辑可遗传影响后代）、克隆人（全球禁止生殖性克隆）、"
     "生物武器（禁止生物武器公约）、基因隐私（基因歧视——保险/就业）。原则："
     "「伦理先行、审慎发展」——技术的边界由伦理划定，科学自由不等于无限自"
     "由。中国《生物安全法》2021 年施行。",
     ["生物技术的前景与风险", "基因编辑婴儿为什么被禁止",
      "什么是CRISPR技术", "合成生物学是什么", "中国生物安全法", "CAR-T是什么"],
     ["问基因治疗临床试验", "问生物武器公约历史"],
     "atomic", "",
     "生物技术双刃=前景(基因治疗/精准医疗/mRNA/合成生物 CO₂ 制淀粉/CAR-T)vs 风险伦理(编辑婴儿判刑/克隆人禁止/生物武器/基因隐私)；原则=伦理先行审慎发展；生物安全法 2021。"),
]

QUESTIONS = [
    ("QB-639", "中国风电主要分布在哪里", "地理学", "技术直答",
     ["三北", "东南沿海"], "通识拓展126"),
    ("QB-640", "电器火灾怎么预防", "生活常识", "技术直答",
     ["不超负荷", "断电"], "通识拓展126"),
    ("QB-641", "网络成瘾的危害有哪些", "生活常识", "技术直答",
     ["视力", "睡眠", "社交"], "通识拓展126"),
    ("QB-642", "基因编辑婴儿为什么被禁止", "生物学", "技术直答",
     ["伦理", "可遗传"], "通识拓展126"),
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
                               "level:L2", "status:verified", "batch:通识拓展126"],
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
    bank["version"] = "v4.0"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
