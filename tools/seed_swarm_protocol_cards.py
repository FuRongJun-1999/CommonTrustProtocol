# -*- coding: utf-8 -*-
"""seed_swarm_protocol_cards.py · 蜂群协议栈条件化知识卡（幂等，2026-08-29）

白箱自举延续：灵枢新造的互联机制（T12 蜂群协议栈）条件化入库——
「系统使用自身的认知机制描述自身」包括它如何与其他节点互联。
跨节点路由时 B 节点可自解释（问蜂群怎么互联/信任怎么算 → 直答）。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_swarm_msgs",
     "蜂群七类消息协议",
     "人工智能知识点内容（人话接口）", "计算机",
     "蜂群互联协议七类消息：HELLO 交换能力表；CAP_QUERY 查询对端能力；"
     "CAP_REPLY 四态裁决（ACCEPT/REJECT/DEFER/BLINDSPOT，跨节点资格判断）；"
     "TASK 派活（仅 ACCEPT 后合法）；RESULT 产出带验证基底说明；VERDICT "
     "发起方用己方基底裁决；ADOPTED 双方固化登记。字段：type/from/to/id/ts/"
     "payload，缺失或非法显式报错。",
     ["问蜂群怎么互联", "蜂群消息协议", "节点之间怎么通信"],
     ["问蓝牙射频实现", "问 TCP 协议栈源码"],
     "atomic", "",
     "蜂群七类消息：HELLO 交换能力→CAP_QUERY 四态协商→TASK→RESULT→"
     "VERDICT 互验证→ADOPTED 双方固化；资格先于执行。"),
    ("kp_card_swarm_discipline",
     "蜂群白箱三纪律",
     "人工智能知识点内容（人话接口）", "计算机",
     "蜂群互联的白箱三纪律：①资格先于执行——未通过四态协商（ACCEPT）"
     "禁止派发任务；②自验证不采信——产出由对方节点用自己的验证基底裁决，"
     "自己验证自己不算数；③盲区记边界——对端回 BLINDSPOT 时把该能力记入"
     "边界表，不重试猜测。三纪律使节点间协作可审计。",
     ["问蜂群三纪律", "节点协作怎么保证可靠", "蜂群互验证"],
     ["问共识算法 Paxos", "问区块链共识"],
     "atomic", "",
     "蜂群三纪律：资格先于执行；自验证不采信（对方裁决）；盲区记边界"
     "不重试。"),
    ("kp_card_swarm_trust",
     "节点信任分",
     "人工智能知识点内容（人话接口）", "计算机",
     "节点信任分 P_trust 是智能论 §2.9 信任定义的工程化：协作者行为在"
     "可接受偏差内保持稳定的置信概率。三性质：可度量（[0,1]）；可更新"
     "（互验证 pass 提升、fail 下降，指数滑动 α=0.3）；可被反例击穿（连续 "
     "fail 跌破隔离阈值 0.3 → 拒绝派单）。分工由信任决定——与对噪声来源"
     "直接隔离的决策同构。",
     ["问节点信任分", "蜂群怎么决定派活给谁", "P_trust 怎么算"],
     ["问人类信任心理学", "问信用评分系统"],
     "atomic", "",
     "节点信任分：行为稳定的置信概率；pass 升 fail 降，跌破 0.3 隔离"
     "拒派单——分工由信任决定。"),
    ("kp_card_swarm_sync",
     "蜂群知识增量同步",
     "人工智能知识点内容（人话接口）", "计算机",
     "跨节点知识同步是 gap 驱动的增量，非全量复制：KNOW_OFFER 发本端知识"
     "条目的 sha256 指纹摘要 → 对端比对自身已有指纹，只回缺失清单 "
     "（KNOW_REQUEST）→ 全文传输（KNOW_GIVE）→ 固化进自身知识库"
     "（tag: swarm_sync）。重复同步幂等：已有指纹零重复传输、零重复入库。"
     "信息差管理命题（D=D(C)）在节点间的落地。",
     ["问蜂群知识怎么共享", "节点间知识同步", "增量同步怎么做"],
     ["问全量备份策略", "问分布式一致性协议"],
     "atomic", "",
     "知识增量同步：指纹摘要→比对缺口→只传缺失→幂等固化；gap 驱动"
     "非全量复制。"),
    ("kp_card_swarm_bus",
     "目录总线与收件箱",
     "人工智能知识点内容（人话接口）", "计算机",
     "蜂群教学模拟传输层：每节点一个收件箱目录，消息为一个 JSON 文件，"
     "发送=写入对方收件箱，读取后删除即消费，按 ts 排序保证序列可追溯。"
     "半写文件（JSON 解析失败）跳过下轮再读。限制显式：这是模拟射频层的"
     "教学口径，真实 socket/蓝牙射频是后续批次。跨实例运行须用唯一目录"
     "（残留消息会串扰）。",
     ["问目录总线", "蜂群消息怎么传输", "收件箱机制"],
     ["问零拷贝网络编程", "问消息队列 Kafka"],
     "atomic", "",
     "目录总线：收件箱目录+JSON 消息文件，读后删除即消费，模拟射频层"
     "教学口径。"),
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
                "name": f"{name}（{dgroup}·蜂群协议卡）",
                "生效条件": conds,
                "子功能": f"{name}——蜂群协议栈条件化知识条目（自举：系统描述自身互联机制）",
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
                               "level:L2", "status:verified", "batch:蜂群协议卡"],
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
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    r = ensure_seed()
    print(f"蜂群协议卡入库: +{r['inserted']} 更新 {r['updated']} 幂等跳过 {r['skipped']}"
          f"（共 {len(NODES)} 卡）")
