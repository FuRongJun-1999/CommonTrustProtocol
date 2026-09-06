# -*- coding: utf-8 -*-
"""seed_common_312_cards.py · 通识拓展批次312知识卡+题库（幂等）

312：人物-达芬奇全才/建筑-故宫紫禁城
KCCS 四要素+题干原句触发词。预检已过（QB-1169/1170+双id可用）。
注：蒙娜丽莎QB-202、凡尔赛QB-1102已有，本批避让取人物与建筑角度。
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
    ("kp_card_davinci",
     "达芬奇：文艺复兴全才",
     "人物历史知识点内容（人话接口）", "历史",
     "达芬奇为什么被称为「全才」：①**画家身份**——《蒙娜丽莎》（神秘的"
     "微笑=晕涂法（轮廓模糊过渡无边界线））、《最后的晚餐》（焦点"
     "透视与心理刻画巅峰）；②**科学家**——解剖尸体绘制人体骨骼肌肉图"
     "（精确到现代医学认可）、研究鸟类飞行画出扑翼机/直升机雏形草图、"
     "观察水流涡旋与心脏瓣膜；③**工程师**——军事工事/运河/起重机/机关"
     "枪雏形等数千页设计手稿；④**手稿之谜**——镜像左撇子书写（从右往"
     "左），7000 多页手稿散落各国，许多构想超前几百年未被当时技术实现；"
     "⑤**时代背景**——1452-1519 年意大利，文艺复兴「人文主义+观察自然"
     "」精神的化身（「认识你自己」+向自然学习），与米开朗基罗/拉斐尔"
     "并称文艺复兴三杰；⑥**启示**——跨领域的好奇心与方法论（观察→记录"
     "→实验）比单一技能更接近「天才」的真相。",
     ["达芬奇是干什么的", "蒙娜丽莎的微笑为什么神秘", "达芬奇手稿",
      "晕涂法", "文艺复兴三杰", "最后的晚餐"],
     ["问达芬奇机械设计", "问文艺复兴艺术史"],
     "atomic", "",
     "达芬奇=1452-1519意大利全才+蒙娜丽莎晕涂法+最后的晚餐+解剖"
     "图鸟飞水流研究+军事工程数千页手稿镜像左书+三杰之一+观察记录实验"
     "方法论跨领域好奇心是天才真相。"),
    ("kp_card_forbidden",
     "故宫紫禁城",
     "建筑历史知识点内容（人话接口）", "历史",
     "故宫（紫禁城）常识：①**建造**——明永乐四年（1406）起建，1420 年"
     "建成，动用工匠十万民夫百万（「伐木于蜀」巨木采运极难），此后 24 位"
     "明清皇帝居此 491 年；②**布局**——中轴对称：午门→太和殿（金銮殿，"
     "最高等级重檐庑殿顶）→中和/保和→乾清宫→神武门，前朝后寝/左祖右社；"
     "③**数字与等级**——房屋 8700 余间（传说9999.5间不实），屋脊兽数量"
     "标等级，黄色琉璃瓦皇家专属；④**榫卯与抗震**——全木结构不用一根"
     "钉子（榫卯柔性连接），600 年历经多次地震不倒（故宫模型抗震实验"
     "轰动）；⑤**排水**——北斗七星排列的排水沟+螭首吐水（600 年无积水"
     "记录）；⑥**如今**——故宫博物院 1925 年成立，186 万件文物，世界"
     "参观人数最多的博物馆之一；「紫禁」源于紫微星（天帝居所）——人间"
     "帝王对应天上帝星。",
     ["故宫是谁建的", "紫禁城多少年历史", "太和殿", "故宫为什么叫紫禁城",
      "故宫榫卯抗震", "故宫博物院文物"],
     ["问故宫文物南迁", "问中国古建等级制度"],
     "atomic", "",
     "故宫=1406-1420明永乐建成工匠十万+24帝491年+中轴对称前朝后寝+太和"
     "殿最高等级+8700余间黄瓦皇家+全木榫卯无钉600年抗震+螭首排水无积水+"
     "紫禁源于紫微星+1925博物院186万文物。"),
]

QUESTIONS = [
    ("QB-1169", "达芬奇除了画画还研究什么？他的手稿有什么特点？", "历史", "技术直答",
     ["达芬奇", "解剖", "手稿", "全才"], "通识拓展312"),
    ("QB-1170", "故宫为什么叫紫禁城？它有多少年历史？", "历史", "技术直答",
     ["紫禁城", "紫微星", "1420", "永乐"], "通识拓展312"),
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
                               "level:L2", "status:verified", "batch:通识拓展312"],
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
    bank["version"] = "v5.82"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
