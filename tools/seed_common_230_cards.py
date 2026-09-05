# -*- coding: utf-8 -*-
"""seed_common_230_cards.py · 通识拓展批次230知识卡+题库（幂等·两卡精批次）

230：生活常识-水土不服/生物学-长颈鹿的脖子为什么长
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖（血糖调节老卡为
稳态生理、salt 卡为高血压饮食——均划界）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_unaccustomed",
     "水土不服",
     "生活常识知识点内容（人话接口）", "生活常识",
     "水土不服=到达**新环境**后出现的胃肠不适、失眠、皮肤反应等：①**核心原"
     "因**——**肠道菌群**需要重新适应新环境的水质/饮食结构（菌群调整需 1-2 "
     "周）+气候温差+作息改变+心理压力；②**缓解**——第一周**饮食清淡易消化**"
     "（循序渐进尝试当地特色，勿一上来就重口味）、喝瓶装水过渡、规律作息、可"
     "补益生菌；③**旅行者腹泻**——若腹泻严重（尤其去卫生条件差的地区），注意"
     "补水防脱水，持续加重就医；④预防：出行前规律作息、带常用肠胃药、入乡"
     "随俗但过渡期「妥协折中」——慢慢地就「服」了。",
     ["水土不服怎么办", "为什么到了新地方会不舒服", "水土不服拉肚子",
      "肠道菌群适应", "旅行者腹泻"],
     ["问益生菌（用乳酸菌卡）", "问旅行者腹泻（就医）"],
     "atomic", "",
     "水土不服=新环境的菌群/水质/气候/作息变化引起胃肠不适失眠皮肤反应——肠道菌群适应需 1-2 周；缓解=第一周清淡易消化+瓶装水过渡+规律作息+益生菌；严重腹泻就医防脱水；慢慢地就「服」了。"),
    ("kp_card_giraffe",
     "长颈鹿的脖子为什么长",
     "基础科学知识点内容（人话接口）", "生物学",
     "长颈鹿的脖子约 **2 米**长（7 块颈椎与人类相同——每块被极度拉长）：①**"
     "经典进化案例**——达尔文自然选择说：古代长颈鹿祖先中**脖子稍长**的个体"
     "能吃到高处树叶，在食物短缺时存活并繁殖——「长脖基因」代代累积；②**生"
     "理奇迹**——为了把血液泵上 2 米高的头，血压高达人类 2 倍多（280/180），"
     "腿部有**紧绷的筋膜**防止血液淤积，低头饮水时脑后**血管网（网状奇异）**"
     "缓冲血压冲击；③**睡眠极少**——每天约 30 分钟-2 小时（多为 站立打"
     "盹）；④**拉马克「用进废退」说**（脖子越用越长并能遗传）已被现代遗传学"
     "否定——是选择压力筛选了天生脖子长的个体，不是「用出来」的。",
     ["长颈鹿脖子为什么长", "长颈鹿血压", "长颈鹿睡觉时间",
      "用进废退错在哪", "长颈鹿的颈椎有几块"],
     ["问达尔文进化论", "问其他动物趣闻（用动物卡）"],
     "atomic", "",
     "长颈鹿脖子约 2 米[7 块颈椎被极度拉长]：自然选择筛选长脖个体能食高处树叶存活——「用进废退」已被否定；生理奇迹=血压 2 倍+腿部筋膜防淤积+脑后血管网缓冲低头冲击；每天睡眠约 30 分钟-2 小时。"),
]

QUESTIONS = [
    ("QB-886", "为什么会「水土不服」？如何缓解水土不服的症状？", "生活常识", "技术直答",
     ["肠道菌群", "水质", "饮食", "适应", "1-2周", "清淡"], "通识拓展230"),
    ("QB-887", "长颈鹿的脖子为什么那么长？用进废退的说法对吗？", "生物学", "技术直答",
     ["自然选择", "高处", "树叶", "拉马克", "被否定"], "通识拓展230"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{6,}", content):
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
                               "level:L2", "status:verified", "batch:通识拓展230"],
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
                   "added": "2026-09-06"})
        added += 1
    bank["version"] = "v5.01"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
