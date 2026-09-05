# -*- coding: utf-8 -*-
"""seed_common_172_cards.py · 通识拓展批次172知识卡+题库（幂等）

172：生活常识三连——保鲜膜材质与加热/牙膏色条辟谣/冰箱除味
KCCS 四要素+题干原句触发词。三重预检：三主题双库零覆盖（冰箱除味为
fridgestore 卡 negs 显式留位对接）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_clingfilm",
     "保鲜膜能进微波炉吗",
     "生活常识知识点内容（人话接口）", "生活常识",
     "保鲜膜分材质，能不能加热看标识：①**PE（聚乙烯）**——最常见食品保鲜膜，"
     "安全性好但**耐温有限**（约 110°C），标「可微波」才可短时微波加热；②**"
     "PVDC（聚偏二氯乙烯）**——耐温更高、阻隔性最好，可微波；③**PVC（聚氯乙"
     "烯）**——便宜但含增塑剂，**遇高温油脂易迁移**，不可加热、别贴热食/油"
     "炸食品（识别：PVC 膜透明度高手感黏、PE 膜略雾不易粘手，最可靠是看底部"
     "数字标识「5 号 PP」微波餐盒安全）。**使用要点**：微波加热要么不用膜、要"
     "么留缝（密封蒸汽会爆开）、别贴着食物尤其**油脂多的菜**（油脂高温加速有"
     "害物迁移）；蔬菜包膜冷藏不宜超 12 小时（闷出亚硝酸盐与滋生菌）。买时认"
     "「食品用/可微波」标注。",
     ["保鲜膜可以加热吗", "PE保鲜膜能进微波炉吗", "PVC保鲜膜危害",
      "保鲜膜哪个牌子食品级", "微波炉加热要盖保鲜膜吗"],
     ["问塑料回收数字标识", "问食品标签（用标签卡）"],
     "atomic", "",
     "保鲜膜按材质：PE 常见耐温有限标可微波才短时加热/PVDC 耐温高可微波/PVC 含增塑剂不可加热避贴热油食；微波留缝防蒸汽爆、蔬果包膜冷藏≤12h；认「食品用/可微波」与 5 号 PP 标识。"),
    ("kp_card_toothpastestrip",
     "牙膏尾部色条的谣言",
     "生活常识知识点内容（人话接口）", "生活常识",
     "谣言：「牙膏尾部色条是成分密码——绿色=纯天然、黑色=全化学成分」——**"
     "纯属谣言**。真相：①尾部色块叫「**电眼定位点/印刷标记**」——自动化灌装"
     "生产线上，**光电传感器扫描色块定位**，让机器准确完成封尾与裁切（色条要"
     "与管身底色反差大，所以常见黑/红/蓝/绿）；②色条颜色只取决于**印刷工艺需"
     "要**（与管身图案颜色区分开即可），与成分**毫无关系**；③牙膏成分好不好"
     "看**配料表**：摩擦剂（碳酸钙/水合硅石）、氟化物（防龋——含氟量标注）、"
     "保湿剂、发泡剂等；④同类谣言还有「瓶底三角形数字决定毒性」夸大版、「洗"
     "发水瓶色条」版——识别套路：**凡说包装上某标记=成分/毒性密码的，基本都"
     "是谣言**（成分必须看配料表/成分表，这是法定标注位置）。",
     ["牙膏尾部色条是什么", "绿色牙膏条纯天然", "牙膏色条颜色含义",
      "牙膏成分怎么看", "电眼定位点"],
     ["问食品标签（用标签卡）", "问含氟牙膏（用牙齿卡）"],
     "atomic", "",
     "牙膏尾部色条=电眼定位点（生产线光电扫描定位封尾裁切），颜色只随印刷需要与成分无关——「绿=天然黑=化学」是谣言；成分看配料表（摩擦剂/氟化物/保湿剂）；识别套路=凡包装标记当成分密码的基本是谣言。"),
    ("kp_card_fridgeodor",
     "冰箱除味",
     "生活常识知识点内容（人话接口）", "生活常识",
     "冰箱异味根源=**食物串味+霉菌与滴水槽藏污**——治本三步：①**清空擦洗**："
     "断电清空，内壁用稀释小苏打水/中性洗洁精擦拭（密封条缝隙用旧牙刷+小苏打"
     "膏），滴水孔疏通；②**除味剂**：活性炭包（吸附最强，用后晒干可复用几次"
     "）、小苏打粉敞口盒（吸酸臭）、柠檬片/茶叶渣/咖啡渣（清香掩盖型，需常"
     "换）；③**防复发**：食物**密封/带盖**存放（剩菜覆膜）、气味大的（榴莲/"
     "臭豆腐/葱姜）双重密封、定期（每月）清过期食品。注意：不要用消毒液擦内胆"
     "（残留污染食物）；除味剂是辅助，**源头密封+定期清理**才是根本。",
     ["冰箱有异味怎么去除", "冰箱除味剂哪种好", "小苏打除冰箱异味",
      "活性炭冰箱除味", "冰箱多久清理一次"],
     ["问冰箱储存（用冰箱储存卡）", "问消毒柜"],
     "atomic", "",
     "冰箱除味治本三步=断电清空小苏打水擦洗（密封条牙刷刷）+活性炭包/小苏打盒吸味（柠檬茶叶只掩盖需常换）+食物密封存放大味品双封；勿用消毒液擦内胆；源头密封+月清理才是根本。"),
]

QUESTIONS = [
    ("QB-767", "PE、PVDC、PVC 三种保鲜膜哪些可以进微波炉加热？使用保鲜膜有什么注意事项？", "生活常识", "技术直答",
     ["PE", "PVDC", "PVC", "耐温", "增塑剂", "留缝"], "通识拓展172"),
    ("QB-768", "牙膏管尾部的色条是「成分密码」吗？绿色色条代表纯天然吗？", "生活常识", "技术直答",
     ["谣言", "电眼定位", "印刷标记", "配料表", "无关"], "通识拓展172"),
    ("QB-769", "冰箱有异味怎么去除？用什么除味剂效果最好？", "生活常识", "技术直答",
     ["活性炭", "小苏打", "柠檬", "擦洗", "密封"], "通识拓展172"),
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
                               "level:L2", "status:verified", "batch:通识拓展172"],
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
    bank["version"] = "v4.45"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
