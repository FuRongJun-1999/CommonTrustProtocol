# -*- coding: utf-8 -*-
"""seed_common_562_cards.py · 通识拓展批次562知识卡+题库（幂等）

562：2 张新卡·姻缘社神域（月老红线 kp_card_yuelao /
    城隍与土地 kp_card_chenghuang——id 与语义等价卡名双重确认双零）。
预检已过（QB-1918~1920 可用）。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

WHITELIST = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
             "effect", "OR6A2", "ghrelin", "DOMS", "DHT", "frisson",
             "AlphaGo", "CFOP", "Transformer", "LLM", "GPT", "BERT",
             "CYP3A4", "ACID", "CNN", "RNN", "LSTM", "Krebs", "NADH",
             "FADH2", "Vmax", "Km", "RNA", "DNA", "mRNA", "KCL", "KVL",
             "BCS", "B2H6", "borrow", "Rust", "sin", "cos", "tan",
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO", "SVM",
             "MTBF", "SQA", "IMC", "HMO", "JD", "STAR", "Word", "offer",
             "XMind", "HDR", "Robotaxi"}


def foreign_word_check(text: str) -> list:
    """西里尔字符一律报警；长英文词(≥4)非白名单报警。只扫中文内容字段。"""
    bad = []
    if re.search(r"[\u0400-\u04FF]", text):
        bad.append("cyrillic:" + re.search(r"[\u0400-\u04FF]+", text).group())
    for w in re.findall(r"[A-Za-z]{4,}", text):
        if w not in WHITELIST:
            bad.append("latin:" + w)
    return bad


NODES = [
    ("kp_card_yuelao",
     "月老红线",
     "民俗信仰知识点内容（人话接口）", "传统文化",
     "月老红线——系在脚上的姻缘：①**典故出处**——唐李复言《续玄怪录"
     "·定婚店》：韦固夜宿遇老人倚囊向月检书，囊中红绳「以系夫妻之足」"
     "，绳一系定，「虽仇敌之家，贵贱悬隔，天涯从宦，吴楚异乡，终不可"
     "逭」；②**韦固不信**——不肯娶老人所指的卖菜瞎眼老妪之女，历经波"
     "折最终还是娶了她，应了前定；③**月老祠**——杭州西湖月老祠香火最"
     "盛，「愿天下有情人终成眷属」的对联挂于祠前；④**俗语**——「千里"
     "姻缘一线牵」；⑤**如今**——月老成了姻缘文化 IP，月老庙求红绳是"
     "婚恋话题的民俗顶流。",
     ["月下老人", "红绳", "定婚店", "千里姻缘一线牵",
      "月老祠", "姻缘"],
     ["问牛郎织女", "问传统婚俗"],
     "atomic", "",
     "月老红线=唐续玄怪录定婚店韦固月下遇老人检婚书囊中红绳系夫妻之足"
     "终不可逭+韦固不信娶菜农女波折后应验前定+西湖月老祠愿天下有情人终"
     "成眷属+千里姻缘一线牵+姻缘文化IP红绳民俗顶流。"),
    ("kp_card_chenghuang",
     "城隍与土地",
     "民俗信仰知识点内容（人话接口）", "传统文化",
     "城隍与土地——最接地气的守护神：①**城隍**——「城」是城墙「隍」"
     "是护城河，城隍即城市守护神；多由对本 地有功的忠臣良将死后充任（"
     "如上海城隍秦裕伯）；明太祖曾大封天下城隍，按府州县分级；②**职能"
     "**——护城池、司阴间、鉴察善恶，城隍庙常是旧时城市社交与庙会中"
     "心；③**土地公**——最基层的地方神，慈眉善目的老者形象，管一方地"
     "面小事，「福德正神」；④**庙会经济**——城隍庙、土地庙的庙会带动"
     "市集（上海城隍庙商圈至今繁华）；⑤**想象**——「阎王好见，小鬼难"
     "缠」把官僚体系投射进了神界。",
     ["城隍", "土地公", "城隍庙", "福德正神",
      "庙会", "守护神"],
     ["问钟馗与门神", "问财神"],
     "atomic", "",
     "城隍土地=城墙护城河城市守护神忠臣良将充任上海秦裕伯+明太祖封天"
     "下城隍府州县分级+护城池司阴间鉴察善恶庙会社交中心+土地公福德正神"
     "基层老者+城隍庙商圈庙会经济+阎王好见小鬼难缠官僚体系投射神界。"),
]

QUESTIONS = [
    ("QB-1918", "「月下老人」的典故出自哪里？红绳有什么寓意？",
     "传统文化", "技术直答",
     ["月下老人", "红绳", "姻缘", "定婚店"], "通识拓展562·新卡"),
    ("QB-1919", "「千里姻缘一线牵」有什么来历？",
     "传统文化", "技术直答",
     ["千里姻缘", "红绳", "月老", "俗语"], "通识拓展562·新卡"),
    ("QB-1920", "城隍是什么神？土地公在民间信仰里是什么角色？",
     "传统文化", "技术直答",
     ["城隍", "土地公", "守护神", "庙会"], "通识拓展562·新卡"),
]


def ensure_seed() -> dict:
    for nid, *_ in NODES:
        conn = sqlite3.connect(DB)
        row = conn.execute("SELECT id FROM nodes WHERE id=?", (nid,)).fetchone()
        conn.close()
        assert not row, f"id 撞车：{nid} 已存在"
    bank = json.load(open(BANK, encoding="utf-8"))
    have = {q["id"] for q in bank["questions"]}
    for qid, *_ in QUESTIONS:
        assert qid not in have, f"QB 撞车：{qid} 已存在"

    all_text = ""
    for n in NODES:
        all_text += n[1] + " " + n[4] + " " + " ".join(n[5]) + " " \
            + " ".join(n[6]) + " " + n[9] + " "
    for q in QUESTIONS:
        all_text += q[1] + " " + " ".join(q[4]) + " "
    bad = foreign_word_check(all_text)
    assert not bad, f"外文词混入：{bad}"

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
                               "level:L2", "status:verified", "batch:通识拓展562"],
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

    qs = bank["questions"]
    added = 0
    for qid, question, domain, qtype, keywords, source in QUESTIONS:
        if qid in have:
            continue
        qs.append({"id": qid, "question": question, "domain": domain,
                   "type": qtype, "keywords": keywords, "source": source,
                   "added": "2026-09-07"})
        added += 1
    bank["version"] = "v8.27"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
