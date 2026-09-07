# -*- coding: utf-8 -*-
"""seed_common_481_cards.py · 通识拓展批次481知识卡+题库（幂等）

481：3 张新卡·中外现当代文学三连（《简·爱》 kp_card_janeeyre /
    《围城》 kp_card_weicheng / 《活着》 kp_card_tolive）。
预检已过（QB-1678~1680 可用，三主题题库卡库双零）。
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
    ("kp_card_janeeyre",
     "《简·爱》",
     "世界文学知识点内容（人话接口）", "世界文化",
     "《简·爱》——夏洛蒂·勃朗特（英国）1847 年出版的长篇小说：①**故事**"
     "——孤女简·爱历经寄人篱下的童年、洛伍德学校磨砺，到桑菲尔德庄园"
     "任家庭教师，与主人罗切斯特相爱；婚礼上发现他已有疯妻，毅然离开；"
     "历经磨难后回到失明落魄的罗切斯特身边；②**经典宣言**——「我们的"
     "精神是平等的，就仿佛我们都经过坟墓，将同样地站在上帝面前」；③**"
     "主题**——女性自尊、独立与平等的爱情观——爱不是依附；④**地位**"
     "——英国文学史上女性自我意识觉醒的里程碑之作。",
     ["简爱是谁写的", "简爱的作者", "简爱讲了什么",
      "夏洛蒂勃朗特", "简爱的名言", "女性独立文学"],
     ["问呼啸山庄", "问世界名著"],
     "atomic", "",
     "简爱=夏洛蒂勃朗特英国1847年长篇+孤女寄人篱下洛伍德学校桑菲尔德家"
     "庭教师与罗切斯特相爱发现疯妻离去历经磨难回归+宣言我们的精神平等"
     "就仿佛经过坟墓同样站在上帝面前+主题女性自尊独立平等爱情爱非依附+"
     "英国文学女性自我意识觉醒里程碑。"),
    ("kp_card_weicheng",
     "《围城》",
     "中国文学知识点内容（人话接口）", "传统文化",
     "《围城》——钱锺书（1910-1998）1947 年出版的讽刺长篇小说：「新"
     "儒林外史」。①**故事**——留学生方鸿渐买假文凭回国，辗转于爱情、"
     "职场与家庭，处处碰壁——婚姻像「被围困的城堡：城外的人想冲进去，"
     "城里的人想逃出来」；②**艺术特色**——妙喻连珠的讽刺语言（「局部"
     "真理」「科学像杨梅核」式的机智比喻）；③**人物**——方鸿渐（优柔"
     "寡断的知识分子）、苏文纨、唐晓芙、孙柔嘉——三闾大学的职场倾轧"
     "是知识分子众生相；④**地位**——中国现代文学讽刺艺术的巅峰，"
     "「围城心态」成为流行语。",
     ["围城是谁写的", "围城讲什么故事", "钱锺书",
      "围城金句城外的人想冲进去", "方鸿渐", "讽刺小说"],
     ["问鲁迅", "问老舍"],
     "atomic", "",
     "围城=钱锺书1947年讽刺长篇新儒林外史+方鸿渐假文凭爱情职场处处碰"
     "壁+金句婚姻是被围困的城堡城外的人想冲进去城里的人想逃出来+妙喻"
     "连珠三闾大学职场众生相+中国现代讽刺艺术巅峰围城心态成流行语。"),
    ("kp_card_tolive",
     "《活着》",
     "中国文学知识点内容（人话接口）", "传统文化",
     "《活着》——余华 1993 年出版的长篇小说：①**故事**——地主少爷福贵"
     "嗜赌败家，此后历经时代动荡，亲人一个个离他而去（父母/妻子家珍/"
     "儿女/女婿/外孙），最后只剩一头老牛与他相依为命；②**主题**——"
     "「人是为活着本身而活着，而不是为了活着之外的任何事物」——苦难"
     "中的坚韧与生命的尊严；③**风格**——冷静克制的白描叙述，以死亡"
     "写生命，以苦难见温情；④**影响**——张艺谋改编同名电影获国际大"
     "奖，小说被译成多种语言，是中国当代文学输出代表作。",
     ["活着是谁写的", "余华", "活着讲了什么", "福贵",
      "人是为活着本身而活着", "中国当代文学"],
     ["问许三观卖血记", "问张艺谋电影"],
     "atomic", "",
     "活着=余华1993年长篇+福贵嗜赌败家历经动荡亲人相继离世只剩老牛相"
     "依为命+主题人为活着本身而活不是为活着之外任何事物苦难中坚韧与生"
     "命尊严+冷静白描以死亡写生命以苦难见温情+张艺谋改编国际获奖当代"
     "文学输出代表作。"),
]

QUESTIONS = [
    ("QB-1678", "《简·爱》的作者是谁？这部小说表达了怎样的爱情观？",
     "世界文学", "技术直答",
     ["简爱", "夏洛蒂勃朗特", "平等", "独立"], "通识拓展481"),
    ("QB-1679", "《围城》是谁写的？「围城」比喻什么？",
     "文学常识", "技术直答",
     ["围城", "钱锺书", "婚姻", "讽刺"], "通识拓展481"),
    ("QB-1680", "《活着》讲了什么故事？表达了怎样的生命态度？",
     "文学常识", "技术直答",
     ["活着", "余华", "福贵", "生命"], "通识拓展481"),
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
                               "level:L2", "status:verified", "batch:通识拓展481"],
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
    bank["version"] = "v7.48"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
