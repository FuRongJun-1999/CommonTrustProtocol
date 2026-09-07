# -*- coding: utf-8 -*-
"""seed_common_479_cards.py · 通识拓展批次479知识卡+题库（幂等）

479：3 张新卡·经典寓言童话三连（《伊索寓言》 kp_card_aesop /
    《格林童话》 kp_card_grimm / 《一千零一夜》 kp_card_arabiannights）。
预检已过（QB-1672~1674 可用，三主题题库卡库双零）。
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
    ("kp_card_aesop",
     "《伊索寓言》",
     "世界文学知识点内容（人话接口）", "世界文化",
     "《伊索寓言》——古希腊寓言集，西方寓言的鼻祖：①**形式**——篇幅"
     "短小、主角多为动物、结尾点出道德教训（「这个故事说明……」）；"
     "②**经典篇目**——《龟兔赛跑》（坚持不懈胜过骄傲自满）、《狼来了》"
     "（说谎者失去信任）、《农夫与蛇》（警惕恩将仇报）、《乌鸦喝水》"
     "（智慧解决问题的变通）；③**作者**——相传为公元前 6 世纪古希腊"
     "奴隶伊索所作，实为流传于民间、后人搜集整理的寓言总集；④**影响**"
     "——与《克雷洛夫寓言》《拉封丹寓言》《莱辛寓言》并称世界四大寓"
     "言集，许多故事成了世界通用典故。",
     ["伊索寓言是哪个国家的", "龟兔赛跑的寓意", "狼来了的故事",
      "农夫与蛇讲什么", "乌鸦喝水", "世界四大寓言集"],
     ["问克雷洛夫寓言", "问中国古代寓言"],
     "atomic", "",
     "伊索寓言=古希腊寓言集西方寓言鼻祖公元前6世纪伊索相传实为民间整"
     "理+短小动物主角结尾点道德教训+龟兔赛跑坚持胜骄傲狼来了失信失信任"
     "农夫与蛇警惕恩将仇报乌鸦喝水智慧变通+与克雷洛夫拉封丹莱辛并称四"
     "大寓言集。"),
    ("kp_card_grimm",
     "《格林童话》",
     "世界文学知识点内容（人话接口）", "世界文化",
     "《格林童话》——德国格林兄弟搜集整理的民间童话集：①**整理者**——"
     "雅各布·格林与威廉·格林兄弟（19 世纪德国语言学家、民俗学家），"
     "他们走遍乡野记录民间口传故事——是「学者整理民间文学」的典范；"
     "②**经典篇目**——《白雪公主》《灰姑娘》《青蛙王子》《小红帽》"
     "《勇敢的小裁缝》等 200 多篇；③**特点**——保留民间传说的质朴与"
     "奇幻：魔法、诅咒、王子公主与善恶分明的结局（善有善报）；④**"
     "影响**——与《安徒生童话》并列为世界童话双璧，是迪士尼动画的"
     "重要灵感来源。",
     ["格林童话是谁写的", "格林兄弟", "白雪公主的故事",
      "灰姑娘的故事", "青蛙王子", "小红帽"],
     ["问安徒生童话", "问一千零一夜"],
     "atomic", "",
     "格林童话=德国格林兄弟19世纪语言学家民俗学家搜集整理民间口传故"
     "事典范+白雪公主灰姑娘青蛙王子小红帽勇敢的小裁缝200多篇+魔法诅咒"
     "善恶分明善有善报质朴奇幻+与安徒生童话并列世界童话双璧迪士尼灵感"
     "来源。"),
    ("kp_card_arabiannights",
     "《一千零一夜》",
     "世界文学知识点内容（人话接口）", "世界文化",
     "《一千零一夜》——阿拉伯民间故事集，又称《天方夜谭》：①**框架"
     "故事**——暴君山鲁亚尔每天娶一位新娘、次日处死；宰相之女山鲁"
     "佐德为拯救姐妹自愿出嫁，每夜讲故事吊住国王好奇心，讲了一千零一"
     "夜——用故事感化暴君、救下性命；②**经典篇目**——《阿里巴巴与四"
     "十大盗》（「芝麻开门」）、《阿拉丁与神灯》、《辛巴达航海》；③**"
     "特点**——浓郁阿拉伯风情：飞毯、神灯、魔法与商旅冒险，想象瑰丽"
     "奔放；④**地位**——阿拉伯文学的巅峰之作，高尔基誉为「民间口头"
     "创作中最壮丽的一座纪念碑」。",
     ["一千零一夜是哪国的", "天方夜谭是什么意思",
      "山鲁佐德", "阿里巴巴与四十大盗", "阿拉丁神灯",
      "辛巴达航海"],
     ["问阿拉伯文化", "问世界名著"],
     "atomic", "",
     "一千零一夜=阿拉伯民间故事集又称天方夜谭+山鲁佐德每夜讲故事千零"
     "一夜感化暴君救姐妹+阿里巴巴四十大盗芝麻开门阿拉丁神灯辛巴达航海"
     "+飞毯神灯魔法商旅冒险想象瑰丽+阿拉伯文学巅峰高尔基誉民间口头创作"
     "最壮丽纪念碑。"),
]

QUESTIONS = [
    ("QB-1672", "《伊索寓言》是哪个国家的？龟兔赛跑讲了什么道理？",
     "世界文学", "技术直答",
     ["伊索寓言", "古希腊", "寓言", "龟兔赛跑"], "通识拓展479"),
    ("QB-1673", "《格林童话》是谁整理的？有哪些经典故事？",
     "世界文学", "技术直答",
     ["格林童话", "格林兄弟", "白雪公主", "灰姑娘"], "通识拓展479"),
    ("QB-1674", "《一千零一夜》为什么又叫《天方夜谭》？有哪些经典故事？",
     "世界文学", "技术直答",
     ["一千零一夜", "天方夜谭", "山鲁佐德", "阿拉丁"], "通识拓展479"),
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
                               "level:L2", "status:verified", "batch:通识拓展479"],
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
