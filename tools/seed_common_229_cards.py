# -*- coding: utf-8 -*-
"""seed_common_229_cards.py · 通识拓展批次229知识卡+题库（幂等·两卡精批次）

229：历史学-张居正改革（一条鞭法）/历史学-和珅
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_zhangjuzheng",
     "张居正改革（一条鞭法）",
     "人文通识知识点内容（人话接口）", "历史学",
     "张居正（1525-1582）=明万历朝**内阁首辅**，明代最著名的改革家：①**考成"
     "法**——官员政绩考核制度（立限考事、以事责官），整饬吏治「虽万里外，朝"
     "下而夕奉行」；②**一条鞭法**——把田赋、徭役和其他杂税**合并为一条，折"
     "成银子征收**（按田亩计税）——简化税制、减轻无地贫民负担、让拥有大量土"
     "地的豪强难以逃税，也适应了白银货币化的趋势；③**用将**——重用戚继光镇"
     "蓟门、李成梁镇辽东，边防稳固；④任内国库充盈（太仓存粮可支十年）。**结"
     "局**——1582 年张居正病逝后即被**抄家清算**（改革触动官僚豪强利益，人"
     "亡政息），但一条鞭法的货币化税制影响延续到清代「摊丁入亩」。",
     ["张居正改革", "一条鞭法是什么", "考成法", "张居正是哪个朝代的",
      "万历首辅", "张居正的结局"],
     ["问王安石变法（用变法卡）", "问戚继光（用戚继光卡）"],
     "atomic", "",
     "张居正=明万历首辅改革家：考成法整吏治[朝下夕奉行]+一条鞭法[赋役合并折银征收简化税制抑制豪强]+用戚继光镇边，国库充盈太仓支十年；1582 病逝后被抄家清算人亡政息——一条鞭法货币税制影响延至清代摊丁入亩。"),
    ("kp_card_heshen",
     "和珅",
     "人文通识知识点内容（人话接口）", "历史学",
     "和珅（1750-1799）=清乾隆朝权臣、**中国历史上著名的巨贪**：①**发迹**——"
     "出身满洲正红旗，仪表堂堂精通满汉蒙藏四种语言，因善迎合乾隆而快速升迁"
     "（军机大臣+户部/吏部/内务府总管，权倾朝野二十余年）；②**贪腐规模**——"
     "卖官鬻爵、结党营私、经营商业（当铺/银号/粮店），1799 年乾隆死后嘉庆帝"
     "迅速**抄家**：查抄财产估值约 **8-11 亿两白银**（一说相当于清政府十余年"
     "财政收入）——民谚「**和珅跌倒，嘉庆吃饱**」；③**意义与警示**——和珅"
     "案是清代由盛转衰的缩影；「和珅现象」成为制度性腐败的代名词。注意与「纪"
     "晓岚/刘墉斗和珅」的影视剧演绎区分（多為艺术加工）。",
     ["和珅是怎么倒台的", "和珅跌倒嘉庆吃饱", "和珅有多少家产",
      "和珅是哪个皇帝时期的", "历史上最大的贪官", "嘉庆抄和珅家"],
     ["问乾隆朝历史", "问清代吏治"],
     "atomic", "",
     "和珅(1750-1799)=乾隆宠臣权倾朝野二十余年：精通四种语言但卖官鬻爵经营商业贪腐巨万；嘉庆即位后迅速抄家查抄约 8-11 亿两白银[相当于清政府十余年财政收入]——「和珅跌倒嘉庆吃饱」；清代由盛转衰缩影+制度性腐败代名词。"),
]

QUESTIONS = [
    ("QB-884", "张居正推行的「一条鞭法」主要内容是什么？他辅佐的是哪位皇帝？", "历史学", "技术直答",
     ["万历", "一条鞭法", "赋役", "折银", "考成法"], "通识拓展229"),
    ("QB-885", "「和珅跌倒，嘉庆吃饱」这句话说的是什么事件？和珅是哪个皇帝时期的宠臣？", "历史学", "技术直答",
     ["乾隆", "抄家", "嘉庆", "贪", "8亿"], "通识拓展229"),
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
                               "level:L2", "status:verified", "batch:通识拓展229"],
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
                   "added": "2026-09-06"})
        added += 1
    bank["version"] = "v5.00"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
