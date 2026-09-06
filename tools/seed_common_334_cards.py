# -*- coding: utf-8 -*-
"""seed_common_334_cards.py · 通识拓展批次334知识卡+题库（幂等）

334：文化-昆曲百戏之祖/文化-京剧脸谱艺术
KCCS 四要素+题干原句触发词。预检已过（QB-1241/1242+双id可用）。
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
             "Dijkstra", "Bellman", "Floyd", "logV"}


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
    ("kp_card_kunqu2",
     "昆曲：百戏之祖",
     "非遗艺术知识点内容（人话接口）", "文化",
     "昆曲——600 年的雅音：①**地位**——发源于元末江苏昆山（昆山腔），"
     "明代经魏良辅改革（水磨调）风靡全国，被誉为「百戏之祖/百戏之师」"
     "——京剧/川剧等众多剧种都吸收过昆曲养分；②**特色**——曲调细腻"
     "婉转（一唱三叹「水磨腔」）、文辞典雅（剧本多用诗词）、表演载歌"
     "载舞（无声不歌无动不舞）；③**代表剧目**——《牡丹亭》（汤显祖："
     "「情不知所起，一往而深」杜丽娘柳梦梅生生死死）/《长生殿》/《"
     "桃花扇》（此二剧并称）；④**行当**——生旦净末丑，闺门旦与巾生"
     "是昆曲标志性美学；⑤**传承危机与复兴**——民国几乎绝响（「传」字"
     "辈艺人苦撑），2001 年入选联合国首批人类口头与非物质遗产代表作"
     "（全票通过），白先勇青春版《牡丹亭》让年轻人重新走进剧场。",
     ["昆曲是什么", "昆曲为什么叫百戏之祖", "牡丹亭是谁写的",
      "水磨调", "昆曲非遗", "青春版牡丹亭"],
     ["问越剧黄梅戏", "问曲牌体"],
     "atomic", "",
     "昆曲=元末昆山腔明魏良辅水磨调改革风靡+百戏之祖诸剧种吸收养分+"
     "曲调婉转文辞典雅载歌载舞+牡丹亭汤显祖情不知所起+长生殿桃花扇"
     "+传字辈苦撑+2001联合国首批非遗+青春版牡丹亭复兴。"),
    ("kp_card_lianpu",
     "京剧脸谱艺术",
     "非遗艺术知识点内容（人话接口）", "文化",
     "京剧脸谱的「密码」：①**功能**——以夸张的色彩与图案揭示角色性格"
     "品质（「寓褒贬，别善恶」），观众一眼识忠奸；②**颜色密码**——红色"
     "=忠义（关羽）、黑色=刚直（包拯/张飞）、白色=奸诈（曹操）、蓝色"
     "=勇猛刚烈（窦尔敦）、金色银色=神仙妖怪；③**谱式**——整脸/三块瓦"
     "脸/十字门脸/碎脸等（图案复杂度对应角色分量）；④**只有净角（花脸"
     "）和丑角勾脸**——生旦多为素面（俊扮），「生旦不勾脸」是惯例；⑤"
     "**不是乱画**——脸谱图案高度程式化（包拯月牙/项羽哭脸/姜维红心"
     "），一代代艺人传承图谱；⑥**现代传播**——脸谱元素进入动漫/文创/"
     "时装设计，成为京剧最外显的文化符号。",
     ["京剧脸谱颜色含义", "红脸白脸黑脸", "曹操为什么是白脸",
      "脸谱的种类", "净角丑角", "包拯脸谱月牙"],
     ["问生旦净丑行当", "问戏服盔头"],
     "atomic", "",
     "脸谱=色彩图案寓褒贬别善恶+红忠义(关羽)黑刚直(包拯张飞)白奸诈"
     "(曹操)蓝勇猛金银神怪+整脸三块瓦十字门碎脸谱式+仅净丑勾脸生旦"
     "俊扮+图案高度程式化传承图谱+动漫文创现代符号。"),
]

QUESTIONS = [
    ("QB-1241", "昆曲为什么被称为「百戏之祖」？代表作有哪些？", "文化", "技术直答",
     ["昆曲", "水磨调", "牡丹亭", "非遗"], "通识拓展334"),
    ("QB-1242", "京剧脸谱的颜色有什么含义？红脸和白脸分别代表什么？", "文化", "技术直答",
     ["红脸", "忠义", "白脸", "奸诈"], "通识拓展334"),
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
                               "level:L2", "status:verified", "batch:通识拓展334"],
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
                   "added": "2026-09-06"})
        added += 1
    bank["version"] = "v6.04"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
