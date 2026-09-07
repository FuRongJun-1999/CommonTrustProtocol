# -*- coding: utf-8 -*-
"""seed_common_496_cards.py · 通识拓展批次496知识卡+题库（幂等）

496：3 张新卡·石窟园林收尾（麦积山 kp_card_maijishan / 豫园
    kp_card_yuyuan / 四大石窟总括 kp_card_fourgrottoes）。
预检已过（QB-1720~1722 可用，三主题题库卡库零独立卡）。
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
    ("kp_card_maijishan",
     "麦积山石窟",
     "考古常识知识点内容（人话接口）", "历史与文明",
     "麦积山石窟——甘肃天水的「东方雕塑陈列馆」：①**位置与得名**——"
     "天水秦岭西端，山形如农家麦垛而得名；②**开凿**——始于后秦（十六"
     "国时期），北魏、北周、隋唐历代续建，现存洞窟 221 个、泥塑石雕万"
     "余身；③**最大特色**——以泥塑见长（崖面多为砂砾岩不宜精雕，古人"
     "以泥塑代石雕），塑像秀美生动、贴近生活；④**名品**——第 133 窟"
     "小沙弥像（纯真微笑被誉为「东方微笑」）、散花楼（第 4 窟）；⑤**地"
     "位**——中国四大石窟之一，2010 年作为丝绸之路文化遗产点列入《世"
     "界遗产名录》。",
     ["麦积山石窟在哪里", "东方雕塑陈列馆", "麦积山是哪个朝代",
      "东方微笑小沙弥", "麦积山泥塑", "天水石窟"],
     ["问莫高窟", "问云冈石窟"],
     "atomic", "",
     "麦积山石窟=甘肃天水山形如麦垛得名+后秦始凿北魏北周隋唐续建221窟"
     "泥塑石雕万余身+泥塑见长砂砾岩不宜精雕以泥代石秀美生动+第133窟小"
     "沙弥东方微笑散花楼+四大石窟之一2010年丝绸之路遗产点列入世界遗"
     "产。"),
    ("kp_card_yuyuan",
     "豫园",
     "园林建筑知识点内容（人话接口）", "传统文化",
     "豫园——上海老城厢的江南名园：①**由来**——始建于明嘉靖年间"
     "（1559 年起），由潘允端为孝敬父母而建，「豫」通「愉」，取「豫悦"
     "老亲」之意；②**地位**——江南古典园林代表，素有「奇秀甲江南」之"
     "誉，与老城隍庙、豫园商城构成上海最有人气的传统街区；③**镇园之宝"
     "**——玉玲珑：一块太湖石，瘦皱漏透俱全，相传为宋代花石纲遗物，"
     "是江南三大名石之一；④**看点**——大假山（明代张南阳叠山遗存）、"
     "点春堂（小刀会起义指挥部旧址）、龙墙花窗曲廊；⑤**身份**——全国"
     "重点文物保护单位（1982）。",
     ["豫园在哪里", "豫园是谁建的", "玉玲珑", "豫园有什么好玩的",
      "奇秀甲江南", "上海园林"],
     ["问苏州园林", "问城隍庙"],
     "atomic", "",
     "豫园=上海老城厢明嘉靖1559年潘允端为孝敬父母而建豫悦老亲+江南古"
     "典园林代表奇秀甲江南+镇园之宝玉玲珑太湖石瘦皱漏透宋代花石纲遗物"
     "江南三大名石+大假山张南阳叠山点春堂小刀会旧址龙墙曲廊+1982年全"
     "国重点文保。"),
    ("kp_card_fourgrottoes",
     "中国四大石窟",
     "考古常识知识点内容（人话接口）", "历史与文明",
     "中国四大石窟——佛教石刻艺术的四座高峰：①**莫高窟**（甘肃敦煌）"
     "——规模最大：洞窟 735 个、壁画 4.5 万平方米，以壁画与彩塑著称"
     "，1987 年列入世界遗产；②**云冈石窟**（山西大同）——北魏皇家工"
     "程，昙曜五窟与第 20 窟露天大佛，2001 年列入世界遗产；③**龙门石"
     "窟**（河南洛阳）——奉先寺卢舍那大佛，唐代雕塑巅峰，2000 年列入"
     "世界遗产；④**麦积山石窟**（甘肃天水）——以泥塑著称，「东方雕塑"
     "陈列馆」，2010 年随丝绸之路廊道列入世界遗产；⑤**记忆口诀**——"
     "「莫云龙麦，壁画皇家塑像泥塑」，由西向东依次为敦煌→天水→大同"
     "→洛阳。",
     ["四大石窟是哪四个", "四大石窟分别在哪里", "中国石窟排名",
      "莫高窟云冈龙门麦积山", "石窟艺术"],
     ["问乐山大佛", "问大足石刻"],
     "atomic", "",
     "四大石窟=莫高窟甘肃敦煌规模最大735窟壁画4.5万平方米1987世遗+云"
     "冈山西大同北魏皇家昙曜五窟2001世遗+龙门河南洛阳卢舍那大佛2000世"
     "遗+麦积山甘肃天水泥塑东方雕塑陈列馆2010世遗+口诀莫云龙麦壁画皇"
     "家塑像泥塑。"),
]

QUESTIONS = [
    ("QB-1720", "麦积山石窟有什么特色？为什么被称为东方雕塑陈列馆？",
     "历史常识", "技术直答",
     ["麦积山", "泥塑", "天水", "东方雕塑"], "通识拓展496·新卡"),
    ("QB-1721", "豫园是谁建的？镇园之宝是什么？",
     "传统文化", "技术直答",
     ["豫园", "潘允端", "玉玲珑", "上海"], "通识拓展496·新卡"),
    ("QB-1722", "中国四大石窟是哪四个？分别在哪里？",
     "历史常识", "技术直答",
     ["四大石窟", "莫高窟", "云冈", "龙门", "麦积山"], "通识拓展496·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展496"],
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
    bank["version"] = "v7.61"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
