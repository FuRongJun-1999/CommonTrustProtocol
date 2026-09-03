# -*- coding: utf-8 -*-
"""seed_n8_v3_cards.py · 白箱知识域拓展第三批知识卡（幂等）

夜批N8：太阳系行星/免疫系统/中文成语/交通安全 四域各一张，
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_solarplanets",
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
    ("kp_card_immune",
     "人体免疫系统的基础",
     "基础科学知识点内容（人话接口）", "免疫学",
     "人体免疫系统三道防线：第一道=皮肤与黏膜（物理屏障阻挡病原体）；第二道="
     "先天免疫（白细胞吞噬、炎症反应，对所有病原体通用）；第三道=适应性免疫"
     "（T 细胞与 B 细胞，B 细胞产生抗体精准打击，并形成记忆细胞使下次反应更快"
     "——疫苗的原理就是训练这第三道防线）。",
     ["人体免疫系统", "免疫系统怎么工作", "什么是抗体", "疫苗的原理",
      "免疫三道防线", "白细胞的作用"],
     ["问过敏原理", "问自身免疫病"],
     "atomic", "",
     "免疫三防线=皮肤黏膜屏障→白细胞先天免疫→T/B 细胞适应性免疫（抗体+记忆细胞=疫苗原理）。"),
    ("kp_card_chengyu",
     "成语的结构与文化",
     "人文通识知识点内容（人话接口）", "汉语成语",
     "成语是汉语中经过长期使用锤炼形成的固定短语，多为四字格。来源主要有四类："
     "历史故事（如完璧归赵出自蔺相如）、寓言传说（如守株待兔出自韩非子）、经典"
     "诗文（如温故知新出自论语）、民间口语（如锦上添花）。成语的意义往往不是字"
     "面直加，而是典故引申——学习成语需要同时了解其出处故事。",
     ["什么是成语", "成语的来源", "四字成语", "完璧归赵的典故",
      "成语有多少个", "守株待兔出自哪里"],
     ["问歇后语", "问对联规则"],
     "atomic", "",
     "成语=四字格固定短语，四大来源=历史故事/寓言/诗文/口语；意义多由典故引申。"),
    ("kp_card_trafficsignal",
     "交通信号灯规则",
     "生活常识知识点内容（人话接口）", "交通安全",
     "交通信号灯规则：红灯停、绿灯行、黄灯亮时不已越过停止线的应停在线内等待。"
     "方向箭头灯按箭头指示通行；闪光黄灯=警告慢行确认安全后通过。行人与非机动"
     "车同样服从信号灯；无论信号如何，遇到执行任务的特种车辆（救护/消防/警车）"
     "都应让行。闯红灯记分罚款且极易引发事故——「宁停三分，不抢一秒」。",
     ["交通信号灯规则", "红灯停绿灯行", "黄灯亮了怎么办", "闯红灯的后果",
      "闪光黄灯是什么意思", "问交通规则", "黄灯亮起时应该怎么通行", "黄灯亮起时",
      "问黄灯", "黄灯时能走吗"],
     ["问酒驾标准", "问高速公路规则"],
     "atomic", "",
     "信号灯=红灯停/绿灯行/黄灯未越线停；特种车辆必让行；宁停三分不抢一秒。"),
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
                               "level:L2", "status:verified", "batch:白箱拓展第三批"],
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
