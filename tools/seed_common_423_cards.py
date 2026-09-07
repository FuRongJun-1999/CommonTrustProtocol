# -*- coding: utf-8 -*-
"""seed_common_423_cards.py · 通识拓展批次423知识卡+题库（幂等）

423：3 张新卡·学习方法三连（费曼学习法 kp_card_feynman /
    错题本与复盘 kp_card_wrongbook / 思维导图 kp_card_mindmap）。
KCCS 四要素+题干原句触发词。预检已过（QB-1507~1509 可用，
三主题题库卡库双零；叛逆/专注候选为卡库误中已排除）。
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
             "XMind"}


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
    ("kp_card_feynman",
     "费曼学习法",
     "学习方法知识点内容（人话接口）", "学习成长",
     "费曼学习法——诺贝尔物理学奖得主费曼推崇的「以教代学」：①**核心"
     "思想**——检验是否真懂的最好办法，是把概念讲给完全不懂的人听"
     "（输出倒逼输入）；②**四步循环**——选定概念 → 假装教外行（白纸"
     "复述，不许看书）→ 发现卡壳的地方（那就是理解盲区）→ 回炉重学并"
     "用更简单的语言再讲一遍；③**为什么有效**——「看懂了」和「会讲了」"
     "是两回事：阅读产生熟悉感（掌握幻觉），讲授暴露真实的理解漏洞；"
     "④**使用场景**——复习理科概念、准备面试讲项目、写技术分享；⑤**"
     "费曼的检验标准**——如果你不能用简单的语言解释，说明你自己还没"
     "真正理解。",
     ["费曼学习法是什么", "以教代学", "怎么检验自己学会了",
      "费曼技巧四步", "掌握幻觉", "学习输出"],
     ["问网课学习", "问错题本"],
     "atomic", "",
     "费曼学习法=以教代学讲给外行听输出倒逼输入+四步选概念教外行发现"
     "卡壳回炉简化+看懂和会讲是两回事阅读熟悉感是掌握幻觉+复习概念面"
     "试讲项目写分享适用+不能用简单语言解释说明没真懂。"),
    ("kp_card_wrongbook",
     "错题本与复盘",
     "学习方法知识点内容（人话接口）", "学习成长",
     "错题本——把错误变成进步阶梯的工具：①**不止抄题**——核心是记录"
     "「错因」：概念不清/审题失误/计算粗心/方法没掌握，四类错因对策"
     "完全不同；②**三栏法**——原题 + 我的错解、正确解法 + 错因分析"
     "与同类题提示；③**重做比抄写重要**——遮住答案重新做一遍（间隔"
     "一周/一月各做一次），做对了才标记「过关」；④**考前黄金材料**——"
     "错题本是最针对个人弱点的精准复习资料，比盲目刷题高效得多；⑤**"
     "延伸**——复盘思维不止用于考试：工作项目复盘、运动失误复盘，"
     "「从错误中学习」是通用的成长算法。",
     ["错题本怎么整理", "错题本有必要吗", "错因怎么分类",
      "错题重做方法", "考前怎么复习", "复盘是什么意思"],
     ["问费曼学习法", "问笔记方法"],
     "atomic", "",
     "错题本=核心记错因概念不清审题失误计算粗心方法没掌握四类对策不"
     "同+三栏法原题错解正解错因+重做比抄写重要间隔一周一月做对才过关"
     "+考前最针对个人弱点的精准复习资料+复盘思维通用于工作运动成长算"
     "法。"),
    ("kp_card_mindmap",
     "思维导图",
     "学习方法知识点内容（人话接口）", "学习成长",
     "思维导图——东尼·博赞推广的发散式思考工具：①**结构**——中心"
     "主题在中央，分支向四周放射性展开，一层层细分（主干→分支→细节）；"
     "②**为什么有效**——契合大脑的「放射性思维」：关键词+颜色+图像"
     "比大段文字更容易被记忆和联想（图像是大脑的原生语言）；③**典型"
     "用途**——读书笔记（一章一张图）、复习总结（把厚书变薄）、头脑"
     "风暴（发散想法不设限）、写作提纲（先搭骨架再填肉）；④**要点**"
     "——分支上写关键词而不是整句、每条分支一个颜色、留白给后续补充；"
     "⑤**工具**——纸笔即可，软件有 XMind 等，但工具永远服务于思考"
     "本身。",
     ["思维导图怎么画", "思维导图有什么用", "东尼博赞",
      "用思维导图做笔记", "思维导图复习", "头脑风暴"],
     ["问笔记方法", "问记忆法"],
     "atomic", "",
     "思维导图=中心主题放射性展开层层细分+契合大脑放射性思维关键词颜"
     "色图像比大段文字易记忆联想+读书笔记复习总结头脑风暴写作提纲四大"
     "用途+分支写关键词不写整句一分支一色留白+纸笔即可工具服务思考。"),
]

QUESTIONS = [
    ("QB-1507", "费曼学习法是什么？怎么用它检验自己真的学会了？",
     "学习成长", "技术直答",
     ["费曼", "以教代学", "输出", "学习法"], "通识拓展423"),
    ("QB-1508", "错题本怎么整理才有效？为什么要定期重做错题？",
     "学习成长", "技术直答",
     ["错题本", "错因", "重做", "复盘"], "通识拓展423"),
    ("QB-1509", "思维导图怎么画？它为什么能帮助记忆？",
     "学习成长", "技术直答",
     ["思维导图", "画法", "记忆", "发散"], "通识拓展423"),
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
                               "level:L2", "status:verified", "batch:通识拓展423"],
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
    bank["version"] = "v6.94"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
