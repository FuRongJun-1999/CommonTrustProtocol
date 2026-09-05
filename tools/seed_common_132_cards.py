# -*- coding: utf-8 -*-
"""seed_common_132_cards.py · 通识拓展批次132知识卡+题库（幂等）

132：生活常识-食品标签与营养成分表/历史学-中国茶文化/地理学-世界首都综合
KCCS 四要素+题干原句触发词。出卡前 id+触发词双预检（书法撞卡 QB-182 已换题）。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_foodlabel",
     "食品标签与营养成分表",
     "生活常识知识点内容（人话接口）", "生活常识",
     "看懂食品包装三件事：①**配料表**——按加入量递减排序，排位越靠前含量越"
     "高（排第一位的是主要原料；氢化植物油/植脂末靠前要警惕反式脂肪酸）；②**营"
     "养成分表**——强制标示「1+4」：能量+蛋白质、脂肪、碳水化合物、**钠**四项"
     "核心营养素；**NRV%**=营养素参考值百分比，指每 100g（ml）或每份食品中该"
     "营养素占全天推荐摄入量的百分比（钠 NRV 50%=吃这份就占全天盐量一半）；③"
     "**日期与声称**——保质期内是最佳食用期（不是过期即变质）；「无糖」标准为"
     "含糖≤0.5g/100g(ml)，「0 脂肪」为≤0.5g/100g，「高钙」为≥30%NRV 每"
     "100g。买食品先看配料表和钠含量——很多「健康食品」钠 NRV 高得惊人。",
     ["营养成分表怎么看", "NRV% 是什么意思", "无糖食品的标准",
      "食品保质期和保存期的区别", "配料表排序规则", "买食品看什么标签"],
     ["问食品安全标志（QS/绿色食品，用食品安全卡）", "问具体品牌推荐"],
     "atomic", "",
     "食品标签三看=配料表（递减排·首位主料）+营养成分表 1+4（能量/蛋白/脂肪/碳水/钠，NRV%=占全天推荐量比，钠 50%=半天盐量）+声称标准（无糖≤0.5g/100g、0 脂肪同限、高钙≥30%NRV）；保质期=最佳食用期非变质线。"),
    ("kp_card_teaculture",
     "中国茶文化与六大茶类",
     "人文通识知识点内容（人话接口）", "历史学",
     "中国是茶树原产地，「茶兴于唐、盛于宋」——唐代陆羽著《茶经》，是世界第一"
     "部茶叶专著，陆羽被尊为「茶圣」。**六大茶类按发酵（氧化）程度分类**：①绿"
     "茶——不发酵（杀青止酵），清汤绿叶，如西湖龙井、碧螺春、黄山毛峰；②白"
     "茶——微发酵，如白毫银针；③黄茶——轻发酵（闷黄），如君山银针；④青茶"
     "（乌龙茶）——半发酵，绿叶红镶边，如铁观音、大红袍、凤凰单丛；⑤红茶——"
     "全发酵，红汤红叶，如祁门红茶、正山小种；⑥黑茶——后发酵（微生物参与），"
     "如云南普洱（熟茶）、安化黑茶。发酵越深茶性越温和（绿茶偏寒凉，红茶黑茶"
     "暖胃）。茶马古道：川滇茶叶换西藏马匹的古代贸易通道。世界饮茶风俗：英国"
     "下午茶、日本茶道（源由中国传去演变）。",
     ["中国六大茶类怎么分类", "绿茶和红茶的区别", "茶圣是谁", "陆羽茶经",
      "普洱茶属于什么茶", "西湖龙井铁观音大红袍"],
     ["问茶艺冲泡技法", "问咖啡文化"],
     "atomic", "",
     "六大茶类按发酵（氧化）度分：绿茶不发酵（龙井/碧螺春）→白黄微轻→乌龙半发酵（铁观音/大红袍）→红茶全发酵（祁门/正山小种）→黑茶后发酵（普洱熟茶）；发酵深茶性温和；茶圣陆羽《茶经》=世界首部茶专著；茶马古道=以茶易马通道。"),
    ("kp_card_worldcapitals",
     "世界首都与定都趣知识",
     "人文通识知识点内容（人话接口）", "地理学",
     "首都=国家中央政府所在地（政治中心，不一定最大城市）。有趣的定都案例："
     "①**堪培拉**是澳大利亚首都——悉尼与墨尔本争当首都相持不下，1908 年折中"
     "在两城之间新建首都（类似加拿大多伦多/蒙特利尔/魁北克之争→定都**渥太"
     "华**，英语区法语区折中）；②**巴西利亚**——1960 年巴西从里约热内卢迁都"
     "内陆高原，为开发内陆+平衡人口，城市规划像一架飞机，世界遗产；③华盛顿"
     "哥伦比亚特区——美国首都，不属于任何州（联邦直辖区）；④荷兰**法定首都"
     "是阿姆斯特丹，但国王与政府在海牙**工作；⑤日本法律上未明确首都（东京为"
     "事实首都）；⑥缅甸 2005 年从仰光迁都**内比都**。全球最大首都圈=日本东京"
     "圈（约 3700 万人）。",
     ["澳大利亚的首都是哪", "堪培拉为什么是首都", "巴西的首都是哪座城市",
      "荷兰的首都是哪里", "渥太华是哪国首都", "日本的首都法律上怎么定"],
     ["问最大城市排名", "问迁都的利弊分析"],
     "atomic", "",
     "首都=中央政府所在地非必最大城：堪培拉=悉尼墨尔本之争折中新建；渥太华=英法折中；巴西利亚 1960 迁内陆（城如飞机）；华盛顿=联邦直辖区不属任何州；荷兰法定首都阿姆斯特丹政府在海牙；日本法律未明确（东京事实首都）；缅甸 2005 迁内比都。"),
]

QUESTIONS = [
    ("QB-662", "食品包装上营养成分表中的 NRV% 表示什么含义？", "生活常识", "技术直答",
     ["营养素参考值", "全天", "占比", "推荐摄入量"], "通识拓展132"),
    ("QB-663", "中国六大茶类是按什么标准分类的？绿茶和红茶的根本区别是什么？", "历史学", "技术直答",
     ["发酵", "不发酵", "全发酵", "氧化"], "通识拓展132"),
    ("QB-664", "澳大利亚的首都是哪座城市？为什么不是悉尼？", "地理学", "技术直答",
     ["堪培拉", "折中", "墨尔本"], "通识拓展132"),
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
                               "level:L2", "status:verified", "batch:通识拓展132"],
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
                   "added": "2026-09-04"})
        added += 1
    bank["version"] = "v4.5"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
