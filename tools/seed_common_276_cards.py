# -*- coding: utf-8 -*-
"""seed_common_276_cards.py · 通识拓展批次276知识卡+题库（幂等）

276：生物-狗的嗅觉/生物-猫的胡须（动物感官新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1048/1049+双id可用）。
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
             "FADH2", "Vmax", "Km"}


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
    ("kp_card_dogsmell",
     "狗的嗅觉",
     "生物通识知识点内容（人话接口）", "基础科学",
     "狗鼻子为什么灵：①**硬件碾压**——人嗅觉感受器约 500 万个，狗约 2-3 亿"
     "个（嗅上皮面积人约 10cm² vs 狗可达 170cm²），大脑处理嗅觉的区域也比"
     "人大 40 倍——综合灵敏度约为人的百万倍级；②**结构加持**——湿润的"
     "鼻头吸附气味分子、长鼻道盘旋增大队气流接触、呼气走侧缝不干扰吸气"
     "（「闻得不打断」）；③**立体闻嗅**——能分辨气味的时间差与浓度差"
     "（左鼻右鼻对比）定位气味源方向，甚至「嗅出」几分钟前路过的人；④"
     "**工作犬**——缉毒/搜爆/搜救/搜尸/疾病检测（部分癌症低血糖犬嗅感知"
     "）——气味「指纹」各不相同；⑤**闻屁股读信息**——信息素传达"
     "情绪与状态，狗互相闻屁股是在「读简历」；⑥**保护**——强烈气味（"
     "香水/消毒水/辣椒）对狗是刺激伤害，别往狗鼻子喷东西。",
     ["狗的嗅觉有多灵敏", "狗鼻子为什么灵", "警犬怎么闻出毒品",
      "狗能闻出癌症吗", "狗互相闻屁股是什么行为", "嗅觉感受器"],
     ["问缉毒犬训练", "问电子鼻技术"],
     "atomic", "",
     "狗嗅觉=感受器2-3亿个vs人500万+嗅上皮170cm²灵敏百万倍级+湿鼻头吸附"
     "长鼻道盘旋呼气走侧缝+双鼻立体定位时间差+工作犬缉毒搜爆疾病检测"
     "+闻屁股=读信息素简历+勿喷强烈气味。"),
    ("kp_card_whisker",
     "猫的胡须",
     "生物通识知识点内容（人话接口）", "基础科学",
     "猫胡须的用途：①**精密触觉传感器**——胡须根部连着丰富神经末梢，可"
     "感知极细微的触碰、气流与振动（「振动探测器」），不是普通毛发；②**测"
     "量仪**——胡须展开宽度约等于身体最宽处，钻洞前先用胡须一探——能过"
     "胡须就能过身体（野外钻缝隙的生存依据）；③**暗视雷达**——夜里胡须"
     "感知空气流动的微小变化，帮猫在黑暗中察觉靠近的猎物与障碍；④**情绪"
     "显示器**——放松时自然前伸、恐惧时向后贴脸、狩猎时前张——读猫先读"
     "须；⑤**勿剪**——剪掉胡须猫会失去空间判断与平衡感（躲藏不动/撞东西"
     "/食欲下降），胡须自然脱落无妨人为修剪有害；⑥**不止脸上有**——前腿"
     "后侧也有胡须，辅助捕猎时感知猎物挣扎方位。",
     ["猫的胡须有什么用", "猫胡须能剪吗", "猫胡须是触觉还是毛发",
      "猫情绪看胡须", "猫为什么能钻小洞", "胡须测量"],
     ["问猫瞳孔变化", "问其他动物触觉器官"],
     "atomic", "",
     "猫胡须=根部丰富神经末梢精密触觉传感器感知触碰气流振动+展开宽度≈体宽"
     "钻洞前探测+暗视感知空气流动=夜行雷达+情绪显示器(放松前伸恐惧后贴"
     "狩猎前张)+勿剪(失去空间判断平衡)自然脱落无妨+前腿后侧也有。"),
]

QUESTIONS = [
    ("QB-1048", "狗的嗅觉为什么那么灵敏？警犬靠嗅觉能做什么？", "基础科学", "技术直答",
     ["感受器", "嗅上皮", "灵敏", "缉毒"], "通识拓展276"),
    ("QB-1049", "猫的胡须有什么用？能不能剪掉？", "基础科学", "技术直答",
     ["触觉", "测量", "情绪", "剪"], "通识拓展276"),
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
                               "level:L2", "status:verified", "batch:通识拓展276"],
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
    bank["version"] = "v5.47"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
