# -*- coding: utf-8 -*-
"""seed_common_113_cards.py · 通识拓展批次113知识卡+题库（幂等）

113：物理学-近视眼与远视眼的矫正原理/化学-固体药品的取用/生物学-流感与普通感冒的区别
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_eyeglasscorr",
     "近视眼与远视眼的矫正原理",
     "基础科学知识点内容（人话接口）", "物理学",
     "成像位置与矫正镜片对照：①**近视眼**——晶状体太厚（折光太强）或眼球前后"
     "径过长，远处物体成像在视网膜**前**方→佩戴**凹透镜**（发散光线，让像后移"
     "到视网膜上）；②**远视眼**——晶状体太薄或眼轴过短，成像在视网膜**后**方→"
     "佩戴**凸透镜**（会聚光线，让像前移）；老花眼与远视类似也用凸透镜（但成因"
     "是晶状体老化弹性变差）。记忆口诀：「近凹远凸」。验光配镜需专业验光（度数"
     "不准确反而加速视力恶化）。预防近视：户外阳光（多巴胺抑制眼轴增长）+20-20-"
     "20 法则（每用眼 20 分钟看 20 英尺外 20 秒）+读写姿势三个一（一尺一拳一寸）。",
     ["近视眼和远视眼的矫正原理", "近视为什么戴凹透镜", "远视为什么戴凸透镜",
      "老花镜是什么透镜", "近视的成像位置", "怎么预防近视加深"],
     ["问眼球结构复习", "问散光与近视的区别"],
     "atomic", "",
     "近视=像成视网膜前(晶状体过凸/眼轴长)→凹透镜发散矫正；远视=像成后→凸透镜会聚；老花=晶状体老化(也用凸)；预防=户外阳光+20-20-20+三个一。"),
    ("kp_card_powdertake",
     "固体药品的取用方法",
     "基础科学知识点内容（人话接口）", "化学",
     "固体药品取用规范：①**粉末状**——用药匙或纸槽：试管**横放**，把药品送到试"
     "管**底部**，然后直立试管让药品滑落（「一横二送三直立」）——防止药品沾在"
     "管口和管壁；②**块状固体**——用镊子：试管横放，把药品放在**管口**，缓缓竖"
     "立滑到管底（防打破管底）；③用剩的药品——**不放回原瓶**、不随意丢弃、更不"
     "能带出实验室（放入指定容器）。倾倒液体规范：瓶塞**倒放**（防污染瓶塞），标"
     "签**向手心**（防残液流下腐蚀标签），瓶口紧挨试管口。这些规范都是用血泪教训"
     "总结的——遵守规范就是保护自己。",
     ["固体药品怎么取用", "粉末状药品取用方法", "一横二送三直立",
      "块状固体怎么放进试管", "倾倒液体时瓶塞为什么倒放", "用剩的药品能放回原瓶吗"],
     ["问液体药品取用规范", "问量筒滴管使用"],
     "atomic", "",
     "粉末=药匙/纸槽「一横二送三直立」；块状=镊子放管口缓竖滑落；剩药不放回原瓶；倾倒液体=瓶塞倒放+标签向手心+瓶口挨管口——规范皆源于事故教训。"),
    ("kp_card_flucold",
     "流感与普通感冒的区别",
     "生活常识知识点内容（人话接口）", "生活常识",
     "流感（流行性感冒）与普通感冒是两种不同的病：①**病原体**——流感由流感病"
     "毒（甲型/乙型等）引起，传染性强易暴发流行；普通感冒由鼻病毒等多种病原引"
     "起，传染性弱；②**症状**——流感起病急、高热（39-40℃）、全身酸痛乏力明"
     "显，可致肺炎等并发症；普通感冒症状轻（鼻塞流涕打喷嚏），低热或不发热；③"
     "**治疗**——流感在 48 小时内用奥司他韦等抗病毒药有效，普通感冒无特效药（对"
     "症缓解，多喝水休息自愈）；④**预防**——流感疫苗（每年流行株不同需每年接"
     "种）、勤洗手、流感季戴口罩。误区：「流感就是重感冒」——错，流感可致死（老"
     "人儿童高危）。「着凉会感冒」——着凉只是降低抵抗力，病原体才是原因。",
     ["流感和普通感冒的区别", "流感是由什么引起的", "流感48小时内用什么药",
      "流感疫苗为什么要每年打", "着凉会感冒吗", "流感的症状有哪些"],
     ["问感冒药成分解析", "问流感并发症高危人群"],
     "atomic", "",
     "流感≠重感冒：病原=流感病毒(甲乙型·易暴发)vs 鼻病毒等；症=急起高热全身酸痛可致肺炎 vs 轻症；治疗=48h 内奥司他韦 vs 对症自愈；预防=每年接种流感疫苗+口罩洗手。"),
]

QUESTIONS = [
    ("QB-587", "近视眼和远视眼的矫正原理", "物理学", "技术直答",
     ["凹透镜", "凸透镜"], "通识拓展113"),
    ("QB-588", "固体药品怎么取用", "化学", "技术直答",
     ["药匙", "纸槽"], "通识拓展113"),
    ("QB-589", "流感和普通感冒的区别", "生物学", "技术直答",
     ["流感病毒", "传染性", "高热"], "通识拓展113"),
]


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
                               "level:L2", "status:verified", "batch:通识拓展113"],
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
    bank["version"] = "v2.5"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
