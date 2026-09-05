# -*- coding: utf-8 -*-
"""seed_common_146_cards.py · 通识拓展批次146知识卡+题库（幂等）

146：生活常识-发票常识/地理学-海绵城市/历史学-玄武门之变
KCCS 四要素+题干原句触发词。三重预检：发票老卡=会计凭证角度（实用角度未覆
盖）、海绵城市=水循环卡仅涉水系、玄武门=tangfound 仅提唐建立。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_invoice",
     "发票的实用常识",
     "生活常识知识点内容（人话接口）", "生活常识",
     "发票三用途=消费凭证+**报销凭证**+维权证据（「无发票难维权」）。①**普"
     "票 vs 专票**：增值税**普通发票**——个人消费都能开（餐饮/网购/打车，抬头"
     "写个人或单位）；增值税**专用发票**——只有一般纳税人企业用于抵扣进项税"
     "额，个人拿专票没用；②**抬头**=购买方名称——单位报销必须开**单位全称+"
     "纳税人识别号（税号）**，抬头开错只能作废重开（当场核对）；③**电子发票"
     "**——与纸质发票同等法律效力，从邮箱/平台下载 PDF 存档防丢；④商家拒开"
     "发票是违法的（「不开票送饮料」也是违规）——可打 **12366** 纳税服务热线"
     "投诉；⑤发票内容要真实——「虚开发票」（开与实际交易不符的品名金额）是"
     "违法行为。",
     ["发票抬头是什么意思", "普票和专票的区别", "电子发票有法律效力吗",
      "商家不给开发票怎么办", "报销发票抬头写什么", "12366是什么电话"],
     ["问会计记账流程（用会计凭证卡）", "问税务筹划"],
     "atomic", "",
     "发票=消费+报销+维权三凭证；普票人人可开/专票企业抵税用；报销抬头须单位全称+税号当场核对；电子发票同等效力存 PDF 防丢；拒开发票违规打 12366 投诉；虚开发票违法。"),
    ("kp_card_spongecity",
     "海绵城市",
     "人文通识知识点内容（人话接口）", "地理学",
     "**城市内涝**的根源：地面被水泥/沥青**硬化**——雨水下不去，只能全靠下水"
     "道排；短时强降雨超排水能力→「看海」。**海绵城市**=让城市像海绵一样有"
     "**吸水-蓄水-渗水-净水**能力：①**透水铺装**（透水砖/透水沥青让雨水下"
     "渗）；②**下沉式绿地/雨水花园**（比路面低洼，集蓄雨水慢慢下渗）；③蓄水"
     "池/湿地公园（调蓄+净化）；④植草沟引导径流。六字方针「**渗、滞、蓄、"
     "净、用、排**」——优先让雨水渗下去、滞留住、蓄起来、净化后利用，最后才"
     "排放。好处：治内涝+补充地下水+缓解热岛效应+雨水资源化。中国 2015 年启动"
     "试点（武汉/遂宁/庄河等）。对比：传统「快排」模式 vs 海绵「就地消纳」。",
     ["海绵城市是什么意思", "城市为什么会内涝", "透水铺装是什么",
      "渗滞蓄净用排", "雨水花园", "海绵城市试点"],
     ["问具体城市工程案例", "问地下管网改造"],
     "atomic", "",
     "内涝根=硬化地面不透水只靠管网排；海绵城市=透水铺装+下沉绿地/雨水花园+蓄水池湿地，六字方针渗滞蓄净用排（先消纳后排）；兼治内涝+补地下水+缓热岛；2015 起中国试点。"),
    ("kp_card_xuanwumen",
     "玄武门之变",
     "人文通识知识点内容（人话接口）", "历史学",
     "玄武门之变：**公元 626 年**（武德九年）七月初二，秦王**李世民**在长安太"
     "极宫**玄武门**设伏，射杀太子**李建成**、齐王**李元吉**（兄弟相残），随"
     "后唐高祖李渊立李世民为太子、不久禅位——李世民即位，次年改元**贞观**，"
     "开创「贞观之治」。背景：唐朝建立后太子与秦王两大集团争斗加剧（太子建成的东宫势力与李世民的功臣集团），先发制人成为政变直接动因。历史评价：手段"
     "残酷（杀兄逼父），但即位后李世民虚心纳谏（魏征）、轻徭薄赋、完善科举，"
     "成就中国历史上的治世典范——「以铜为镜可以正衣冠，以史为镜可以知兴替」"
     "即出自其与魏征的君臣故事。",
     ["玄武门之变发生在哪一年", "李世民杀的是谁", "贞观之治的皇帝",
      "魏征进谏", "唐朝怎么建立的", "玄武门之变的评价"],
     ["问安史之乱（唐朝由盛转衰）", "问武则天称帝"],
     "atomic", "",
     "玄武门之变=626 年李世民伏杀太子李建成+齐王李元吉、李渊禅位；次年改元贞观→虚心纳谏(魏征)+轻徭薄赋+完善科举=贞观之治；手段残酷但治世典范——「以史为镜知兴替」。"),
]

QUESTIONS = [
    ("QB-699", "报销发票的抬头应该写什么？普通发票和专用发票有什么区别？", "生活常识", "技术直答",
     ["单位全称", "税号", "抵扣", "普通发票", "专用发票"], "通识拓展146"),
    ("QB-700", "海绵城市是怎么应对城市内涝的？「渗滞蓄净用排」是什么意思？", "地理学", "技术直答",
     ["透水", "下渗", "蓄水", "雨水花园", "绿地"], "通识拓展146"),
    ("QB-701", "玄武门之变发生在哪一年？事变后谁即位开创了贞观之治？", "历史学", "技术直答",
     ["626", "李世民", "李建成", "贞观"], "通识拓展146"),
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
                               "level:L2", "status:verified", "batch:通识拓展146"],
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
    bank["version"] = "v4.19"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
