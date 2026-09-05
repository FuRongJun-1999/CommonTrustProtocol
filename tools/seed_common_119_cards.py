# -*- coding: utf-8 -*-
"""seed_common_119_cards.py · 通识拓展批次119知识卡+题库（幂等）

119：物理学-测电笔/化学-长期饮用纯净水健康吗/地理学-世界的时区划分
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_testpen",
     "测电笔的原理与使用",
     "基础科学知识点内容（人话接口）", "物理学",
     "测电笔（试电笔）用于辨别火线与零线：①结构——笔尖金属体+高值电阻+氖管+"
     "弹簧+笔尾金属体；②使用——手**接触笔尾金属体**、笔尖接触被测导线：接触"
     "**火线**时氖管发光（火线-测电笔-人体-大地构成微弱回路，高值电阻限制电流"
     "在安全范围所以不会触电），接触零线不发光；③**绝不能**用手接触笔尖金属体"
     "（直接触电！）。用途：辨别火线零线、检查用电器外壳是否带电。安全提醒：使"
     "用前要在已知有电的线路上试测确认测电笔完好。数字测电笔可显示电压数值。",
     ["测电笔的原理和使用方法", "测电笔为什么不会触电", "测电笔怎么辨别火线",
      "测电笔为什么不能碰笔尖", "氖管发光说明什么", "使用测电笔的注意事项"],
     ["问验电笔与验电器区别", "问家庭电路故障排查"],
     "atomic", "",
     "测电笔=笔尖+高值电阻+氖管+笔尾金属体：手触笔尾·笔尖触线——氖管亮=火线(微弱回路安全·高阻限流)；**禁触笔尖**(直接触电)；用前先在已知火线验证完好。"),
    ("kp_card_purewater",
     "长期饮用纯净水健康吗",
     "生活常识知识点内容（人话接口）", "生活常识",
     "纯净水（蒸馏水/反渗透水）：去除了绝大多数杂质和矿物质的水。争议与共识：纯"
     "净水**不含有害物质也无矿物质**——人体矿物质主要来源是**食物**（约 90%），"
     "饮水提供的矿物质占比很小（膳食均衡者喝纯净水不会缺矿物质）。但特殊情况："
     "①婴幼儿（配方奶冲调建议用低矿水）；②高强度运动大量出汗（电解质流失——"
     "补运动饮料更合适）；③膳食不均衡者长期只喝纯净水理论上有微量元素摄入不足"
     "风险。综合建议：正常饮食者喝纯净水安全；选择矿泉水/自来水烧开也完全可以"
     "——关键是**保证饮水量**（1500-1700ml）和饮水卫生，水的种类不是健康决定因"
     "素。「纯净水刮骨」等说法无科学依据。",
     ["长期饮用纯净水健康吗", "纯净水和矿泉水的区别", "矿物质从哪里补充",
      "纯净水有副作用吗", "婴儿能用纯净水冲奶粉吗", "每天喝什么水最健康"],
     ["问饮用水标准 GB", "问电解质平衡复习"],
     "atomic", "",
     "纯净水=无杂质也无矿物质：人体矿物质 90% 来自食物·膳食均衡者喝纯净水安全；特殊=婴幼儿/大量出汗者注意电解质；关键=饮水量和卫生·水的种类非决定因素。"),
    ("kp_card_timezone24",
     "世界的时区划分",
     "人文通识知识点内容（人话接口）", "地理学",
     "时区划分原理：地球每 24 小时自转 360°，即每小时转 15°——全球按经度每 15°"
     "划为**一个时区**，共 **24 个时区**。以本初子午线（0° 经线，英国格林尼治天"
     "文台）为中央经线的时区为零时区（中时区），向东为东一区至东十二区，向西为"
     "西一区至西十二区，东十二区与西十二区重合于 180° 经线（国际日期变更线）。"
     "相邻时区相差 1 小时：东边时刻早（「东加西减」）——北京（东八区）比伦敦（零"
     "时区）早 8 小时。中国统一使用北京时间（东八区区时），但新疆实际位置在东五"
     "至东六区（作息比北京晚约 2 小时）。国际日期变更线大致沿 180° 经线，跨越它"
     "日期加一天或减一天。",
     ["世界划分为多少个时区", "时区划分的依据", "北京和伦敦时差",
      "国际日期变更线", "为什么新疆作息比北京晚", "东八区是什么意思"],
     ["问夏令时原理", "问地方时与区时区别"],
     "atomic", "",
     "时区=每 15° 一个·共 24 个(0° 中央经线=格林尼治)：东加西减·相邻差 1 小时；北京东八区比伦敦早 8 小时；中国统一北京时间（新疆实际晚 2h）；日界线沿 180°。"),
]

QUESTIONS = [
    ("QB-611", "测电笔的原理和使用方法", "物理学", "技术直答",
     ["氖管", "火线"], "通识拓展119"),
    ("QB-612", "长期饮用纯净水健康吗", "化学", "技术直答",
     ["安全", "矿物质", "食物"], "通识拓展119"),
    ("QB-613", "世界划分为多少个时区", "地理学", "技术直答",
     ["24", "二十四"], "通识拓展119"),
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
                               "level:L2", "status:verified", "batch:通识拓展119"],
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
    bank["version"] = "v3.3"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
