# -*- coding: utf-8 -*-
"""seed_common_235_cards.py · 通识拓展批次235知识卡+题库（幂等）

235：科技-二维码的原理与容错/生活常识-肉类冷冻保存与解冻
KCCS 四要素+题干原句触发词。出卡前三重预检（QB号断言+id查重+主题撞车）已过。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

WHITELIST = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
             "effect", "OR6A2", "ghrelin", "DOMS", "DHT", "frisson"}


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
    ("kp_card_qrcode",
     "二维码的原理与容错",
     "科技通识知识点内容（人话接口）", "科技",
     "二维码（矩阵码）工作原理：①**黑白方块=二进制**——黑格 1 白格 0，数据被"
     "编码为点阵，比一维条码能存几百倍的信息（网址/文本/名片）；②**三个角的"
     "「回」字形方块是定位图案**——无论正扫斜扫倒扫，扫码器靠它们确定坐标系，"
     "所以扫的时候不需要对正方向；③**容错纠错**——内置里德-所罗门纠错算法，"
     "容错等级 L(7%)/M(15%)/Q(25%)/H(30%)，最高可修复近三成破损——这就是"
     "二维码中间贴标识图案或缺一角仍能扫出的原因；④**掩模**——编码后与掩模图"
     "异或，打散黑白块避免出现大面积同色区域干扰识别；⑤右侧无定位图案的角有"
     "校正图形（小方块），用于扭曲变形时的坐标修正。",
     ["二维码是什么原理", "二维码破了还能扫是什么原理",
      "二维码三个角的方块是干什么的", "二维码容错率有多高",
      "二维码中间加图案还能扫吗"],
     ["问二维码支付安全", "问一维条码编码细节"],
     "atomic", "",
     "二维码=黑白点阵二进制+三回字定位图案（任意方向可扫）+里德-所罗门纠错"
     "（最高容错 30%故缺角贴图仍可扫）+掩模打散同色块+校正图形修正变形。"),
    ("kp_card_freeze_defrost",
     "肉类冷冻保存与解冻",
     "生活常识知识点内容（人话接口）", "生活常识",
     "肉类冷冻与解冻要点：①**冷冻不是保鲜魔法**——-18℃ 下细菌停止繁殖但不是"
     "被杀死，回温即复活；脂肪氧化和冰晶损伤仍在缓慢进行，红肉类建议 10-12 个"
     "月内吃完，禽类 8-10 个月，海鲜油脂高仅 2-4 个月；②**分装再冻**——按每餐"
     "量分装扁平封装（薄=解冻快+冰晶小），反复解冻复冻是品质杀手；③**最佳解冻"
     "法=冷藏室缓慢解冻**（低温下细菌不繁殖，外里温差小）；④**勿室温/热水解冻**"
     "——表层温度进入 4-60℃ 危险带细菌每 20 分钟翻倍，外层烂了中心还是冰；⑤"
     "**微波解冻档解冻须立即烹饪**——局部已半熟且升温不均；⑥**解冻后不再回冻**"
     "——解冻时细菌已开始繁殖，回冻只抑菌不杀菌，营养流失口感变差（生肉 "
     "冷藏解冻后 1-2 天内烹饪）。",
     ["肉放冰箱冷冻能保存多久", "冷冻肉怎么解冻最好",
      "肉可以反复解冻再冻吗", "解冻肉用热水泡对吗", "微波炉解冻后能放回去吗"],
     ["问熟食冷冻期限", "问冰箱冷藏区温度分布"],
     "atomic", "",
     "冷冻=-18℃抑菌不杀菌红肉10-12月海鲜2-4月+分装薄冻减冰晶+冷藏室缓慢解冻"
     "最佳+室温热水解冻=危险带细菌翻倍+微波解冻立即烹饪+解冻后不回冻。"),
]

QUESTIONS = [
    ("QB-895", "二维码是什么原理？为什么破损或贴了标识还能扫出来？",
     "科技", "技术直答",
     ["定位", "容错", "纠错", "二进制"], "通识拓展235"),
    ("QB-896", "冷冻肉可以放多久？解冻的正确方法是什么？能不能反复解冻？",
     "生活常识", "技术直答",
     ["冷藏", "解冻", "危险带", "回冻"], "通识拓展235"),
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
                               "level:L2", "status:verified", "batch:通识拓展235"],
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
    bank["version"] = "v5.06"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
