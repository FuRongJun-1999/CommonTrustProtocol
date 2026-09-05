# -*- coding: utf-8 -*-
"""seed_common_142_cards.py · 通识拓展批次142知识卡+题库（幂等）

142：文学-对联民俗/地理学-丹霞与雅丹地貌辨析/数学-彩票的概率真相
KCCS 四要素+题干原句触发词。三重预检：三主题双库零覆盖（对联与诗词格律卡
划界、丹霞雅丹为独立地貌主题、彩票概率全新）。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_couplet",
     "对联的规矩",
     "人文通识知识点内容（人话接口）", "文学",
     "对联（楹联）规矩四条：①**字数相等**——上下联字数完全相同；②**词性相"
     "对**——名对名、动对动（「天对地，雨对风，大陆对长空」《笠翁对韵》）；"
     "③**仄起平收**——**上联末字为仄声（普通话三四声），下联末字为平声（一二"
     "声）**：如上联「生意兴隆通四海」（海=仄）下联「财源茂盛达三江」（江="
     "平）；④**贴法**——面对大门，**上联贴右、下联贴左**（传统竖排从右往左"
     "读），横批从右往左写（现代印刷横批从左则联可从左贴）。历史：五代后蜀孟"
     "昶「新年纳余庆，嘉节号长春」被认为是最早的春联；王羲之「福无双至今朝"
     "至，祸不单行昨夜行」的巧联故事流传甚广。名联欣赏：昆明大观楼长联（180"
     "字，「天下第一长联」）。",
     ["对联怎么分上下联", "上联贴左边还是右边", "仄起平收是什么意思",
      "最早的春联是谁写的", "对联的要求", "横批怎么贴"],
     ["问诗词平仄格律（用诗词格律卡）", "问书法作品创作"],
     "atomic", "",
     "对联四规矩=字数相等+词性相对+仄起平收(上联末字三四声/下联末字一二声)+上联贴右下联贴左(面对门，传统从右读)；最早春联=五代孟昶「新年纳余庆」；大观楼 180 字长联=天下第一。"),
    ("kp_card_danxiayar",
     "丹霞与雅丹地貌辨析",
     "人文通识知识点内容（人话接口）", "地理学",
     "两个易混地貌（名字都带「丹/雅」但成因相反）：①**丹霞地貌**=红色砂砾岩"
     "层被**流水侵蚀**切割，形成赤壁丹崖方山石峰——名字源于广东韶关**丹霞山"
     "**（「色如渥丹，灿若明霞」）；典型：广东丹霞山、福建泰宁、贵州赤水（中"
     "国丹霞世界自然遗产）；甘肃张掖「七彩丹霞」实为彩色丘陵（多种矿物色层，"
     "严格说是另一类）；②**雅丹地貌**=干旱区湖积平原上松软沉积岩被**风力侵"
     "蚀**（偶尔暴雨冲刷）形成的平行土墩与沟槽（维吾尔语「陡峭的小丘」）——典"
     "型：新疆罗布泊地区、克拉玛依**乌尔禾「魔鬼城」**、甘肃敦煌雅丹国家地质"
     "公园。**口诀：丹霞水成（湿润区流水）、雅丹风成（干旱区风蚀）**——「丹"
     "霞水淋淋，雅丹风呼呼」。",
     ["丹霞地貌怎么形成的", "雅丹地貌和丹霞的区别", "魔鬼城是什么地貌",
      "张掖七彩丹霞", "丹霞山在哪里", "风蚀地貌有哪些"],
     ["问喀斯特地貌（溶蚀）", "问黄土高原沟壑成因"],
     "atomic", "",
     "丹霞=红色砂砾岩流水侵蚀成赤壁丹崖(广东丹霞山/泰宁/赤水)；雅丹=干旱区湖积层风力侵蚀成土墩沟槽(罗布泊/乌尔禾魔鬼城/敦煌)；口诀=丹霞水成雅丹风成；张掖七彩丘陵严格说非丹霞。"),
    ("kp_card_lottery",
     "彩票的概率真相",
     "基础科学知识点内容（人话接口）", "数学",
     "用概率看清彩票：①**头奖概率**——双色球头奖（6 红+1 蓝全中）概率约 "
     "**1/1772 万**，比「一年内被雷击中」还低一个数量级；②**期望值**——每种"
     "彩票的返奖率约 50% 左右（其余为公益金+发行费），即每花 2 元买一注，长期"
     "平均只能「收回」约 1 元——**买得越多亏得越稳**，指望买彩票致富在数学上"
     "不成立；③**赌徒谬误**——很多人研究「走势图」认为上期没出的号码「该出"
     "了」：错！每期开奖是**独立事件**，机器没有记忆，上期号码对下期概率零影"
     "响；④理性定位：彩票=小额娱乐+公益捐助（公益金用于福利/体育事业），量力"
     "而行，**勿借贷购彩勿沉迷**——「多买必亏，中头奖靠运气不靠技巧」。",
     ["中彩票头奖的概率是多少", "买彩票能赚钱吗", "彩票走势图有用吗",
      "什么是赌徒谬误", "双色球中奖概率", "彩票返奖率"],
     ["问具体投注策略（不存在必胜策略）", "问双色球规则细节"],
     "atomic", "",
     "彩票真相=双色球头奖约 1/1772 万(比雷击低)+返奖率约 50%(每 2 元长期期望回 1 元必亏)+每期独立无记忆(走势图=赌徒谬误)；定位=小额娱乐+公益捐助，量力勿沉迷。"),
]

QUESTIONS = [
    ("QB-690", "对联怎么区分上联和下联？面对大门时上联应该贴在哪一边？", "文学", "技术直答",
     ["仄声", "三四声", "平声", "右边", "右"], "通识拓展142"),
    ("QB-691", "丹霞地貌和雅丹地貌分别是由什么外力作用形成的？", "地理学", "技术直答",
     ["流水侵蚀", "流水", "风力侵蚀", "风力", "风蚀"], "通识拓展142"),
    ("QB-692", "双色球头奖的中奖概率大约是多少？为什么看「走势图」选号没有数学依据？", "数学", "技术直答",
     ["1772万", "千万", "独立", "赌徒谬误", "无记忆"], "通识拓展142"),
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
                               "level:L2", "status:verified", "batch:通识拓展142"],
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
    bank["version"] = "v4.15"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
