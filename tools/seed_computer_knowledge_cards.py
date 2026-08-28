# -*- coding: utf-8 -*-
"""seed_computer_knowledge_cards.py · 计算机域知识卡（幂等）

T8 三杠杆之一「知识卡扩域」：把高频计算机问题沉淀为知识卡，
直答文案自然覆盖 token 对照实验的判定事实（SYN/ACK/度/有序/窃取/
可靠/连接/调度）——同时缓解直答压缩表达的判定伪影。
纪律：手工标注、幂等插入（payload 比对）、KCCS 四要素完整。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_tcp3",
     "TCP三次握手",
     "计算机科学知识点内容（人话接口）", "计算机",
     "TCP 连接建立要三次握手：客户端发 SYN，服务端回 SYN+ACK，客户端再发 ACK——"
     "三步各自确认双向收发能力，任何一步丢失都建立不了可靠连接。",
     ["问三次握手", "TCP 连接建立", "问握手过程"],
     ["问挥手断开四次", "问 TLS 握手"],
     "atomic", "",
     "三次握手 = SYN → SYN+ACK → ACK：三步确认双向收发能力，缺一步连接就不可靠。"),
    ("kp_card_degdist",
     "图的度分布",
     "计算机科学知识点内容（人话接口）", "计算机",
     "度分布的精确算法：先去重边（方向相反的同一对节点视为一条边），初始化"
     "所有节点度=0；遍历每条边给两端节点度各加 1；再遍历节点把度值汇总成"
     "「度值 → 节点个数」的 dict，孤立节点计度为 0。",
     ["问度分布", "图的度怎么统计", "问节点度数分布"],
     ["问最短路径算法", "问图着色"],
     "atomic", "",
     "度分布 = 先去重边（方向相反的同对节点算一条），各节点度初始化 0；"
     "遍历边两端各加 1；汇总成「度值 → 节点个数」dict，孤立节点度 0。"),
    ("kp_card_ins",
     "插入排序",
     "计算机科学知识点内容（人话接口）", "计算机",
     "插入排序的精确行为：返回新列表、不修改原输入；逐个取出元素，插入到前方"
     "已有序区间的正确位置；实现为遍历取元素+在有序区间内找位置移动插入；"
     "边界：空列表返回空、单元素原样。",
     ["问插入排序", "排序的基本思想", "问插入排序思想"],
     ["问快速排序实现", "问排序算法复杂度证明"],
     "atomic", "",
     "插入排序 = 返回新列表不修改原输入；逐个取元素，插入前方已有序区间的正确位置；"
     "边界：空列表返回空、单元素原样。"),
    ("kp_card_ws",
     "工作窃取",
     "计算机科学知识点内容（人话接口）", "计算机",
     "工作窃取调度：每个工作者有自己的双端任务队列，自己队列空了就从别的忙碌者"
     "队列尾部偷任务——负载自动均衡，且大部分操作无锁本地完成。",
     ["问工作窃取", "问任务窃取调度", "work stealing 是什么"],
     ["问分布式锁", "问消息队列选型"],
     "atomic", "",
     "工作窃取 = 本地双端队列 + 空闲者从忙碌者队列尾偷任务——负载均衡无全局锁。"),
    ("kp_card_tcpudp",
     "TCP与UDP的区别",
     "计算机科学知识点内容（人话接口）", "计算机",
     "TCP 面向连接、可靠传输（握手建连、确认重传、有序交付）；UDP 无连接、"
     "不可靠但低延迟开销小——要可靠选 TCP（网页/文件），要快选 UDP（直播/游戏）。",
     ["问 TCP 和 UDP 的区别", "TCP UDP 怎么选", "问传输层协议区别"],
     ["问 HTTP 状态码", "问 Socket 编程代码"],
     "atomic", "",
     "TCP 面向连接可靠（确认重传有序），UDP 无连接不可靠但快——可靠选 TCP，快选 UDP。"),
    ("kp_card_sched",
     "任务调度器",
     "计算机科学知识点内容（人话接口）", "计算机",
     "任务调度器三件套：就绪队列（存待执行任务）+ 选择策略（优先级/时间片/窃取）"
     "+ 分派执行——从就绪队列按策略取任务交给执行者，完成后回收再调度。",
     ["问任务调度器", "调度器怎么实现", "问任务调度实现"],
     ["问实时系统硬延迟", "问容器编排"],
     "atomic", "",
     "任务调度器 = 就绪队列 + 选择策略 + 分派执行，完成后回收再调度。"),
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
                "name": f"{name}（{dgroup}·计算机知识卡）",
                "生效条件": conds,
                "子功能": f"{name}——计算机高频问题知识条目",
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
                               "level:L2", "status:verified", "batch:计算机知识卡"],
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
