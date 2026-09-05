# -*- coding: utf-8 -*-
"""seed_common_134_cards.py · 通识拓展批次134知识卡+题库（幂等）

134：生活常识-人民币防伪/生活常识-电梯安全与困梯自救/地理学-潮汐现象
KCCS 四要素+题干原句触发词。出卡前三重预检（题库关键词+卡库 id+卡库内容），
既有卡仅「提及」非「主题覆盖」的判定为本批次选题依据。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_rmbsecurity",
     "人民币防伪特征识别",
     "生活常识知识点内容（人话接口）", "生活常识",
     "识别真假人民币看五处（以 2019 版第五套为例）：①**光彩光变面额数字**——"
     "垂直观察呈金色/品红色，倾斜时颜色变化且有光带滚动（假币多为普通油墨）；"
     "②**水印**——透光可见毛泽东头像水印（层次分明）和面额数字白水印；③**光"
     "变安全线**——票面竖向埋入，晃动时颜色在红/绿间变化，透光可见「RMB+面"
     "额」字样；④**雕刻凹版印刷**——正面的头像、国徽、盲文点和背面主景用手触"
     "摸有明显**凹凸感**（盲人靠触摸识别面额）；⑤**隐形面额数字**——将票面置"
     "于与眼睛接近平行的位置、面对光源斜看可见面额数字。发现假币：个人无权没收"
     "他人钞票，应上交银行鉴定或报警；银行收缴假币会出具《假币收缴凭证》。",
     ["人民币怎么辨别真假", "人民币防伪特征有哪些", "水印怎么看",
      "盲人怎么识别人民币", "安全线变色", "发现假币怎么办"],
     ["问残缺污损人民币兑换（去银行按标准兑换）", "问外币真伪鉴别"],
     "atomic", "",
     "人民币防伪五看=光彩光变数字(倾斜变色+光带)+透光水印(头像+白水印)+光变安全线(晃动红绿变)+雕刻凹版(摸凹凸感·盲文)+隐形面额数字(斜对光看)；假币无凹凸油墨普通；发现假币交银行鉴定/报警，个人无权没收。"),
    ("kp_card_liftsafety",
     "电梯安全与困梯自救",
     "生活常识知识点内容（人话接口）", "生活常识",
     "乘直梯安全：先出后进、不超载（超载报警后退出一人）、儿童由大人牵好。**被"
     "困轿厢怎么办**：①保持冷静——电梯轿厢不是密闭空间，有通风口**不会窒"
     "息**；②按轿厢内**警铃按钮/对讲电话**报警，或拨打 96333 电梯应急处置电"
     "话（看轿厢内标牌）与 119；③**等待专业救援**，切勿强行扒门或爬出天窗——"
     "电梯可能停在两层楼之间（不平层），扒门坠入井道是电梯伤亡的第一大原因；"
     "④不要反复蹦跳（可能加剧故障）。安全常识：电梯有多重保险（限速器/安全钳/"
     "缓冲器），「电梯下坠」多为故障后的平层保护动作。乘扶梯：握扶手、站黄线"
     "内、不倚靠围裙板，发生夹卡立即按出入口红色**急停按钮**。",
     ["被困电梯怎么办", "电梯困人自救方法", "为什么不能扒电梯门",
      "电梯会窒息吗", "96333是什么电话", "扶梯急停按钮在哪"],
     ["问电梯维保周期（物业/市场监管职责）", "问电梯品牌选购"],
     "atomic", "",
     "困梯三步=按警铃/对讲+拨96333/119+等待专业救援；轿厢有通风不会窒息；切勿扒门/爬天窗——不平层坠井道是伤亡主因，蹦跳加剧故障；扶梯夹卡按红色急停钮；电梯有限速器/安全钳/缓冲器多重保险。"),
    ("kp_card_tide",
     "潮汐现象与钱塘江大潮",
     "人文通识知识点内容（人话接口）", "地理学",
     "潮汐=海水周期性涨落现象，成因是**月球引力**为主（太阳引力为辅）——月球"
     "对地球的引潮力使正对侧和背对侧各鼓起一个「潮峰」，地球自转使多数海岸一天"
     "约两次涨潮落潮（半日潮）。**朔望大潮**：农历初一（朔）和十五前后（望），"
     "日月地近似一条直线，引力叠加形成大潮；农历初七八、廿二三（上下弦月）日月"
     "引力互成直角，抵消一部分形成小潮——渔民和赶海都看农历。中国最壮观的潮景"
     "=**钱塘江大潮**（农历八月十八前后最盛）：杭州湾喇叭口地形外宽内窄，潮水"
     "涌入急剧抬升，潮头可达数米。潮汐利用：潮汐发电（清洁可再生）、海洋养殖与"
     "赶海、大型船舶乘潮进港。",
     ["潮汐是怎么形成的", "为什么初一十五涨大潮", "钱塘江大潮什么时候",
      "什么是小潮", "潮汐能可以发电吗", "赶海看什么时间"],
     ["问海啸（海底地震引发，与潮汐无关）", "问具体海域潮汐表"],
     "atomic", "",
     "潮汐=海水周期涨落：月球引力为主太阳为辅，多数海岸一日两涨落（半日潮）；农历初一十五日月同线=大潮（朔望潮），上下弦=小潮；钱塘江大潮农历八月十八最盛（喇叭口地形潮头数米）；利用=潮汐发电/赶海/乘潮进港；海啸是地震波非潮汐。"),
]

QUESTIONS = [
    ("QB-667", "人民币上的水印应该怎么观察？用手摸起来有凹凸感的是什么印刷技术？", "生活常识", "技术直答",
     ["透光", "水印", "雕刻凹版", "凹凸"], "通识拓展134"),
    ("QB-668", "被困在电梯轿厢里应该怎么自救？为什么不能强行扒开电梯门？", "生活常识", "技术直答",
     ["警铃", "求救", "等待", "扒门", "井道", "窒息"], "通识拓展134"),
    ("QB-669", "潮汐主要是由什么天体的引力引起的？为什么农历初一和十五前后会出现大潮？", "地理学", "技术直答",
     ["月球", "引力", "一条直线", "叠加", "朔望"], "通识拓展134"),
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
                               "level:L2", "status:verified", "batch:通识拓展134"],
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
    bank["version"] = "v4.7"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
