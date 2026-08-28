# -*- coding: utf-8 -*-
"""seed_python_knowledge_cards.py · P 线语言机制知识卡（幂等）

把 Mini-Python T4 语言机制沉淀为知识卡（atomic kp）——桥接
python_code 域代码单元与知识卡路由：问「什么是复合赋值」这类
知识型问题可路由直答，代码实现走域单元组装。
纪律：手工标注、幂等插入（payload 比对）、KCCS 四要素完整。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_aug",
     "复合赋值语义",
     "计算机科学知识点内容（人话接口）", "计算机",
     "复合赋值 x op= e 等价于 x = x op e：Mini-Python 支持 += -= *= /= 四种；"
     "/= 为真除恒返回 float 且零除报错；字符串 += 为拼接。",
     ["问复合赋值", "问 += 是什么", "Mini-Python 复合赋值"],
     ["问 C 语言指针", "问运算符重载"],
     "atomic", "",
     "复合赋值 x op= e 就是 x = x op e：四种 op，/= 真除零除报错，字符串 += 拼接。"),
    ("kp_card_strm",
     "字符串方法白名单",
     "计算机科学知识点内容（人话接口）", "计算机",
     "Mini-Python 的 str 方法走白名单机制：现支持 upper（大写）与 split（单字符切分，"
     "保留空段）；白名单外方法拒绝并提示允许集——机制可扩展，语义对照 CPython。",
     ["问字符串方法", "问 upper split", "Mini-Python str 方法"],
     ["问正则表达式", "问字符串算法"],
     "atomic", "",
     "str 方法白名单现含 upper 与 split：不在白名单的方法会拒绝并提示允许集。"),
    ("kp_card_print",
     "print 多参",
     "计算机科学知识点内容（人话接口）", "计算机",
     "Mini-Python 的 print 支持多参数，按空格分隔输出（CPython sep 默认语义）；"
     "零参输出空行。",
     ["问 print 多参", "问打印多个值", "Mini-Python print"],
     ["问 f-string 格式化", "问 print 到文件"],
     "atomic", "",
     "print 多参空格分隔（如 print(\"x =\", 7) 输出 x = 7），零参输出空行。"),
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
                "name": f"{name}（{dgroup}·P线知识卡）",
                "生效条件": conds,
                "子功能": f"{name}——Mini-Python 语言机制知识条目",
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
                               "level:L2", "status:verified", "batch:P线知识卡"],
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
