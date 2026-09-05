# -*- coding: utf-8 -*-
"""seed_common_151_cards.py · 通识拓展批次151知识卡+题库（幂等·两卡精批次）

151：生活常识-地铁乘车常识/生活常识-电动车骑行安全与头盔
KCCS 四要素+题干原句触发词。三重预检：地铁双库零覆盖；电动车头盔角度
（trafficsign 为标志卡、libattery 为电池卡）未覆盖；铅笔石墨已有覆盖弃选。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_metroguide",
     "地铁乘车常识",
     "生活常识知识点内容（人话接口）", "生活常识",
     "地铁乘坐流程与规矩：①**进站**——安检（包过 X 光机、人过金属门；管制刀"
     "具/易燃易爆/大容量锂电池禁带，活禽宠物一般限带——导盲犬例外）；②**购"
     "票/过闸**——单程票/交通卡/手机 NFC 与乘车码（支付宝微信城市码）刷闸；"
     "同站进出也扣费（部分城市最低票价）；③**候车**——站在黄线（屏蔽门）后"
     "排队，先下后上，勿倚靠屏蔽门；④**乘车**——扶稳坐好，老幼病残孕专座让"
     "座；**勿抢上抢下阻止关门**（夹伤风险+延误全线）；⑤紧急情况——车厢内"
     "紧急对讲/报警按钮联系司机；**非紧急勿动紧急拉手**（隧道内停车更危险）；"
     "⑥**末班车**——各线路时间不同（多在 22:30-23:30 末班），留意换乘站末班"
     "衔接；遗失物品联系地铁客服热线（各地 96165/96100 等）。",
     ["地铁怎么坐", "地铁安检什么不能带", "地铁末班车几点",
      "地铁紧急拉手什么时候用", "地铁乘车码怎么用", "地铁东西丢了怎么办"],
     ["问具体城市线路图", "问地铁建设规划"],
     "atomic", "",
     "地铁=安检(管制刀/易燃/大锂电池禁带·导盲犬例外)+扫码/交通卡过闸(同站进出也扣费)+黄线后排队先下后上+勿挡门抢上；紧急对讲联系司机、非紧急勿拉紧急手(隧道停车更险)；末班 22:30-23:30 留意换乘衔接。"),
    ("kp_card_ebikehelmet",
     "电动车骑行安全与头盔",
     "生活常识知识点内容（人话接口）", "生活常识",
     "电动自行车骑行安全：①**戴头盔**——「**一盔一带**」安全守护行动：正确佩"
     "戴头盔可使事故死亡风险降低 60-70%（头部是电动车事故致死的首要部位）；选"
     "**3C 认证**头盔、系紧扣带（不系=没戴）；②**新国标**车——电动自行车最高"
     "时速 **25km/h**、整车含电池≤55kg、必须有脚踏骑行功能（超标车属机动车"
     "管理范畴需驾照）；③**禁入楼道充电**——电池入户/飞线充电是火灾主因（锂"
     "电池热失控 30 秒内爆燃，烟气致命）——在户外集中充电桩充电；④**骑行规"
     "则**——走非机动车道、不逆行、不闯红灯、不载 12 岁以上人员、不手持接打"
     "电话；路口大货车「内轮差」盲区远离；⑤雨天减速，积水路段防电池进水与打"
     "滑。",
     ["骑电动车要戴头盔吗", "一盔一带是什么", "电动车新国标时速",
      "电动车为什么不能进楼充电", "锂电池入户危害", "电动车走哪个车道"],
     ["问头盔品牌选购", "问电动车驾照法规细节"],
     "atomic", "",
     "电动车安全=一盔一带（3C 头盔系紧扣带降死亡风险 60-70%）+新国标 25km/h≤55kg 有脚踏+电池禁入楼道飞线充电（热失控 30 秒爆燃·户外桩充）+走非机动车道不逆行远离大货车内轮差。"),
]

QUESTIONS = [
    ("QB-712", "坐地铁哪些物品不能通过安检？车厢里的紧急拉手什么情况下才能使用？", "生活常识", "技术直答",
     ["管制刀具", "易燃易爆", "锂电池", "紧急", "隧道"], "通识拓展151"),
    ("QB-713", "骑电动自行车为什么要戴头盔？「一盔一带」指的是什么？电池为什么不能进楼充电？", "生活常识", "技术直答",
     ["头盔", "3C", "25", "新国标", "热失控", "飞线", "楼道"], "通识拓展151"),
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
                               "level:L2", "status:verified", "batch:通识拓展151"],
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
    bank["version"] = "v4.24"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
