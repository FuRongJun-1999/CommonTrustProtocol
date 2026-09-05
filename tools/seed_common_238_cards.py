# -*- coding: utf-8 -*-
"""seed_common_238_cards.py · 通识拓展批次238知识卡+题库（幂等）

238：生活常识-晕车晕船的成因与缓解/物理-静电的成因与防护
KCCS 四要素+题干原句触发词。预检已过（QB-901/902+双id可用）。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

WHITELIST = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
             "effect", "OR6A2", "ghrelin", "DOMS", "DHT", "frisson"}


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
    ("kp_card_motionsick",
     "晕车晕船的成因与缓解",
     "生活常识知识点内容（人话接口）", "生活常识",
     "晕车晕船（晕动症）的成因与缓解：①**成因**——内耳前庭器官感知的「运动"
     "信号」与眼睛看到的「静止画面」在大脑里打架（感知冲突理论）——车厢里"
     "看书最容易晕，就是眼睛说静止、前庭说在动的典型冲突；②**座位选择**——"
     "汽车坐前排、飞机坐机翼附近、船坐中部靠后（运动幅度最小的位置）；③"
     "**缓解**——看远处固定物（地平线/远山）让视觉与前庭信号一致、开窗通风"
     "（闷味加重恶心）、生姜片/姜糖（姜辣素抑制恶心反应）、按压内关穴（腕横"
     "纹上三指）；④**晕车药**——需**提前 30-60 分钟服用**才起效（上车再吃"
     "来不及），嗜睡是常见副作用；⑤**预防**——出发前勿过饱过饿、避免油腻、"
     "行车途中不看书手机。",
     ["晕车怎么办", "为什么会晕车晕船", "晕车药什么时候吃",
      "坐车看手机为什么容易晕", "晕船如何缓解", "防止晕车的小妙招"],
     ["问前庭医学手术", "问飞行模拟器眩晕"],
     "atomic", "",
     "晕动症=前庭运动信号与视觉静止画面冲突→坐前排/机翼/船中部+看远处固定"
     "点+通风+生姜+内关穴+晕车药提前 30-60 分钟服（嗜睡副作用）+途中不看"
     "书手机。"),
    ("kp_card_static1",
     "静电的成因与防护",
     "物理通识知识点内容（人话接口）", "基础科学",
     "静电现象的成因与防护：①**成因**——摩擦起电的本质是**电子转移**：两种"
     "材料摩擦时，对电子束缚弱的材料失电子带正电，强的得电子带负电（并非"
     "「摩擦生电」，而是电子本来就存在只是换了主人）；②**冬天更明显**——"
     "干燥空气是绝缘体，电荷积聚不泄露；夏天湿度大，水汽导走电荷，所以夏季"
     "少有噼啪火花；③**放电刺痛**——人体积聚的电荷瞬间通过小接触点释放"
     "（电压可达数千伏但电量和功率极小，对人是安全的）；④**防护**——开门"
     "前先摸钥匙/墙壁（用钥匙尖端放电，痛感转移）、加湿器保持湿度 40-60%、"
     "穿棉质衣物（化纤最易积电）、防静电手环（电子装配行业必备——保护精密"
     "元件而非人）；⑤**安全警示**——加油站严禁拍打化纤衣物（静电火花可点燃"
     "汽油蒸气）。",
     ["冬天为什么容易有静电", "静电是怎么产生的", "防止静电的小妙招",
      "被静电电到怎么回事", "为什么加油站不能拍打衣服", "摸墙壁能防静电吗"],
     ["问工业防静电标准", "问雷电形成机制"],
     "atomic", "",
     "静电=摩擦电子转移(非生电)+冬季干燥电荷积聚(水汽导电故夏天少)+数千伏"
     "但电量小安全+防护(先摸钥匙墙/加湿/棉衣/防静电手环保元件)+加油站严禁"
     "拍化纤(火花燃汽油蒸气)。"),
]

QUESTIONS = [
    ("QB-901", "为什么会晕车晕船？晕车药应该什么时候吃？", "生活常识", "技术直答",
     ["前庭", "视觉", "冲突", "提前", "30"], "通识拓展238"),
    ("QB-902", "冬天为什么容易起静电？静电是怎么产生的？怎么防护？",
     "基础科学", "技术直答",
     ["摩擦", "电子", "干燥", "加湿"], "通识拓展238"),
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
                               "level:L2", "status:verified", "batch:通识拓展238"],
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
    bank["version"] = "v5.09"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
