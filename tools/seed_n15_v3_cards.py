# -*- coding: utf-8 -*-
"""seed_n15_v3_cards.py · 知识域拓展第九批知识卡（幂等）

夜批N15：植物学-花的结构与传粉/天文学-太阳系行星/体育学-奥林匹克/营养学-膳食
均衡 四域各一张，KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_flowerpollination",
     "花的结构与传粉",
     "基础科学知识点内容（人话接口）", "植物学",
     "花的结构与传粉：一朵完全花包括花萼、花瓣、雄蕊（产生花粉）和雌蕊（子房"
     "里有胚珠）。传粉=花粉从雄蕊花药传到雌蕊柱头的过程，分自花传粉和异花传"
     "粉——异花传粉靠昆虫（蜜蜂蝴蝶，花蜜与鲜艳花瓣吸引）或风力（花粉轻小数"
     "量多）。传粉受精后子房发育成果实、胚珠发育成种子。",
     ["花的结构", "什么是传粉", "花有哪些部分", "蜜蜂和花的关系",
      "果实是怎么来的", "问传粉"],
     ["问光合作用", "问种子萌发"],
     "atomic", "",
     "花 = 花萼+花瓣+雄蕊（花粉）+雌蕊（子房）；传粉靠虫媒/风媒；受精后子房成果实、胚珠成种子。"),
    ("kp_card_solarsystem",
     "太阳系八大行星",
     "基础科学知识点内容（人话接口）", "天文学",
     "太阳系八大行星按离太阳由近到远：水星、金星、地球、火星（四颗类地岩石"
     "行星）、木星、土星（两颗巨气态行星，有行星环）、天王星、海王星（两颗冰"
     "巨星）。冥王星 2006 年被重新归类为矮行星。记忆口诀：水金地火木土天海。"
     "木星是最大的行星，金星是最热的行星（温室效应）。",
     ["太阳系八大行星", "八大行星有哪些", "太阳系行星顺序", "最大的行星是哪个",
      "冥王星为什么不是行星", "离太阳最近的行星"],
     ["问月球细节", "问小行星带"],
     "atomic", "",
     "八大行星顺序=水金地火木土天海；前四类地岩石/后四巨气态冰；木星最大、金星最热。"),
    ("kp_card_olympics",
     "奥林匹克运动会",
     "人文通识知识点内容（人话接口）", "体育学",
     "奥林匹克运动会：起源于古希腊奥林匹亚（公元前 776 年有文字记载），现代奥"
     "运会由顾拜旦倡导于 1896 年在雅典复兴，每四年一届。五环旗五种颜色代表五大"
     "洲团结；格言「更快、更高、更强——更团结」。冬奥会与之相间两年举行。中国"
     "2008 年举办北京夏季奥运会、2022 年举办北京冬奥会（双奥之城）。",
     ["奥林匹克运动会", "奥运会的起源", "奥运会几年一届", "五环代表什么",
      "奥运格言是什么", "双奥之城是哪里"],
     ["问世界杯足球", "问亚运会"],
     "atomic", "",
     "奥运会 = 古希腊起源/1896 雅典复兴/四年一届；五环象征五洲团结；格言更快更高更强更团结。"),
    ("kp_card_balanceddiet",
     "膳食均衡",
     "基础科学知识点内容（人话接口）", "营养学",
     "膳食均衡：人体需要碳水化合物（主食供能）、蛋白质（肉蛋奶豆，组织修复与"
     "生长）、脂肪（储能与必需脂肪酸）、维生素（调节代谢）、矿物质（如钙铁锌）"
     "和水/膳食纤维六大类营养，缺一不可。中国居民膳食指南建议：食物多样谷类为"
     "主，餐餐有蔬菜、天天吃水果、常吃奶豆、适量鱼禽蛋瘦肉，少油少盐少糖。",
     ["什么是膳食均衡", "膳食均衡", "人体需要哪些营养", "怎么吃才健康",
      "膳食指南", "六大营养素"],
     ["问减肥饮食", "问儿童营养"],
     "atomic", "",
     "膳食均衡 = 六大营养素齐全、谷类为主餐餐蔬菜、少油少盐少糖——食物多样是核心。"),
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
                               "level:L2", "status:verified", "batch:拓展第九批"],
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
