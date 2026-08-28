# -*- coding: utf-8 -*-
"""seed_t10_cards.py · T10 复杂任务预置规范型卡（幂等）

按单源规范四·五节「规范型卡优先」纪律：执行字段=精确行为规范
（怎么做/边界/返回结构），数值与边界显式——层级对齐实验（T10）的
A 组弹药。插入后 CSRE 索引由 bootstrap_loop 自动重建。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_fsm",
     "订单状态机流转",
     "计算机科学知识点内容（人话接口）", "计算机",
     "订单状态机有 4 个状态与 3 个合法动作：待支付--支付-->已支付--发货-->已发货"
     "--确认-->已完成；取消动作仅待支付态合法且进入已取消。其余任何「状态×动作」"
     "组合均为非法流转。",
     ["问订单状态机", "问状态流转规则", "订单状态怎么变"],
     ["问物流跟踪接口", "问退款流程"],
     "atomic", "",
     "合法流转表：待支付+支付→已支付；已支付+发货→已发货；已发货+确认→已完成；"
     "待支付+取消→已取消。其余组合全部非法。"),
    ("kp_card_leap",
     "闰年规则",
     "数学知识点内容（人话接口）", "数学",
     "闰年判定：年份能被 4 整除且不能被 100 整除，或能被 400 整除——即"
     "（y%4==0 且 y%100!=0）或 y%400==0。闰年 2 月 29 天，平年 28 天。",
     ["问闰年规则", "怎么判断闰年", "二月多少天"],
     ["问农历闰月", "问节气日期"],
     "atomic", "",
     "闰年 =（被 4 整除且不被 100 整除）或被 400 整除；闰年 2 月 29 天。"),
    ("kp_card_agg",
     "账单聚合规范",
     "计算机科学知识点内容（人话接口）", "计算机",
     "账单聚合三步：①过滤 amount>0 的记录（负数为冲销不入统计）；②按类目累加"
     "金额得每类目小计；③总额=全部过滤后金额之和（保留两位小数），top 类目=小计"
     "最大者（并列取字典序首个）。空输入返回 total=0.0、by_category={}、top=None。",
     ["问账单聚合", "怎么按类目统计金额", "问消费汇总"],
     ["问 Excel 操作", "问数据库 SQL"],
     "atomic", "",
     "聚合三步：过滤 amount>0 → 按类目累加 → 总额两位小数 + top 类目（并列取"
     "字典序首个）；空输入 total=0.0、by_category={}、top=None。"),
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
                "name": f"{name}（{dgroup}·T10规范卡）",
                "生效条件": conds,
                "子功能": f"{name}——规范型知识卡（实现任务直接遵循）",
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
                               "level:L2", "status:verified", "batch:T10规范卡"],
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
