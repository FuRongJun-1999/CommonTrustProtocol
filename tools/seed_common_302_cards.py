# -*- coding: utf-8 -*-
"""seed_common_302_cards.py · 通识拓展批次302知识卡+题库（幂等）

302：历史-金字塔与古埃及/历史-木乃伊的制作（古埃及文明新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1137/1138+双id可用）。
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
             "BCS", "B2H6", "borrow", "Rust"}


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
    ("kp_card_pyramid",
     "金字塔与古埃及",
     "历史知识点内容（人话接口）", "历史",
     "金字塔常识：①**是什么**——古埃及法老（国王）的陵墓，四棱锥形；现存"
     "约 80 余座，最著名吉萨三大金字塔（胡夫金字塔约公元前 2560 年，原高"
     "约 146 米——保持世界最高建筑纪录 3800 余年）；②**尼罗河文明**——"
     "埃及是「尼罗河的赠礼」：定期泛滥带来肥沃淤泥，农业依托尼罗河，历法"
     "（太阳历 365 天）因测汛期而生；③**怎么建的**——石灰岩巨石（平均"
     "2.5 吨）斜坡+杠杆/撬具人力拖运（考古支持雇佣劳工而非纯奴隶说），"
     "底边误差极小展现惊人工程测量能力；④**狮身人面像**——哈夫拉金字塔"
     "旁，整块岩石雕成，传说谜语的主人；⑤**象形文字与罗塞塔石碑**——"
     "1799 年罗塞塔石碑（同一诏书三种文字：象形文/世俗体/古希腊文）让"
     "商博良 1822 年破译象形文字，埃及学诞生；⑥**文明时间感**——吉萨"
     "金字塔建成时猛犸象还存活着（孤岛上残存种群）。",
     ["金字塔是谁建的", "胡夫金字塔多高", "金字塔怎么建造的",
      "尼罗河与古埃及", "罗塞塔石碑", "狮身人面像"],
     ["问图坦卡蒙墓", "问埃及神祇体系"],
     "atomic", "",
     "金字塔=法老四棱锥陵墓(吉萨胡夫前2560年146米纪录3800年)+尼罗河"
     "赠礼泛滥农耕太阳历+斜坡人力建造成就工程测量+狮身人面像整石雕+"
     "罗塞塔石碑三文对照1822商博良破译象形文+时间感猛犸象尚存。"),
    ("kp_card_mummy",
     "木乃伊的制作",
     "历史知识点内容（人话接口）", "历史",
     "木乃伊怎么做成的：①**信仰根源**——古埃及人相信灵魂不死（「卡」与"
     "「巴」），肉体是灵魂回归的居所——保存尸体=保住永生资格；②**制作"
     "流程（约 70 天）**——脑经鼻腔掏出弃置（古人认为心才是思维器官）/"
     "内脏取出分装四个卡诺卜坛（肝肺胃肠，防腐液保存；心留在体内受秤量"
     "审判）→尸身以泡碱（天然碳酸钠）覆盖 40 天彻底脱水→亚麻布+树脂"
     "填塞塑形→层层亚麻绷带缠绕+护身符与《亡灵书》；③**脱水是关键**——"
     "细菌需要水，泡碱吸干组织水分腐败即止；④**科学读木乃伊**——CT/"
     "DNA 检测不拆裹布即可知年龄/疾病/死因（拉美西斯三世喉部割伤案）；"
     "⑤**动物木乃伊**——猫/鳄鱼/圣甲虫制成百万计（宗教供奉产业）；⑥"
     "**误解**——「法老的诅咒」无科学依据，墓穴霉菌与巧合可解释。",
     ["木乃伊是怎么制作的", "木乃伊为什么要做", "泡碱脱水",
      "卡诺卜坛", "亡灵书", "木乃伊的诅咒是真的吗"],
     ["问埃及神话体系", "问文物科技检测"],
     "atomic", "",
     "木乃伊=灵魂不死肉体为居所信仰+70天流程(掏脑弃/内脏入卡诺卜坛心"
     "留秤量审判+泡碱40天脱水关键+绷带亡灵书)+CT与DNA无损检测+动物"
     "木乃伊供奉产业+法老诅咒无科学依据。"),
]

QUESTIONS = [
    ("QB-1137", "金字塔是谁建造的？罗塞塔石碑有什么意义？", "历史", "技术直答",
     ["法老", "尼罗河", "罗塞塔", "象形文字"], "通识拓展302"),
    ("QB-1138", "木乃伊是怎么制作的？为什么脱水是关键？", "历史", "技术直答",
     ["泡碱", "脱水", "内脏", "绷带"], "通识拓展302"),
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
                               "level:L2", "status:verified", "batch:通识拓展302"],
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
    bank["version"] = "v5.72"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
