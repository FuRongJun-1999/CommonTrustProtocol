# -*- coding: utf-8 -*-
"""seed_common_147_cards.py · 通识拓展批次147知识卡+题库（幂等）

147：历史学三连——光武中兴/澶渊之盟/杯酒释兵权
KCCS 四要素+题干原句触发词。三重预检：三主题双库零覆盖（三峡/湿地/糖类等
候选命中已有覆盖当场弃选）。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_guangwu",
     "光武中兴",
     "人文通识知识点内容（人话接口）", "历史学",
     "西汉末年王莽篡权建「新」朝，天下大乱。汉室宗亲**刘秀**（汉高祖九世孙）"
     "参加绿林起义起兵，**公元 25 年**称帝，重建汉政权，定都**洛阳**（史称**东"
     "汉**，刘秀即汉光武帝）。治国以「**柔道**」行之：①**释放奴婢**、减轻刑"
     "罚（六道诏令释放奴婢，缓和阶级矛盾）；②**度田令**清查全国土地人口，打"
     "击豪强隐匿田产；③裁并四百多个县、精简官吏；④轻徭薄赋恢复经济。光武帝"
     "在位 33 年（25-57），社会安定、经济恢复，史称「**光武中兴**」。注意时序："
     "西汉→新（王莽）→**东汉**——洛阳在西边长安之东，故称东汉（也称后汉）。",
     ["光武中兴是谁开创的", "刘秀建立东汉", "东汉什么时候建立的",
      "柔道治国", "度田令是什么", "光武帝的政绩"],
     ["问文景之治（西汉）", "问王莽改制细节"],
     "atomic", "",
     "光武中兴=刘秀公元 25 年重建汉室定都洛阳（东汉）：柔道治国=释放奴婢轻刑罚+度田令清土地+裁并四百县+轻徭薄赋，在位 33 年天下安定；时序：西汉→王莽新朝→东汉（洛阳在长安东故称）。"),
    ("kp_card_chanyuan",
     "澶渊之盟",
     "人文通识知识点内容（人话接口）", "历史学",
     "**1004 年**秋，辽（契丹）萧太后与辽圣宗率大军南下深入宋境，直逼澶州（又"
     "名澶渊，今河南濮阳），威胁汴京。朝野震动，**宰相寇准**力排众议（南迁之"
     "议）请**宋真宗**亲征——真宗渡河至澶州前线，宋军士气大振，射杀辽将萧挞"
     "凛。**1005 年**（景德二年元月）双方议和订立「澶渊之盟」：①宋辽约为**兄"
     "弟之国**（宋真宗称萧太后为叔母）；②宋每年送辽**岁币银 10 万两、绢 20 万"
     "匹**（合计 30 万）；③双方以白沟河为界，各守边界，不得交侵。**评价**两"
     "面：岁币是沉重财政负担（屈辱色彩）；但此后**宋辽约 120 年保持和平**，边"
     "境贸易（榷场）繁荣，促进经济文化交融。",
     ["澶渊之盟是哪一年", "寇准和宋真宗亲征", "澶渊之盟的内容",
      "岁币是什么", "宋辽约为兄弟之国", "澶渊之盟的评价"],
     ["问靖康之变（北宋末）", "问岳飞抗金（南宋）"],
     "atomic", "",
     "澶渊之盟=1004 辽军南下逼澶州，寇准力主真宗亲征士气大振，1005 议和：宋辽兄弟之国+岁币银 10 万绢 20 万+划界不侵；此后宋辽约 120 年和平、榷场繁荣——岁币负担与和平红利两面性。"),
    ("kp_card_cupwine",
     "杯酒释兵权",
     "人文通识知识点内容（人话接口）", "历史学",
     "**961 年**（建隆二年），宋太祖**赵匡胤**接受赵普建议，宴请禁军高级将领"
     "**石守信、高怀德**等人：席间叹息自己这个皇帝「终夕未尝安枕」——怕部下"
     "也像当年自己一样被部下「黄袍加身」（960 年陈桥兵变赵匡胤自己就是这么当"
     "上皇帝的）。将领们领悟，次日纷纷称病交出兵权，到地方任闲职、享受富贵—"
     "—**和平解除开国将领兵权**，史称「杯酒释兵权」。后续：解除地方藩镇权力、"
     "文官知州、设转运使收财权，确立**重文轻武**国策（士大夫地位空前）。**影"
     "响两面**：防止了唐末五代以来的兵变循环（宋代无武将篡权），但军队「兵不"
     "识将、将不识兵」，战斗力削弱——与澶渊之盟岁币、靖康之变形成因果链。",
     ["杯酒释兵权是谁", "赵匡胤怎么解除兵权", "黄袍加身是什么典故",
      "重文轻武的国策", "陈桥兵变", "石守信"],
     ["问澶渊之盟（用澶渊卡）", "问王安石变法"],
     "atomic", "",
     "杯酒释兵权=961 宋太祖赵匡胤宴请石守信等禁军将领，以黄袍加身之惧劝其和平交权（自己正是 960 陈桥兵变上位）；确立重文轻武国策——防兵变循环但兵将分离战力削弱，为宋代军事困局伏笔。"),
]

QUESTIONS = [
    ("QB-702", "「光武中兴」是哪位皇帝开创的？他定都哪里、建立的政权史称什么？", "历史学", "技术直答",
     ["刘秀", "光武帝", "洛阳", "东汉"], "通识拓展147"),
    ("QB-703", "澶渊之盟订立于哪一年？盟约中宋每年送给辽的「岁币」包括哪些？", "历史学", "技术直答",
     ["1005", "1004", "银10万两", "绢20万匹", "岁币", "兄弟之国"], "通识拓展147"),
    ("QB-704", "「杯酒释兵权」说的是哪位皇帝的典故？它对宋代国策有什么深远影响？", "历史学", "技术直答",
     ["赵匡胤", "宋太祖", "石守信", "重文轻武"], "通识拓展147"),
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
                               "level:L2", "status:verified", "batch:通识拓展147"],
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
    bank["version"] = "v4.20"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
