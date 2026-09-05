# -*- coding: utf-8 -*-
"""seed_common_234_cards.py · 通识拓展批次234知识卡+题库（幂等）

234：生活常识-食物中毒的识别与处理/生活常识-溺水自救与岸上施救
KCCS 四要素+题干原句触发词。出卡前三重预检（QB号断言+id查重+主题撞车）已过。
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
    """西里尔字符一律报警；长英文词(≥4)非白名单报警。返回违规列表。"""
    bad = []
    if re.search(r"[\u0400-\u04FF]", text):
        bad.append("cyrillic:" + re.search(r"[\u0400-\u04FF]+", text).group())
    for w in re.findall(r"[A-Za-z]{4,}", text):
        if w not in WHITELIST:
            bad.append("latin:" + w)
    return bad


NODES = [
    ("kp_card_foodpoison",
     "食物中毒的识别与处理",
     "生活常识知识点内容（人话接口）", "生活常识",
     "疑似食物中毒的识别与处理：①**识别特征**——进食后数小时内出现恶心/呕吐/"
     "腹泻/腹痛，**多人同吃同一食物先后发病**是最典型的线索；②**首要措施**——"
     "补水防脱水（口服补液盐或淡盐水**少量多次**，呕吐腹泻流失的水和电解质才是"
     "最大威胁）；③**保留证据**——可疑食物+呕吐物样本冷藏留存，供医院检验定性；"
     "④**就医信号**——血便/持续高烧/剧烈脱水（口干尿少头晕）/意识模糊/呕吐到"
     "无法进水，立即就医；⑤**勿盲目催吐**——昏迷或误服腐蚀性物质时催吐会造成"
     "误吸和二次灼伤，由医生决定；⑥**预防**——生熟分开、食物彻底加热、室温"
     "放置超 2 小时的剩菜慎食（金黄色葡萄球菌等毒素耐热，加热也未必破坏）。",
     ["疑似食物中毒该怎么处理", "吃了变质食物又吐又拉怎么办",
      "食物中毒首要措施是什么", "食物中毒要不要催吐", "多人吃同一食物集体发病"],
     ["问具体细菌种类鉴定", "问慢性食物过敏"],
     "atomic", "",
     "食物中毒=识别(同食同发)+首要补水防脱水+留样供检+重症信号就医(血便/高烧/"
     "脱水/意识模糊)+昏迷腐蚀物勿催吐+预防生熟分开彻底加热。"),
    ("kp_card_drownself",
     "溺水自救与岸上施救",
     "生活常识知识点内容（人话接口）", "生活常识",
     "溺水自救与施救：①**岸上施救三字诀**——叫（大声呼救+拨打 110/120）、伸"
     "（递竹竿树枝拉拽）、抛（抛救生圈/空矿泉水瓶/泡沫板等漂浮物）；**非专业"
     "救援者切勿盲目下水**——溺水者会本能死抱施救者，连环溺亡悲剧多源于此；"
     "②**自救**——保持冷静，头向后仰**仰漂**（口鼻露出水面，四肢放松），勿"
     "挣扎乱扑（耗氧下沉更快）；③**控水法已被弃用**——倒挂控水挤不出肺内的"
     "水，反而延误抢救，救上岸后立即判断呼吸；④**无呼吸立即心肺复苏**——胸外"
     "按压 30 次+人工呼吸 2 次循环，直到专业人员到达；⑤**预防**——不野泳、"
     "不在无救援水域戏水、未成年人勿下水救人（先呼救）。",
     ["有人溺水怎么办", "溺水了如何自救", "落水后怎么自救",
      "岸上如何正确施救溺水者", "溺水救上来要不要控水", "不会游泳落水怎么办"],
     ["问专业潜水救援装备", "问船舶事故救援"],
     "atomic", "",
     "溺水=岸上三字诀(叫伸抛)勿盲目下水+自救仰漂勿挣扎+控水法已弃用延误抢救+"
     "无呼吸立即 CPR(30:2)+未成年人先呼救勿下水。"),
]

QUESTIONS = [
    ("QB-893", "疑似食物中毒该怎么处理？首要措施是什么？", "生活常识", "技术直答",
     ["补水", "脱水", "样本", "就医"], "通识拓展234"),
    ("QB-894", "有人落水溺水，岸上的人应该怎么施救？救上岸后要不要控水？",
     "生活常识", "技术直答",
     ["岸上", "抛", "漂浮物", "勿盲目下水", "控水", "心肺复苏"], "通识拓展234"),
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
                               "level:L2", "status:verified", "batch:通识拓展234"],
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
    bank["version"] = "v5.05"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
