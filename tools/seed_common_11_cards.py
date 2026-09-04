# -*- coding: utf-8 -*-
"""seed_common_11_cards.py · 通识拓展批次知识卡（幂等）

11：物理-温度与热量/化学-常见的酸和碱/地理-人口与城市/文学-中国古典诗词
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_tempheat",
     "温度与热量",
     "基础科学知识点内容（人话接口）", "物理学",
     "温度与热量：温度表示物体冷热程度（°C 或 K），热量是热传递过程中转移的"
     "能量（单位焦耳 J）——温度是状态量，热量是过程量（不能说物体含有多少热"
     "量，只能说吸收或放出了多少热量）。热传递方向：从高温物体传向低温物体，"
     "直到温度相同（热平衡）。热传递三种方式：传导（固体）、对流（液体气体）、"
     "辐射（电磁波不需要介质）。",
     ["温度和热量的区别", "温度与热量", "热传递的方式", "热量是什么",
      "热传递的三种方式", "传导对流辐射"],
     ["问热力学定律", "问比热容"],
     "atomic", "",
     "温度=冷热程度（状态量）；热量=传递的能量（过程量）；三方式=传导+对流+辐射；热从高温→低温。"),
    ("kp_card_acidsbases",
     "生活中常见的酸和碱",
     "基础科学知识点内容（人话接口）", "化学",
     "生活中常见的酸：食醋（醋酸/乙酸）、柠檬（柠檬酸）、胃酸（盐酸）、可乐"
     "（碳酸）。常见的碱：氢氧化钠（烧碱/火碱，工业用强碱）、氢氧化钙（熟石"
     "灰，改良酸性土壤）、氨水（化肥）、小苏打水溶液（弱碱性）。酸碱指示剂："
     "紫色石蕊试液遇酸变红遇碱变蓝；无色酚酞遇酸不变色、遇碱变红。",
     ["生活中常见的酸和碱", "常见的酸有哪些", "常见的碱有哪些", "食醋是酸还是碱",
      "酸碱指示剂", "石蕊试液变色"],
     ["问pH试纸", "问中和反应应用"],
     "atomic", "",
     "常见酸=食醋/柠檬酸/胃酸(盐酸)；常见碱=烧碱/熟石灰/氨水；指示剂：石蕊酸红碱蓝、酚酞碱红酸不变。"),
    ("kp_card_population",
     "世界人口与城市化",
     "人文通识知识点内容（人话接口）", "地理学",
     "世界人口与城市化：世界人口已突破 80 亿（2022年11月），人口增长最快的大"
     "洲是非洲。人口自然增长率=出生率-死亡率；人口密度=总人口÷总面积。城市化"
     "=人口向城市聚集、农村地区转变为城市地区的过程——发达国家城市化率高（超"
     "过75%），发展中国家正在快速城市化。城市化带来经济活力但也伴随交通拥堵、"
     "环境污染、住房紧张等问题。",
     ["世界人口", "人口与城市化", "人口密度怎么算", "什么是城市化",
      "人口自然增长率", "城市化带来什么问题"],
     ["问人口老龄化", "问移民"],
     "atomic", "",
     "世界人口超80亿；城市化=人口向城市聚集；自然增长率=出生率-死亡率；密度=总人口÷面积。"),
    ("kp_card_classicalpoetry",
     "中国古典诗词",
     "人文通识知识点内容（人话接口）", "文学",
     "中国古典诗词：唐诗、宋词、元曲是中国古典文学的三大高峰。唐诗分初唐（初"
     "唐四杰）、盛唐（李白诗仙、杜甫诗圣）、中晚唐（白居易、李商隐）；宋词分"
     "豪放派（苏轼、辛弃疾）和婉约派（李清照、柳永）；元曲代表人物关汉卿（《窦"
     "娥冤》）。诗词讲究格律——平仄、对仗、押韵；唐诗分绝句（四句）和律诗（八"
     "句）。",
     ["中国古典诗词", "唐诗宋词", "诗仙和诗圣", "李白和杜甫",
      "豪放派和婉约派", "唐诗的分类"],
     ["问现代诗歌", "问对对联"],
     "atomic", "",
     "唐诗=李白(仙)/杜甫(圣)；宋词=豪放(苏轼/辛弃疾)+婉约(李清照/柳永)；绝句四句/律诗八句。"),
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
                               "level:L2", "status:verified", "batch:通识拓展11"],
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
    return {"inserted": inserted, "updated": updated, "skipped": skipped}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
