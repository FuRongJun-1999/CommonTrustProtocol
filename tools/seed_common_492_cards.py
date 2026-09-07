# -*- coding: utf-8 -*-
"""seed_common_492_cards.py · 通识拓展批次492知识卡+题库（幂等）

492：3 张新卡·世界自然奇观三连（大堡礁 kp_card_greatbarrier /
    黄石公园 kp_card_yellowstone / 科罗拉多大峡谷
    kp_card_canyon）。预检已过（QB-1708~1710 可用，
    三主题题库卡库双零）。
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
    ("kp_card_greatbarrier",
     "大堡礁",
     "世界自然奇观知识点内容（人话接口）", "自然常识",
     "大堡礁——世界最大的珊瑚礁系统：①**位置规模**——澳大利亚东北部"
     "昆士兰海域，绵延约 2300 公里，由近 3000 个独立礁体、900 座岛屿"
     "组成，从太空可见；②**珊瑚礁是什么**——珊瑚虫（腔肠动物）分泌"
     "碳酸钙骨骼，亿万个珊瑚虫世代堆积形成礁体——珊瑚礁是「动物建的"
     "建筑」；③**共生奥秘**——珊瑚虫体内共生虫黄藻（提供养分与颜色），"
     "海水升温会导致虫黄藻离开，珊瑚失去颜色死亡——即「珊瑚白化」；"
     "④**生态价值**——供养 1500 多种鱼类、400 多种珊瑚，是海洋中的"
     "「热带雨林」；1981 年列入世界遗产；⑤**威胁**——全球变暖白化、"
     "冠刺海星爆发、农业污染。",
     ["大堡礁在哪里", "珊瑚礁是怎么形成的", "珊瑚白化",
      "大堡礁有多长", "珊瑚是动物还是植物", "世界自然遗产海洋"],
     ["问马尔代夫", "问海洋保护"],
     "atomic", "",
     "大堡礁=澳大利亚东北绵延2300公里近3000礁体900岛屿太空可见+珊瑚"
     "虫分泌碳酸钙世代堆积动物建的建筑+共生虫黄藻提供养分颜色海水升温"
     "白化死亡+1500多种鱼类400多种珊瑚海洋热带雨林1981世界遗产+威胁"
     "变暖白化冠刺海星污染。"),
    ("kp_card_yellowstone",
     "黄石公园",
     "世界自然奇观知识点内容（人话接口）", "自然常识",
     "黄石公园——世界第一座国家公园（1872 年，美国）：①**地质奇观**——"
     "坐落超级火山之上：间歇泉（老忠实泉规律喷发）、五彩热泉（大棱镜"
     "泉的橙红蓝绿来自嗜热微生物）、泥火山、喷气孔；②**野生动物**——"
     "美洲野牛、灰狼、灰熊、麋鹿——「美国的塞伦盖蒂」；③**生态启示**"
     "——1995 年重引灰狼控制马鹿种群，植被河狸随之恢复——「营养级"
     "联」生态修复经典案例；④**管理理念**——「为了人民的利益与享受"
     "」设立，国家公园理念由此推广全球（中国国家公园体系借鉴其经验）。"
     ,
     ["黄石公园在哪里", "世界第一座国家公园", "老忠实泉",
      "大棱镜泉颜色", "黄石超级火山", "灰狼重回黄石"],
     ["问国家公园", "问地热"],
     "atomic", "",
     "黄石公园=1872年世界第一座国家公园美国+超级火山之上间歇泉老忠实"
     "泉大棱镜泉五彩嗜热微生物泥火山+野牛灰狼灰熊麋鹿美国塞伦盖蒂+"
     "1995重引灰狼营养级联植被恢复生态修复经典+国家公园理念推广全球。"),
    ("kp_card_canyon",
     "科罗拉多大峡谷",
     "世界自然奇观知识点内容（人话接口）", "自然常识",
     "科罗拉多大峡谷——流水亿万年切割的地质史书：①**规模**——美国"
     "亚利桑那州，长约 446 公里、深约 1800 米、最宽 29 公里；②**怎么"
     "形成**——科罗拉多高原整体缓慢抬升 + 科罗拉多河持续下切侵蚀，"
     "河水像「锯子」切穿岩层；峡谷壁暴露出约 20 亿年的地质层（底部"
     "岩石近太古代）；③**岩层如书页**——每一层岩石对应一个地质年代，"
     "颜色随矿物成分变化（红/橙/棕/灰层理分明）；④**生态**——从谷底"
     "荒漠到谷顶森林的垂直气候带，物种随海拔变化；⑤**地位**——1919"
     " 年设立国家公园，世界自然遗产。",
     ["科罗拉多大峡谷", "大峡谷怎么形成的", "大峡谷有多深",
      "峡谷岩层", "侵蚀作用", "美国国家公园"],
     ["问东非大裂谷", "问地质年代"],
     "atomic", "",
     "科罗拉多大峡谷=亚利桑那州长446公里深1800米+高原抬升科罗拉多河"
     "下切侵蚀河水如锯切穿岩层+谷壁20亿年地质层如书页每层对应地质年代"
     "颜色随矿物变化+谷底荒漠谷顶森林垂直气候带+1919年国家公园世界自"
     "然遗产。"),
]

QUESTIONS = [
    ("QB-1708", "大堡礁在哪里？珊瑚礁是怎么形成的？",
     "自然常识", "技术直答",
     ["大堡礁", "珊瑚", "澳大利亚", "白化"], "通识拓展492"),
    ("QB-1709", "黄石公园为什么著名？它的地质奇观有哪些？",
     "自然常识", "技术直答",
     ["黄石公园", "间歇泉", "国家公园", "火山"], "通识拓展492"),
    ("QB-1710", "科罗拉多大峡谷是怎么形成的？",
     "自然常识", "技术直答",
     ["大峡谷", "侵蚀", "岩层", "河流"], "通识拓展492"),
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
                               "level:L2", "status:verified", "batch:通识拓展492"],
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
    bank["version"] = "v7.57"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
