# -*- coding: utf-8 -*-
"""主动盲区补卡 v1（2026-08-20 · 主动探测驱动）

从 active_blindspot_report.json 的 60 条高价值盲区中，选 6 张
对比关系卡（算法/操作系统/计算机组成核心概念），补入图谱。

审核闸门（与 flywheel_knowledge_supply 相同纪律）：
  - 客观事实（算法/系统概念定义，可查证）
  - 无主观词（我认为/应该/好/坏）
  - 每条带审核说明 + 条件空间
"""
import sys, io, json, sqlite3, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DB = r"C:\Users\FuRongJun\.dsh\profiles\web\data\lingshu.db"
DB_W = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db"

# (问题, 答案, 学科域, 审核说明) —— 对比关系卡
CONTRAST_ENTRIES = [
    ("动态规划和贪心算法有什么区别",
     "动态规划（DP）和贪心算法的区别：DP 考虑所有子问题并保存最优子结构解，全局最优；贪心只做当前局部最优选择，不回退。DP 适合重叠子问题+最优子结构（如背包/最短路径），贪心适合贪心选择性质成立的问题（如活动选择/哈夫曼编码）。DP 保证全局最优，贪心不保证但通常更快。（审核：算法教材标准定义，可查证）",
     "计算机科学", "E4", "算法教材对比定义"),
    ("回溯与分支限界和图搜索有什么区别",
     "回溯、分支限界、图搜索的区别：回溯系统地深度优先搜索解空间树并剪枝（八皇后/0-1背包）；分支限界用广度优先+限界函数剪枝（割平面/旅行商）；图搜索是在图上找路径（BFS 无权最短/DFS 连通性/A* 启发式）。回溯求所有解或可行解，分支限界求最优解，图搜索求路径。（审核：算法教材标准定义）",
     "计算机科学", "E4", "算法教材对比定义"),
    ("最短路径算法和最大流最小割有什么区别",
     "最短路径与最大流最小割的区别：最短路径求图中两点的最小代价路径（Dijkstra 非负权/Floyd 全源/Bellman-Ford 负权）；最大流求网络从源到汇的最大流量（Ford-Fulkerson/Edmonds-Karp/Dinic），最小割定理：最大流=最小割容量。最短路径是路径优化，最大流是流量分配。（审核：图论标准定义）",
     "计算机科学", "E4", "图论教材对比"),
    ("死锁和进程间通信有什么区别",
     "死锁与进程间通信（IPC）的区别：死锁是进程互相等待对方占用的资源而永久阻塞（四个必要条件：互斥/持有等待/不可剥夺/循环等待，预防用破坏条件或银行家算法）；IPC 是进程间传递数据的机制（管道/消息队列/共享内存/信号/套接字）。死锁是资源管理问题，IPC 是通信问题，二者是操作系统的不同子系统。（审核：操作系统教材标准定义）",
     "计算机科学", "E3", "操作系统教材对比"),
    ("冯诺依曼体系和数据表示有什么区别",
     "冯诺依曼体系与数据表示的区别：冯诺依曼体系是计算机结构模型（存储程序：指令和数据同存内存，CPU 取指-译码-执行循环，五大部件：运算器/控制器/存储器/输入/输出）；数据表示是数据在计算机中的编码方式（二进制/补码/浮点数 IEEE754/字符 ASCII-UTF8）。体系是硬件结构，数据表示是数据编码。（审核：计算机组成原理标准内容）",
     "计算机科学", "E3", "计算机组成教材对比"),
    ("形式逻辑和科学方法论有什么区别",
     "形式逻辑与科学方法论的区别：形式逻辑研究推理形式的有效性（演绎/归纳/溯因，三段论，命题逻辑与谓词逻辑，关注形式正确性不关心内容真假）；科学方法论研究知识如何被验证（可检验性/证伪/实验设计/统计证据，关注主张如何被证据支持）。逻辑给推理形式，方法论给验证标准。（审核：哲学/科学哲学标准区分）",
     "哲学", "E4", "哲学与科学方法论对比"),
]

REJECT_WORDS = ("我觉得", "我认为", "应该", "最好", "美丽",
                "值得", "重要", "必须", "所有人", "总是", "从不")


def audit(ans, reason):
    # v1.22 单字「好/坏」只拦独立成词（前后是标点/空格/句首句尾），
    # 组合词（破坏/好坏参半/美好）不误伤——「预防用破坏条件」的
    # 「坏」是「破坏」的一部分，不是主观评价。
    import re as _re
    for w in REJECT_WORDS:
        if w in ans:
            return False, f"含主观词「{w}」"
    for w in ("好", "坏"):
        for m in _re.finditer(w, ans):
            i = m.start()
            prev = ans[i - 1] if i > 0 else " "
            nxt = ans[i + 1] if i + 1 < len(ans) else " "
            if (prev in "，。；、（）\s" or not prev.isalpha()) and \
                    (nxt in "，。；、（）\s" or not nxt.isalpha()):
                return False, f"含独立主观词「{w}」"
    if len(ans) < 30:
        return False, "答案过短"
    if not reason:
        return False, "缺审核说明"
    return True, reason


def main():
    for db in (DB, DB_W):
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        now = time.time()
        added = 0
        for q, ans, domain, edu, reason in CONTRAST_ENTRIES:
            ok, note = audit(ans, reason)
            if not ok:
                print(f"  ✗ 拒绝 {q[:16]}：{note}")
                continue
            cur.execute("SELECT COUNT(*) FROM nodes WHERE content LIKE ?",
                        ('%' + ans[:20] + '%',))
            if cur.fetchone()[0] > 0:
                print(f"  — 已存在 {q[:16]}")
                continue
            node_id = f"kp_contrast_{int(time.time()*1000)}"
            cs = json.dumps({"observation_position": "主动盲区探测补卡",
                             "observation_tool": "对比关系知识点（审核后）",
                             "time_window": [now, now + 31536000],
                             "existence_constraint": "算法/系统/哲学教材标准定义"}, ensure_ascii=False)
            cur.execute(
                "INSERT INTO nodes (id, content, modality, spatial_coordinates, temporal_coordinate, "
                "condition_space, importance, confidence, layer, access_count, last_access, created_at, "
                "tags, semantic_coordinates, state_attributes, entity_id) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (node_id, ans, "text", "{}", now, cs, 0.8, 0.9, "knowledge", 0, now, now,
                 json.dumps(["知识飞轮", "主动盲区补卡", f"domain:{domain}", f"edu:{edu}",
                             "verified", "对比关系"], ensure_ascii=False),
                 "{}", "{}", None))
            added += 1
            print(f"  ✓ [{domain}] {q[:20]} → {ans[:40]}...")
        conn.commit()
        print(f"库 {db[-40:]}: 添加 {added} 条")
        conn.close()


if __name__ == "__main__":
    main()
