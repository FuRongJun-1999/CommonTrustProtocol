# -*- coding: utf-8 -*-
"""seed_common_178_cards.py · 通识拓展批次178知识卡+题库（幂等·两卡精批次）

178：生活常识-眼镜起雾与防雾/生活常识-挑鸡蛋的技巧
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_foggyglasses",
     "眼镜起雾与防雾",
     "生活常识知识点内容（人话接口）", "生活常识",
     "起雾原理：呼出的**水蒸气**是热的，遇到冷的镜片**凝结**成无数微小水珠附"
     "在镜面，光发生散射——看起来就是「雾」。**防雾思路=让水不形成小水珠**："
     "①**防雾剂/肥皂水**——用手指蘸肥皂水或洗洁精薄涂镜片再擦干：表面活性剂"
     "让凝结的水铺成**透明水膜**而不是散射光的小水珠（可维持数小时）；②**戴"
     "口罩防上窜**——把口罩鼻夹金属条**捏紧贴鼻梁**，呼气从两侧排出不冲镜片；"
     "③镜片稍离面部/压低眼镜位置（物理拉开温差通道）；④工业方案：防雾镀膜"
     "（亲水涂层）泳镜汽车防雾贴同理。注意：哈气擦干只是暂时，温差大马上再起"
     "雾——肥皂水法最实用廉价。火锅/泡面/进 warm 房间起雾同理，等温差平衡自"
     "然消散，勿反复干擦（伤镀膜）。",
     ["眼镜起雾怎么办", "戴口罩眼镜起雾", "肥皂水防雾原理",
      "防雾剂有用吗", "吃火锅眼镜有雾"],
     ["问近视手术（就医）", "问镜片镀膜种类"],
     "atomic", "",
     "起雾=呼气水蒸气遇冷镜片凝结成散射小水珠；防雾=肥皂水/防雾剂让水铺成透明水膜（表面活性剂·可维持数小时）+口罩鼻夹捏紧防上窜；反复干擦伤镀膜——温差平衡后自散。"),
    ("kp_card_pickegg",
     "挑鸡蛋的技巧",
     "生活常识知识点内容（人话接口）", "生活常识",
     "鸡蛋新鲜度三招：①**沉水法**——放入清水：**平躺水底=新鲜**（气室小、蛋"
     "内水分足）；竖立=放了一段时间；**漂浮=已变质**（气室大+产气，别吃）；"
     "②**摇一摇**——新鲜蛋内容物紧实无晃动声；有「晃水声」=散黄或气室大；"
     "③**照一照**——对光看：气室小、蛋黄轮廓模糊均匀=新鲜；气室大、有黑影="
     "陈蛋。**保存**：大头朝上放（气室在上、蛋黄浮离蛋壳不易贴壳变质）；冷藏"
     "4°C 可存 30-40 天，室温夏天约 10 天；**别洗**（壳外天然保护膜洗掉反而"
     "易坏，脏污吃前再洗）。磕开判断：蛋黄饱满挺立、蛋清浓稠分层=新鲜；蛋黄"
     "散开蛋清如水=不新鲜。变色/异味（硫化氢臭味）=已变质勿吃。",
     ["怎么挑新鲜鸡蛋", "鸡蛋沉水新鲜还是浮的新鲜", "鸡蛋大头朝上还是小头朝上",
      "鸡蛋能放多久", "鸡蛋要不要洗了再放"],
     ["问溏心蛋安全性", "问土鸡蛋营养差异"],
     "atomic", "",
     "挑鸡蛋=沉水法（平躺新鲜/竖立放久/漂浮变质）+摇晃无水声+照光气室小；存放大头朝上冷藏 4°C 30-40 天、壳外保护膜勿洗（脏污吃前洗）；磕开蛋黄挺立蛋清浓稠=新鲜；异味变色勿吃。"),
]

QUESTIONS = [
    ("QB-783", "戴口罩时眼镜为什么容易起雾？用肥皂水涂镜片为什么能防雾？", "生活常识", "技术直答",
     ["水蒸气", "凝结", "水膜", "表面活性剂", "鼻夹"], "通识拓展178"),
    ("QB-784", "把鸡蛋放进清水里，新鲜蛋、放置久的蛋和坏蛋分别是什么状态？", "生活常识", "技术直答",
     ["平躺", "沉底", "竖立", "漂浮", "气室"], "通识拓展178"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    whitelist = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba", "effect"}
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{6,}", content):
            if word not in whitelist:
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
                               "level:L2", "status:verified", "batch:通识拓展178"],
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
                   "added": "2026-09-05"})
        added += 1
    bank["version"] = "v4.51"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
