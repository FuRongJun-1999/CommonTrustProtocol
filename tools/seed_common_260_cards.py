# -*- coding: utf-8 -*-
"""seed_common_260_cards.py · 通识拓展批次260知识卡+题库（幂等）

260：建筑-福建土楼的聚居智慧/历史-地道战的战争智慧
KCCS 四要素+题干原句触发词。预检已过（QB-971/972+双id可用）。
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
             "AlphaGo", "CFOP"}


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
    ("kp_card_tulou",
     "福建土楼的聚居智慧",
     "建筑人文知识点内容（人话接口）", "地理学",
     "福建土楼为什么这样建：①**是什么**——闽西南山区客家/闽南人的大型夯土"
     "集体住宅，圆形或方形，直径可达 70 余米、高 4-5 层，一座楼住几百人"
     "（承启楼最多时 600+ 人）；②**防御刚需**——历史上迁居山区的客家人"
     "面对匪患械斗，外墙夯土厚达 1-2 米，底层不开窗，一二层对外无窗或射击"
     "孔，只有三四层开小窗——「易守难攻」的堡垒式民居；③**聚族而居**——"
     "圆楼内一圈套一圈：祖堂居中，住房环列，体现宗族平等向心（各户房间大小"
     "朝向均等）；④**材料智慧**——就地取材：生土+砂+石灰+竹木墙骨夯筑，"
     "冬暖夏凉，抗震耐久（数百年不倒）；⑤**世界认可**——2008 年福建土楼"
     "46 处列入世界遗产；美国曾误判卫星照片为「导弹发射井」的流传轶事即指"
     "其外形奇特。",
     ["福建土楼为什么是圆的", "土楼是干什么用的", "客家人土楼",
      "土楼能住多少人", "土楼世界遗产", "承启楼"],
     ["问客家迁徙史", "问夯土建筑工艺"],
     "atomic", "",
     "土楼=闽西南客家夯土集体住宅(直径70余米高4-5层住数百人·承启楼600+)+"
     "防御(墙厚1-2米底层无窗射击孔)+聚族而居祖堂居中房均等+生土砂石灰"
     "竹木夯筑冬暖夏凉数百年+2008年46处世遗。"),
    ("kp_card_tunnelwar",
     "地道战的战争智慧",
     "历史知识点内容（人话接口）", "历史",
     "冀中地道战：①**背景**——抗日战争时期冀中平原无山可依，日军「扫荡」"
     "「三光政策」下华北军民的地道隐蔽求生与伏击工事；②**演进**——从单口"
     "「蛤蟆蹲」藏身洞→双口互通→村村相连户户相通的网络化地道（冀中地道"
     "总长约 1.25 万公里），设翻板/陷坑/卡口防毒防水防火防挖掘；③**功能"
     "复合**——藏人藏粮/转移伤员/通信传令/埋伏射击（兼做工事），与高房"
     "工事、地堡构成「天地阴」三防体系；④**代表**——河北清苑冉庄地道战"
     "遗址保留完整（十字街口古槐与老母鸡坨工事为标志）；⑤**局限**——"
     "地道用于防御与袭扰，非主动决战手段；现代影视（1965 年《地道战》）"
     "使其成为家喻户晓的全民抗战符号。",
     ["地道战是怎么回事", "地道战在哪个省", "冉庄地道战",
      "地道怎么防水防毒", "地道战的发明"],
     ["问地雷战", "问平原游击战战术"],
     "atomic", "",
     "地道战=冀中平原抗战无山可依的地道工事+从蛤蟆蹲演进到村村相通网络"
     "1.25万公里+翻板陷坑卡口防毒防水防火+藏粮转移伏击复合功能+天地阴"
     "三防+冉庄遗址+1965年电影符号化。"),
]

QUESTIONS = [
    ("QB-971", "福建土楼为什么建成圆形？它有什么防御功能？", "地理学", "技术直答",
     ["土楼", "客家", "夯土", "防御"], "通识拓展260"),
    ("QB-972", "地道战是怎么回事？地道怎么防水防毒？", "历史", "技术直答",
     ["地道", "冀中", "防毒", "翻板"], "通识拓展260"),
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
                               "level:L2", "status:verified", "batch:通识拓展260"],
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
    bank["version"] = "v5.31"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
