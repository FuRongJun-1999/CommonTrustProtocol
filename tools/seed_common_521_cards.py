# -*- coding: utf-8 -*-
"""seed_common_521_cards.py · 通识拓展批次521知识卡+题库（幂等）

521：3 张新卡·市井风物域（招幌行当 kp_card_zhaohuang /
    老字号 kp_card_laozihao / 传统玩具 kp_card_wanju——
    id 与语义等价卡名双重确认三主题零覆盖；风筝 QB-1034 已有跳过）。
预检已过（QB-1795~1797 可用）。
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
    ("kp_card_zhaohuang",
     "招幌与市井行当",
     "民俗知识点内容（人话接口）", "传统文化",
     "招幌与市井行当——古人的商业视觉语言：①**招幌**——「幌子」（悬"
     "挂的实物或旗帘）与「招牌」（题字的牌匾）合称：酒旗最古老（杜牧"
     "「水村山郭酒旗风」），《清明上河图》里满目招幌；②**行当标识**——"
     "药铺悬葫芦（「悬壶济世」）、当铺写斗大「当」字、理发铺挂布幡、"
     "油坊挂油葫芦——不识字也能一眼认行；③**行商吆喝**——磨剪子戗"
     "菜刀、卖糖葫芦的叫卖是流动的市声；④**行话与规矩**——各行当有"
     "自己的行话、师承与保护价格默契；⑤**语义引申**——「幌子」后来"
     "泛指借以遮掩的名义（「打幌子」），成为汉语常用比喻。",
     ["幌子是什么", "招幌", "悬壶济世", "酒旗",
      "清明上河图招幌", "打幌子什么意思"],
     ["问庙会与灯谜", "问商帮与会馆"],
     "atomic", "",
     "招幌行当=幌子悬挂实物招牌题字牌匾+酒旗最古老水村山郭酒旗风清明"
     "上河图满目招幌+药铺葫芦当铺大当字不识字认行+行商吆喝磨剪子戗菜"
     "刀市声+幌子引申遮掩名义打幌子比喻。"),
    ("kp_card_laozihao",
     "老字号",
     "商业史知识点内容（人话接口）", "传统文化",
     "老字号——几代人攒下的金字招牌：①**同仁堂**——1669 年乐显扬创"
     "建，古训「炮制虽繁必不敢省人工，品味虽贵必不敢减物力」；②**剪刀"
     "双雄**——杭州张小泉（明末创）与北京王麻子，剪刀质量立身；③**"
     "餐饮绸布**——全聚德（1864 年北京烤鸭）、瑞蚨祥（绸布）、六必居"
     "（明代酱园）；④**内联升**——1853 年创，朝靴与千层底布鞋，「履"
     "备升堂」；⑤**共同基因**——选料实、工艺严、口碑传、字号在——"
     "老字号的核心资产是「信」字，与老残游记里票号命运同理：乱世最易"
     "失，盛世最值钱。",
     ["老字号有哪些", "同仁堂", "全聚德", "张小泉",
      "六必居", "炮制虽繁必不敢省人工"],
     ["问商帮与会馆", "问镖局与票号"],
     "atomic", "",
     "老字号=同仁堂1669乐显扬炮制虽繁必不敢省人工品味虽贵不减物力+剪"
     "刀双雄张小泉杭州明末王麻子北京+全聚德1864烤鸭瑞蚨祥绸布六必居明"
     "代酱园+内联升1853千层底+核心资产信字选料实工艺严口碑传。"),
    ("kp_card_wanju",
     "传统玩具",
     "民俗知识点内容（人话接口）", "传统文化",
     "传统玩具——没有电池的智慧游戏：①**七巧板**——源于宋代「燕几"
     "图」（宴几拼桌），七块板拼千形，现代几何启蒙鼻祖；②**九连环**——"
     "九环相扣的解环玩具，战国已有记载，完全解开需三百余步，训练耐心"
     "与递归思维；③**兔儿爷**——北京中秋泥塑，月宫玉兔化身的守护神，"
     "金盔金甲骑虎坐莲；④**空竹与陀螺**——抖空竹嗡嗡作响（庙会常客）"
     "，抽陀螺「打尜尜」是北国冬日街景；⑤**不倒翁与拨浪鼓**——不倒"
     "翁重心在下永不倒（寓意跌倒再起），拨浪鼓咚咚声是最早的婴儿玩具"
     "之一；⑥**共性**——就地取材（泥、木、竹、纸），动手动脑，是"
     "「玩中学」的祖先。",
     ["传统玩具有哪些", "七巧板", "九连环", "兔儿爷",
      "空竹", "不倒翁原理"],
     ["问风筝", "问皮影戏"],
     "atomic", "",
     "传统玩具=七巧板源于宋代燕几图七板拼千形几何启蒙+九连环战国记载"
     "解环三百余步递归思维+兔儿爷北京中秋泥塑玉兔守护+空竹嗡嗡陀螺冬"
     "景+不倒翁重心在下拨浪鼓最早婴儿玩具+泥木竹纸就地取材玩中学。"),
]

QUESTIONS = [
    ("QB-1795", "「幌子」是什么？为什么药铺门口挂葫芦？",
     "传统文化", "技术直答",
     ["幌子", "招幌", "悬壶", "葫芦"], "通识拓展521·新卡"),
    ("QB-1796", "同仁堂是哪年创立的？它的制药古训是什么？",
     "传统文化", "技术直答",
     ["同仁堂", "1669", "炮制虽繁", "乐显扬"], "通识拓展521·新卡"),
    ("QB-1797", "七巧板和九连环各有什么来历？锻炼什么能力？",
     "传统文化", "技术直答",
     ["七巧板", "九连环", "燕几图", "益智"], "通识拓展521·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展521"],
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
    bank["version"] = "v7.86"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
