# -*- coding: utf-8 -*-
"""seed_common_387_cards.py · 通识拓展批次387知识卡+题库（幂等）

387：3 张新卡（斑马线与交通信号/刺绣/滑雪）+ 3 题（QB-1399~1401）。
KCCS 四要素+题干原句触发词。预检已过（QB-1399~1401 可用，三主题
题库 0 覆盖，卡库无同名卡——滑雪仅压强卡举例提及，主题不重复）。
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
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO", "SVM"}


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
    ("kp_card_zebra",
     "斑马线与交通信号",
     "交通安全知识点内容（人话接口）", "生活常识",
     "斑马线——人行横道的通行规则：①**由来**——白色平行粗条线横跨车道"
     "、形似斑马纹得名；理念可追溯到古罗马时代的跳石（人行步石）；②**"
     "通行规则**——行人从斑马线过街，信号灯绿灯亮时通行；「机动车礼让"
     "斑马线」是法定义务——遇行人正在通过时不停车让行的会被记分罚款；"
     "③**信号灯口诀**——红灯停、绿灯行、黄灯亮了等一等；黄灯是「清空"
     "路口」的过渡信号，不是加速抢行的信号；④**安全习惯**——过街收起"
     "手机不看屏幕、先看左再看右确认车停稳再走；夜间或雨天穿亮色衣物更"
     "醒目；⑤**其他标线**——黄色实线禁停、虚实线可临时跨越（虚线侧）"
     "、导流线禁止停车压线。",
     ["斑马线怎么来的", "机动车礼让斑马线", "黄灯亮了能不能走",
      "过马路安全", "交通标线含义", "红绿灯规则"],
     ["问交通标志", "问行车安全"],
     "atomic", "",
     "斑马线=白色平行粗条形似斑马纹源自古罗马跳石+行人过街通道机动车"
     "礼让是法定义务不让记分罚款+红灯停绿灯行黄灯是清空路口非抢行+过"
     "街不看手机先左后右+黄实线禁停虚线侧可临时跨越。"),
    ("kp_card_embroidery",
     "刺绣与四大名绣",
     "传统工艺知识点内容（人话接口）", "传统文化",
     "刺绣——针线在织物上刺缀运针构成图案的传统工艺：①**历史**——中"
     "国刺绣至少两千余年（马王堆汉墓已有精美绣品出土）；②**四大名绣**"
     "——苏绣（江苏苏州，图案秀丽针法细腻，代表作双面绣：一块底料两面"
     "各成画面）、湘绣（湖南，狮虎写实见长）、粤绣（广东，构图饱满色彩"
     "浓烈，百鸟朝凤题材多）、蜀绣（四川，针法严谨片线光亮）；③**常见"
     "针法**——平针（平整铺绣）、乱针（交叉叠色似油画）、打籽（绕线成"
     "籽状凸点）；④**辨析**——刺绣用针线，织锦用织机（提花织造），是"
     "两种工艺；⑤**地位**——四大名绣均列入国家级非物质文化遗产名录。",
     ["四大名绣是哪四个", "苏绣湘绣粤绣蜀绣", "双面绣是什么",
      "刺绣有哪些针法", "刺绣和织锦区别", "中国刺绣历史"],
     ["问剪纸", "问陶瓷"],
     "atomic", "",
     "刺绣=针线刺缀成图案两千余年马王堆汉墓出土+四大名绣苏绣细腻双面"
     "绣湘绣狮虎粤绣浓烈蜀绣严谨+平针乱针打籽针法+刺绣针线织锦织机两"
     "种工艺+四大名绣均国家级非遗。"),
    ("kp_card_ski",
     "滑雪",
     "运动常识知识点内容（人话接口）", "体育常识",
     "滑雪——冬季运动代表项目：①**主要类型**——高山滑雪（从山上滑降"
     "下坡，速度与转弯技术）、越野滑雪（平地与起伏地形靠自身动力，被称"
     "「雪上马拉松」）、自由式滑雪（空中技巧/雪上技巧/大跳台等）；②**"
     "装备**——滑雪板、固定器（摔倒时自动脱开保护腿）、雪鞋、雪杖、"
     "头盔和雪镜（防风防紫外线，雪面反光极强必戴）；③**雪道分级**——"
     "绿道（初级缓坡）、蓝道（中级）、黑道（高级陡坡），量力选道是安全"
     "第一原则；④**摔倒要领**——向侧后方坐下、不要用手撑地（易伤腕）"
     "、失去控制就主动摔倒比硬扛安全；⑤**礼仪**——缆车排队、前方有人"
     "时后方滑行者责任避让、不停在雪道中间盲区。",
     ["滑雪有哪些类型", "滑雪装备有哪些", "雪道分级绿蓝黑",
      "滑雪摔倒怎么办", "为什么要戴雪镜", "滑雪安全"],
     ["问滑冰", "问冬奥会"],
     "atomic", "",
     "滑雪=高山滑降越野雪上马拉松自由式空中技巧+板固定器雪鞋杖头盔"
     "雪镜必戴防雪盲+雪道绿初级蓝中级黑高级量力选+摔倒向侧后坐不用手"
     "撑失控主动摔+缆车排队后方避让不停雪道中间。"),
]

QUESTIONS = [
    ("QB-1399", "斑马线是怎么来的？机动车不礼让斑马线会怎样？",
     "生活常识", "技术直答",
     ["斑马线", "礼让", "信号灯", "过街"], "通识拓展387"),
    ("QB-1400", "四大名绣是哪四个？双面绣是什么绝活？",
     "传统文化", "技术直答",
     ["刺绣", "四大名绣", "苏绣", "双面绣"], "通识拓展387"),
    ("QB-1401", "滑雪有哪些类型？雪道分级怎么区分？",
     "体育常识", "技术直答",
     ["滑雪", "雪道", "装备", "安全"], "通识拓展387"),
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
                               "level:L2", "status:verified", "batch:通识拓展387"],
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
    bank["version"] = "v6.57"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
