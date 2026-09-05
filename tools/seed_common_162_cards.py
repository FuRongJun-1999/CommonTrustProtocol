# -*- coding: utf-8 -*-
"""seed_common_162_cards.py · 通识拓展批次162知识卡+题库（幂等）

162：历史学-永乐大典/数学-斐波那契数列/生活常识-切洋葱为什么流泪
KCCS 四要素+题干原句触发词。三重预检：永乐大典/斐波那契双库零覆盖；洋葱命
中为宠物毒理卡（猫狗禁食），切洋葱流泪的人体化学角度未覆盖。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_yongledadian",
     "《永乐大典》",
     "人文通识知识点内容（人话接口）", "历史学",
     "《永乐大典》=明永乐年间敕修的类书（百科全书式汇编）：**解缙**等主持，"
     "**1408 年**成书——**22877 卷、11095 册、约 3.7 亿字**，辑入先秦至明初图"
     "书七八千种，被誉为「**世界有史以来最大的百科全书**」（大英百科全书评"
     "语）。命运多舛：①**正本下落成谜**——明亡后消失（殉葬嘉靖帝陵？毁于乾"
     "清宫大火？至今无定论）；②**副本**清代藏翰林院，经战乱（英法联军/八国"
     "联军）被抢掠焚毁散佚——今存约 **400 余册、800 余卷**，不足原书 4%，散"
     "落在 8 个国家和地区（国家图书馆藏 160 余册为最）。与清代《四库全书》对"
     "比：大典=「抄整部书」保存原貌（辑佚宝藏——很多古书靠它辑出），四库="
     "「删改重编」服务于思想统制。近年「大典数字化」持续推进。",
     ["永乐大典是谁编的", "永乐大典有多少卷", "永乐大典正本去哪了",
      "世界最大的百科全书", "永乐大典和四库全书", "辑佚是什么"],
     ["问四库全书详情", "问郑和下西洋（同永乐朝）"],
     "atomic", "",
     "永乐大典=1408 明解缙等编：22877 卷 11095 册 3.7 亿字=世界最大百科全书；正本下落成谜（殉葬/焚毁说）、副本战乱散佚存约 400 册不足 4% 分藏 8 国；抄整部书=辑佚宝藏 vs 四库删改重编；数字化推进中。"),
    ("kp_card_fibonacci",
     "斐波那契数列",
     "基础科学知识点内容（人话接口）", "数学",
     "**斐波那契数列**：1, 1, 2, 3, 5, 8, 13, 21, 34, 55……**每一项=前两项之"
     "和**。来历：意大利数学家斐波那契 1202 年《计算之书》的「**兔子问题**」"
     "——一对兔子每月生一对小兔（小兔长大后再生），一年后有多少对？递推关系"
     "f(n)=f(n-1)+f(n-2)。**神奇之处**：①**黄金分割的化身**——相邻两项之比 "
     "5/8≈0.625、8/13≈0.615、55/89≈0.618……越来越逼近黄金比例 **0.618**；"
     "②**自然界的隐藏规律**——向日葵种子螺旋 34/55、松果鳞片 8/13、花瓣数多"
     "为 3/5/8/13/21（都是斐波那契数——植物生长的最优排列「黄金角」）；③**"
     "应用**——斐波那契查找算法/股市「斐波那契回撤位」/摄影与美术构图"
     "。与黄金分割卡（比值 0.618 的几何定义）互补：一个讲数列递推、一个讲比例"
     "本身——两者极限重合。",
     ["斐波那契数列是什么", "兔子问题", "1 1 2 3 5 8",
      "斐波那契与黄金分割", "向日葵种子斐波那契", "花瓣数斐波那契"],
     ["问黄金分割（用黄金分割卡）", "问数列求和技巧"],
     "atomic", "",
     "斐波那契数列 1,1,2,3,5,8,13…每项=前两项和（1202 年兔子问题）；相邻项比逼近黄金比例 0.618；自然界向日葵螺旋 34/55、花瓣 3/5/8/13/21 均为斐波那契数（黄金角最优排列）；应用=查找算法/回撤位/构图。"),
    ("kp_card_oniontears",
     "切洋葱为什么流泪",
     "基础科学知识点内容（人话接口）", "化学",
     "切洋葱流泪=洋葱的**化学防御**：①洋葱细胞被刀切开时，细胞里的**蒜氨酸酶**"
     "（一种酶）与**氨基酸亚砜**相遇，快速反应生成**催泪因子**（丙硫醛-S-氧"
     "化物，一种挥发性的硫化合物）；②它飘到眼睛里**刺激角膜神经末梢**（它还"
     "能在眼表微量生成硫酸等刺激物），泪腺立刻大量分泌泪水「冲洗」刺激物——"
     "这是保护机制，不是难过。**少流泪技巧**：①**切前冷藏 15 分钟**（低温酶"
     "活性低、挥发物少）；②**接近水面切**或沾点水（催泪因子水溶性，先被水吸"
     "收）；③**刀要锋利**（切口整齐细胞破坏少、酶反应少）；④开抽油烟机/戴护"
     "目镜（终极方案）；⑤从根部最后切（**芽尖部位催泪物质浓度最高**留到最后"
     "处理）。冷知识：洋葱与大蒜同属百合科（葱属），「辣眼睛」能力是它防备动"
     "物啃食的进化武器——但对人类烹饪香味的贡献更大。",
     ["切洋葱为什么流泪", "怎么切洋葱不辣眼睛", "洋葱催泪因子",
      "冷藏洋葱再切", "蒜氨酸酶"],
     ["问大蒜素（蒜的化学）", "问宠物为什么不能吃洋葱（毒理不同）"],
     "atomic", "",
     "切洋葱流泪=细胞破裂后蒜氨酸酶与氨基酸亚砜生成催泪因子（挥发性硫化合物）刺激角膜→泪腺冲洗保护反应；减泪=冷藏 15min 降酶活+近水面切（因子水溶）+锋利刀+留根部最后切；这是洋葱防啃食的进化武器。"),
]

QUESTIONS = [
    ("QB-741", "《永乐大典》成书于哪个朝代？为什么说它是「世界最大的百科全书」？", "历史学", "技术直答",
     ["明朝", "明代", "永乐", "解缙", "22877卷", "3.7亿字"], "通识拓展162"),
    ("QB-742", "斐波那契数列的规律是什么？它与黄金分割有什么联系？", "数学", "技术直答",
     ["前两项之和", "1,1,2,3,5,8", "黄金分割", "0.618", "兔子"], "通识拓展162"),
    ("QB-743", "切洋葱时为什么会流眼泪？有哪些减少流泪的小技巧？", "化学", "技术直答",
     ["催泪因子", "蒜氨酸酶", "硫", "冷藏", "锋利", "水面"], "通识拓展162"),
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
                               "level:L2", "status:verified", "batch:通识拓展162"],
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
    bank["version"] = "v4.35"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
