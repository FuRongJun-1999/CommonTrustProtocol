# -*- coding: utf-8 -*-
"""seed_common_330_cards.py · 通识拓展批次330知识卡+题库（幂等）

330：健康-定期体检的意义/健康-科学补钙
KCCS 四要素+题干原句触发词。预检已过（QB-1229/1230+双id可用）。
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
    ("kp_card_checkup2",
     "定期体检的意义",
     "健康常识知识点内容（人话接口）", "生活常识",
     "为什么要定期体检：①**核心价值**——许多疾病早期无症状（高血压/糖尿病"
     "/肿瘤早发现治愈率天差地别——早期肠癌五年生存率 90%+，晚期不足 20%）"
     "——体检是「花小钱防大病」；②**体检频率**——健康成年人每年一次基础"
     "体检（血压/血常规/血糖血脂/尿常规/肝肾功能/腹部B超），40 岁后按风险"
     "加项（胃肠镜/低剂量肺CT/乳腺与宫颈筛查）；③**体检前的准备**——空腹"
     "8-12 小时（血脂血糖准确）、勿剧烈运动、如实填写病史（别隐瞒）；④**"
     "报告别只看「正常」**——关注临界值趋势（血压从 110 升到 130 也是信号"
     "），异常指标要复查确认再处理；⑤**体检不能代替就医**——有症状（持续"
     "疼痛/出血/消瘦）直接看医生，别等体检。",
     ["体检多久一次", "体检前注意什么", "体检报告怎么看",
      "早期发现疾病", "体检项目怎么选", "空腹体检"],
     ["问特定癌症筛查", "问体检机构选择"],
     "atomic", "",
     "体检=早发现治愈率天差地别花小钱防大病+健康成人每年一次基础+40岁后"
     "按风险加项胃肠镜CT筛查+空腹8-12小时如实病史+报告看临界趋势异常"
     "复查+有症状直接就医勿等体检。"),
    ("kp_card_calcium",
     "科学补钙",
     "健康常识知识点内容（人话接口）", "生活常识",
     "补钙的正确姿势：①**食补优先**——牛奶及奶制品（吸收率最高）/豆制品/"
     "绿叶菜/虾皮芝麻酱——每天 300ml 奶+豆制品基本满足；②**维生素 D 是"
     "钥匙**——不晒太阳补钙事倍功半（皮肤晒太阳合成维D促钙吸收），每天"
     "日晒约 20 分钟+必要时补维 D 制剂；③**运动与骨量**——负重运动"
     "（走路/跑步/力量训练）刺激骨骼增密，久坐不动补再多钙也难沉积；④"
     "**误区**——骨头汤补钙效率极低（钙在骨头里溶不出多少，汤里主要是"
     "脂肪嘌呤）；补钙并非越多越好（过量增加肾结石风险）；⑤**老年人**——"
     "绝经后女性骨量流失加速，骨密度检查（双能X线）+必要时药物干预防"
     "骨质疏松性骨折（髋部骨折被称为「人生最后一次骨折」）；⑥**钙片**——"
     "随餐服用吸收好，分次小剂量优于一次大剂量。",
     ["怎么补钙效果好", "骨头汤补钙真的吗", "补钙需要晒太阳吗",
      "老人骨质疏松怎么办", "钙片什么时候吃", "补钙过量"],
     ["问骨质疏松症", "问儿童补钙"],
     "atomic", "",
     "补钙=食补优先牛奶豆制品绿叶菜+维D是钥匙日晒20分钟+负重运动刺激"
     "骨密度+骨头汤补钙低效汤多脂肪嘌呤+过量肾结石风险+绝经后骨密度检查"
     "防髋部骨折+钙片随餐分次。"),
]

QUESTIONS = [
    ("QB-1229", "体检应该多久做一次？体检前要注意什么？", "生活常识", "技术直答",
     ["每年", "空腹", "复查", "趋势"], "通识拓展330"),
    ("QB-1230", "怎么补钙才科学？骨头汤真的能补钙吗？", "生活常识", "技术直答",
     ["牛奶", "维生素D", "晒太阳", "骨头汤"], "通识拓展330"),
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
                               "level:L2", "status:verified", "batch:通识拓展330"],
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
    bank["version"] = "v6.00"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
