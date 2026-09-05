# -*- coding: utf-8 -*-
"""seed_common_157_cards.py · 通识拓展批次157知识卡+题库（幂等）

157：生活常识-装修甲醛/历史学-三省六部与行省制/生活常识-旧手机数据安全
KCCS 四要素+题干原句触发词。三重预检：甲醛在变异卡仅列举一句（装修主题未
覆盖）、三省六部+行省制度演变链零覆盖、旧手机数据安全零覆盖。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_formaldehyde",
     "装修甲醛与新房入住",
     "生活常识知识点内容（人话接口）", "生活常识",
     "甲醛从哪来：**人造板材**（颗粒板/密度板）的黏合剂**脲醛树脂**是最大源——"
     "释放周期长达 **3-15 年**（不是通风几个月就没了）；油漆涂料/布艺家具也"
     "有贡献。危害：刺激眼鼻咽喉（流泪咳嗽）、致敏，WHO 列为**一类致癌物**（"
     "与鼻咽癌/白血病风险相关，儿童更敏感）。**治理**（按有效性排序）：①**持"
     "续通风**=最有效最便宜（开窗对流+大风扇增强）；②**新风系统/空气净化器**"
     "（选带活性炭滤网的 CADR 值够大机型）；③活性炭包辅助（**易吸附饱和需定"
     "期暴晒或更换**）；④绿植（绿萝吊兰）作用微乎其微——摆心理安慰可以，靠"
     "它除醛不行。**技巧**：夏季高温高湿甲醛释放最快——「高温闷放（关窗闷几"
     "小时）+开窗强排」交替比一直开窗更高效。**入住标准**：请**CMA 资质**机构"
     "检测（国标 GB/T 18883 关闭门窗 12h 后甲醛≤0.08mg/m³），孕妇儿童家庭宁"
     "严勿松。市面上「零甲醛板材」=甲醛释放量极低而非没有。",
     ["装修甲醛怎么除", "新房通风多久能住", "甲醛释放期是多久",
      "绿萝除甲醛有用吗", "甲醛检测标准", "活性炭除甲醛要晒吗"],
     ["问苯系物与 TVOC（其他污染物）", "问除醛公司治理效果评估"],
     "atomic", "",
     "装修甲醛=板材脲醛树脂缓释 3-15 年（一类致癌物·儿童敏感）；治理序=持续通风最有效>新风/活性炭滤网净化器>活性炭包(饱和需晒)>绿植微乎其微；高温闷放+通风交替更高效；入住认 CMA 检测≤0.08mg/m³，零甲醛=低释放非没有。"),
    ("kp_card_threedepts",
     "三省六部与行省制",
     "人文通识知识点内容（人话接口）", "历史学",
     "中国古代政治制度两条主线：**中央（三省六部制）**——隋文帝初创、唐完善："
     "**中书省**起草诏令→**门下省**审核封驳→**尚书省**执行，尚书省下设**六"
     "部**（吏=官员、户=财政户籍、礼=科举礼仪、兵=军事、刑=司法、工=工程）"
     "——把相权一分为三，分工制衡又互相配合，加强皇权+减少决策失误（「三省"
     "分权」类似近代分权雏形但目的不同）。**地方（行省制度）**——元朝疆域空"
     "前，首创**行中书省**（行省）作为地方最高行政区：「行省」=行动中的中书省"
     "，中央派出机构地方化——**今日中国「省」的名称与区划渊源即此**（沿用至"
     "今）。后续演变：明废丞相设内阁、清设军机处——皇权达到顶峰。记忆口诀："
     "「隋唐三省分相权，元朝行省管地方；明清内阁军机处，皇权步步到顶峰」。",
     ["三省六部制是哪个朝代", "中书省门下省尚书省的职能", "六部分别管什么",
      "行省制度是哪个朝代", "省的名称由来", "古代丞相权力怎么被分割"],
     ["问科举制度（用科举卡）", "问宦官专权与内阁之争"],
     "atomic", "",
     "三省六部=隋唐创：中书起草→门下审核→尚书执行+六部(吏户礼兵刑工)——分相权强皇权；行省制=元首创「行中书省」=今日「省」之源；明清废丞相设内阁/军机处皇权顶峰——口诀「隋唐三省分相权，元朝行省管地方」。"),
    ("kp_card_olddata",
     "旧手机数据安全",
     "生活常识知识点内容（人话接口）", "生活常识",
     "出旧手机（转卖/送人）前的数据安全清单：①**先备份**——照片通讯录聊天记"
     "录上云或导电脑；②**退出所有账号**——Apple ID（关「查找我的 iPhone」，"
     "否则对方无法激活）/各 App 账号（微信/支付宝/银行——**解绑支付与银行卡**"
     "）；③**「加密后再恢复出厂」**——关键一步：直接恢复出厂在旧机型闪存上数"
     "据仍可能被专业软件恢复；先在设置里**加密手机**再恢复出厂，原数据变成无"
     "法解读的乱码，才能算彻底清除（新机型文件系统加密默认开启，恢复出厂已够"
     "用）；④**SIM 卡与 SD 卡**——取出或销毁（SIM 卡绑定号码与验证码，物理折"
     "断）；⑤回收渠道选**正规以旧换新**（当面清验+要求数据清除承诺），路边摊"
     "「高价回收」可能整机转卖含数据。换机后：改重要账户密码+关注登录提醒。",
     ["旧手机数据怎么彻底清除", "恢复出厂设置数据能恢复吗",
      "卖手机前要做什么", "退出Apple ID为什么重要", "SIM卡怎么处理"],
     ["问数据恢复技术（勿用于违法）", "问二手平台交易流程"],
     "atomic", "",
     "旧机出清=备份→退全部账号（关查找/解绑支付）→加密后再恢复出厂（直接重置旧机数据可被恢复，加密后成乱码）→SIM/SD 取出销毁→正规渠道回收；换机后改重要密码开登录提醒。"),
]

QUESTIONS = [
    ("QB-727", "新装修房子里的甲醛主要来自哪里？甲醛的释放周期一般有多长？", "生活常识", "技术直答",
     ["板材", "脲醛树脂", "黏合剂", "3-15年", "缓释"], "通识拓展157"),
    ("QB-728", "三省六部制中中书省、门下省、尚书省各负责什么？「省」作为行政区名称源于哪个朝代的什么制度？", "历史学", "技术直答",
     ["起草", "审核", "执行", "吏户礼兵刑工", "元朝", "行省"], "通识拓展157"),
    ("QB-729", "出售旧手机前，为什么建议「先加密再恢复出厂设置」而不是直接恢复出厂？", "生活常识", "技术直答",
     ["数据恢复", "加密", "乱码", "闪存", "账号"], "通识拓展157"),
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
                               "level:L2", "status:verified", "batch:通识拓展157"],
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
    bank["version"] = "v4.30"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
