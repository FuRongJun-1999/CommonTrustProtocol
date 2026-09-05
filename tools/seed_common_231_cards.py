# -*- coding: utf-8 -*-
"""seed_common_231_cards.py · 通识拓展批次231知识卡+题库（幂等·单卡精批次）

231：生活常识-麦粒肿（针眼）——blooddonor 卡的「针眼」为采血针眼同名异物
判定可做。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_sty",
     "麦粒肿（针眼）",
     "生活常识知识点内容（人话接口）", "生活常识",
     "麦粒肿（俗称「针眼」）=**眼睑腺体的细菌感染**（多为金黄色葡萄球菌）：①"
     "**表现**——眼睑边缘**红肿热痛的硬结**，几天后可能出脓头（「成熟」）；②"
     "**处理**——**热敷**是核心（干净热毛巾每次 10-15 分钟、每天 3-4 次，促"
     "进排脓自愈）+抗生素眼膏；**脓头成熟**后可由医生切开排脓（勿自己挤）；"
     "③**切勿挤压**——面部静脉无瓣膜，挤压可使细菌进入颅内（「危险三角区"
     "」感染可致海绵窦血栓——严重可危及生命）；④**预防**——不用脏手揉眼、"
     "眼部妆卸干净、隐形眼镜清洁到位；反复发作查血糖（糖尿病者易感染）。",
     ["麦粒肿是什么", "针眼怎么处理", "长针眼能挤吗", "麦粒肿热敷",
      "针眼是看了不该看的东西吗", "睑腺炎"],
     ["问霰粒肿区别", "问结膜炎"],
     "atomic", "",
     "麦粒肿（针眼）=眼睑腺体金葡菌感染：红肿热痛硬结可出脓头；处理=热敷 10-15 分钟×3-4 次+抗生素眼膏，脓熟由医生切开；勿挤压——面部静脉无瓣膜挤压可致颅内海绵窦感染；反复发作查血糖；「看了不该看的」是迷信。"),
]

QUESTIONS = [
    ("QB-888", "长「针眼」（麦粒肿）是怎么回事？为什么千万不能用手挤压？", "生活常识", "技术直答",
     ["睑腺炎", "金黄色葡萄球菌", "热敷", "挤压", "颅内", "危险三角"], "通识拓展231"),
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
                               "level:L2", "status:verified", "batch:通识拓展231"],
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
    bank["version"] = "v5.02"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
