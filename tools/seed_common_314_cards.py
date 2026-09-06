# -*- coding: utf-8 -*-
"""seed_common_314_cards.py · 通识拓展批次314知识卡+题库（幂等）

314：建筑-吴哥窟/建筑-帕特农神庙（世界建筑奇迹新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1175/1176+双id可用）。
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
    ("kp_card_angkor",
     "吴哥窟",
     "建筑历史知识点内容（人话接口）", "历史",
     "吴哥窟——世界上最大的宗教建筑群：①**是什么**——柬埔寨吴哥王朝"
     "（约 12 世纪初苏耶跋摩二世主持）修建的印度教（毗湿奴）神庙，后转"
     "佛教寺院；高棉语意为「寺庙之都」；②**规模**——占地约 162 "
     "公顷，护城河宽 190 米环绕，整体象征印度教宇宙观（中心塔=须弥山，"
     "护城河=海洋）；③**建筑特色**——全部用砂岩块垒砌（无灰浆，靠精密切"
     "割咬合），浮雕壁画近 2000 平方米（史诗《摩诃婆罗多》等场景），回廊"
     "立面朝西（罕见——多数印度教神庙朝东）；④**失落与重现**——16 世纪"
     "后逐渐被丛林吞没，1860 年法国博物学家穆奥「重新发现」，轰动欧洲；"
     "⑤**国旗上的建筑**——柬埔寨国旗中央就是吴哥窟剪影；⑥**水利之谜**"
     "——吴哥王朝庞大的水利系统（水库运河）支撑百万人口，系统崩溃疑是"
     "王朝衰落原因之一。",
     ["吴哥窟在哪里", "吴哥窟是谁建的", "吴哥窟为什么朝西",
      "吴哥窟浮雕", "吴哥窟失落", "柬埔寨国旗"],
     ["问蒲甘佛塔", "问东南亚史"],
     "atomic", "",
     "吴哥窟=12世纪初苏耶跋摩二世毗湿奴神庙后转佛寺+世界最大宗教建筑群"
     "162公顷护城河190m+象征须弥山宇宙观+砂岩无灰浆精密切割+浮雕近"
     "2000㎡摩诃婆罗多+罕见朝西+丛林吞没1860穆奥重发现+国旗剪影+水利"
     "系统崩溃疑致衰落。"),
    ("kp_card_parthenon",
     "帕特农神庙",
     "建筑历史知识点内容（人话接口）", "历史",
     "帕特农神庙——古典建筑的黄金标准：①**背景**——公元前 447-432 年"
     "建于雅典卫城，供奉雅典娜（雅典城守护神），庆祝希波战争胜利，主持者"
     "政治家伯里克利+雕塑家菲狄亚斯；②**视觉纠偏魔法**——整座神庙没有"
     "一条真正的直线：柱子中段微鼓（卷杀工艺，抵消视觉凹陷）、柱身"
     "向内倾斜、基座微弧——肉眼看却笔直挺拔（2500 年前的视错觉科学）；"
     "③**多立克柱式**——粗壮简洁无柱础，柱高约为底径的 5.5 倍（黄金感）；"
     "④**雕塑巅峰**——东山墙雅典娜诞生/西山墙波塞冬争城+柱廊内浮雕带"
     "（泛雅典娜节游行，现藏大英博物馆的「埃尔金石雕」争议）；⑤**命运"
     "多舛**——先后被改教堂/清真寺，1687 年威尼斯炮弹引爆土耳其军火库"
     "致大损，200 年来修复争议不断；⑥**地位**——「多立克柱式最高成就+"
     "黄金比例的化身」，西方建筑教育的第一课。",
     ["帕特农神庙在哪里", "帕特农神庙供奉谁", "帕特农神庙没有直线",
      "多立克柱式", "埃尔金石雕", "雅典卫城"],
     ["问罗马柱式对比", "问希腊雕塑"],
     "atomic", "",
     "帕特农=前447-432雅典卫城供奉雅典娜庆希波胜利+伯里克利菲狄亚斯+"
     "无直线视觉纠偏(卷杀柱微鼓基座微弧)+多立克柱式5.5倍+泛雅典娜"
     "浮雕带埃尔金石雕争议+1687炮弹引爆军火库大损+西方建筑教育第一课。"),
]

QUESTIONS = [
    ("QB-1175", "吴哥窟在哪里？它是什么宗教的建筑？", "历史", "技术直答",
     ["柬埔寨", "吴哥", "印度教", "佛教"], "通识拓展314"),
    ("QB-1176", "帕特农神庙供奉的是谁？它的建筑有什么视觉奥秘？", "历史", "技术直答",
     ["雅典娜", "卫城", "视觉", "柱式"], "通识拓展314"),
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
                               "level:L2", "status:verified", "batch:通识拓展314"],
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
    bank["version"] = "v5.84"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
