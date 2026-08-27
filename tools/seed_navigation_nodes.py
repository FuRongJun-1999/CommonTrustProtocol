# -*- coding: utf-8 -*-
"""seed_navigation_nodes.py · 导航递归首批复合节点种子（幂等）

《导航递归CSPRE_实现文档_v0.1》§4.5：
  复合节点 = knowledge_type: composite + sub_route 子条件空间词
  叶子原子卡 = 生效条件含 sub_route 词（refine_question 收窄后可命中）

纪律：手工标注、增量插入、防误标污染路由（不做自动推断）。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

# (id, name, domain, domain_group, content, 生效条件, 不适用条件,
#  knowledge_type, sub_route, 直答)
NODES = [
    # ---- 复合根：婆媳相处 ----
    ("kp_nav_px_root",
     "婆媳相处",
     "家庭关系知识点内容（人话接口）", "生活",
     "婆媳相处的核心：丈夫是桥梁不是裁判；妻子与婆婆的关系需要边界感和尊重共同经营。",
     ["婆媳矛盾", "婆媳关系不好", "和婆婆吵架", "问怎么处理婆媳关系"],
     ["问财产纠纷", "问法律诉讼"],
     "composite", "沟通情境",
     ""),
    # 叶子 1：沟通情境 → 倾听共情
    ("kp_nav_px_qt",
     "倾听共情",
     "家庭关系知识点内容（人话接口）", "生活",
     "婆媳有分歧先倾听共情：先复述对方的感受让对方知道被理解，再表达自己的想法，不争对错。",
     ["沟通情境下如何倾听", "问婆媳沟通怎么开始", "说不上话怎么办"],
     ["问财产分配比例"],
     "atomic", "",
     "先倾听共情，再表达自己——让婆婆感到被理解，矛盾就化解了一半。"),
    # 叶子 2：边界设定
    ("kp_nav_px_bj",
     "边界设定",
     "家庭关系知识点内容（人话接口）", "生活",
     "小家庭事务的边界要温和而明确：夫妻商量一致后由儿子/丈夫出面沟通，妻子不直接顶撞。",
     ["沟通情境下怎么设边界", "问小家庭事务谁做主"],
     ["问抚养权归属"],
     "atomic", "",
     "小家庭的事夫妻商量好，由儿子出面跟妈妈温和沟通——边界清楚但不伤感情。"),

    # ---- 复合根：理财亏损 ----
    ("kp_nav_lc_root",
     "理财亏损",
     "经济学与金融知识点内容（人话接口）", "财经",
     "理财亏损的处理框架：先止损盘点，再分析原因，最后调整策略——不同阶段动作不同。",
     ["理财亏了", "投资亏损了", "基金股票被套"],
     ["问具体股票代码推荐"],
     "composite", "风险场景",
     ""),
    ("kp_nav_lc_fx",
     "风险评估",
     "经济学与金融知识点内容（人话接口）", "财经",
     "亏损后第一步评估风险承受度：这笔钱短期要不要用？最大能承受多少回撤？答案决定加仓还是止损离场。",
     ["风险场景下怎么评估承受力", "问该不该割肉"],
     ["问内幕消息"],
     "atomic", "",
     "先用「这笔钱半年内要不要用」自测风险承受度——要用的钱尽早止损，长期闲钱再谈策略。"),

    # ---- 复合根：育儿冲突 ----
    ("kp_nav_ye_root",
     "育儿冲突",
     "发展心理学知识点内容（人话接口）", "心理",
     "育儿冲突的正解不是分输赢：先区分冲突类型——是隔代观念差异还是教育方式分歧，再分别处理。",
     ["带孩子观念不一致", "和家人在教育孩子上冲突"],
     ["问学区房政策"],
     "composite", "冲突类型",
     ""),
    ("kp_nav_ye_jg",
     "隔代观念调和",
     "发展心理学知识点内容（人话接口）", "心理",
     "隔代育儿观念冲突：抓大放小——安全和原则问题坚持科学做法，生活习惯类差异宽容共存。",
     ["冲突类型是老人溺爱或观念旧", "问隔代教育冲突怎么办"],
     ["问学区房规划"],
     "atomic", "",
     "隔代观念差用「抓大放小」：安全与健康的原则坚持科学，生活习惯的差异宽容共存。"),
]


def ensure_schema_and_seed() -> dict:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # 表结构自检（nodes 无 name 列，name 在 state_attributes）
    inserted = updated = skipped = 0
    for nid, name, domain, dgroup, content, conds, negs, ktype, sub_route, direct in NODES:
        row = cur.execute("SELECT state_attributes FROM nodes WHERE id=?",
                          (nid,)).fetchone()
        if row:
            try:
                obj = json.loads(row[0]) if isinstance(row[0], str) else {}
            except Exception:
                obj = {}
            if not isinstance(obj, dict):
                # 第二阶段审查教训（列序错位事故）：payload 曾被写进 created_at 列，
                # state_attributes 残留时间戳 int——从 created_at 找回真实 payload
                try:
                    obj = json.loads(row[0]) if isinstance(row[0], str) else {}
                except Exception:
                    obj = {}
                try:
                    recovered = conn.execute(
                        "SELECT created_at FROM nodes WHERE id=?", (nid,)).fetchone()[0]
                    if isinstance(recovered, str) and recovered.startswith("{"):
                        obj = json.loads(recovered)
                except Exception:
                    obj = {}
            if obj.get("knowledge_type") == ktype and obj.get("fingerprint"):
                skipped += 1
                continue
            existing_sa = obj
            exists = True
        else:
            existing_sa = {}
            exists = False
        sa = {
            "name": name,
            "kind": "knowledge_point",
            "knowledge_type": ktype,
            "sub_route": sub_route,
            "domain": domain,
            "domain_group": dgroup,
            "edu_level": "",
            "comment": {
                "name": f"{name}（{dgroup}·导航种子）",
                "生效条件": conds,
                "子功能": (f"{name}的条件空间导航入口" if ktype == "composite"
                           else f"{name}——原子知识条目"),
                "执行": direct or content,
                "不适用条件": negs,
            },
        }
        payload = json.dumps(sa, ensure_ascii=False)
        if not exists:
            tags = json.dumps(["knowledge_point", f"domain:{domain}",
                               "level:L2", "status:verified",
                               f"nav:{sub_route or 'root'}"], ensure_ascii=False)
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
                        "created_at=CAST(strftime('%s','now') AS INTEGER), "
                        "spatial_coordinates='[]', temporal_coordinate='[0,0,0]', "
                        "condition_space='{}', semantic_coordinates='{}' "
                        "WHERE id=?", (payload, content, nid))
            updated += 1
    conn.commit()
    conn.close()
    return {"inserted": inserted, "updated": updated, "skipped": skipped}


if __name__ == "__main__":
    print(json.dumps(ensure_schema_and_seed(), ensure_ascii=False))
