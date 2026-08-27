# -*- coding: utf-8 -*-
"""知识考古 · 批次2 补卡（2026-08-21）

#7 复杂系统科学（6卡）+ #3 认知科学补齐（6卡）= 12 张前沿知识卡 → 图谱

审核纪律（沿用知识飞轮 + 批次1）：
  - 物理基底可验证（涌现/幂律/工作记忆容量——客观定义）
  - 拒绝主观词（独立成词的 好/坏/我觉得/应该）
  - 每条带审核说明 + 条件空间 + 学科域/学段标签
  - 不宣称首创：既有学术成果，贡献在纳入协议坐标系
"""
import sys, io, json, sqlite3, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DB = r"C:\Users\FuRongJun\.dsh\profiles\web\data\lingshu.db"
DB_W = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db"

ENTRIES = [
    # ============ #7 复杂系统科学 ============
    ("涌现", "涌现：局部规则交互产生全局模式，模式不能还原为局部规则的简单叠加——蚁群觅食、鸟群编队、神经元→意识。对应协议0.0.3局部不可知（局部规则可知，全局模式不可直接推导）。",
     "复杂系统", "E4", "涌现是复杂系统科学核心概念，可验证"),
    ("自组织临界性", "自组织临界性（SOC）：系统自发演化到临界态——沙堆模型：不断加沙粒，系统保持在崩塌临界点，崩塌大小呈幂律分布。是认知边界/思维切换的物理对应（临界点附近系统最敏感）。",
     "复杂系统", "E4", "Bak 1987自组织临界性，沙堆实验可验证"),
    ("网络科学", "网络科学：用图论研究复杂系统的连接结构——小世界网络（六度分隔，高聚类+短路径）、无标度网络（度分布幂律，枢纽节点）、社区结构。是知识图谱结构的数学基础。",
     "复杂系统", "E4", "Watts-Strogatz小世界/Barabasi无标度，可验证"),
    ("混沌的边缘", "混沌的边缘：系统介于有序与混沌之间的相变区域——有序（规则主导）与混沌（敏感混乱）的边界。生命/智能/认知被认为运行在混沌的边缘（最大信息处理能力）。",
     "复杂系统", "E4", "Langton 1990混沌边缘，元胞自动机实验可验证"),
    ("复杂适应系统", "复杂适应系统（CAS）：由大量适应性主体组成的系统——主体基于局部规则交互、学习、适应，全局呈现自组织（免疫系统/市场/生态系统）。对应蜂群架构。",
     "复杂系统", "E4", "Holland 1995复杂适应系统理论，可验证"),
    ("标度律", "标度律：系统属性随规模呈幂律变化（y ∝ x^b）——异速生长（代谢率∝质量^0.75）、城市规模指数、网络度分布。是信息分型（CNN权值共享）的数学对应。",
     "复杂系统", "E4", "Kleiber定律/幂律标度，可验证"),
    # ============ #3 认知科学补齐 ============
    ("工作记忆", "工作记忆：暂时保持并操作信息的能力，容量约4±1个组块（Cowan 2001）——中央执行器+语音环路+视空间模板+情景缓冲器。对应协议情境层（对话上下文的快速暂存）。",
     "认知科学", "E4", "Baddeley工作记忆模型/Cowan容量研究，可验证"),
    ("认知偏差", "认知偏差：系统性的思维偏离理性——确认偏差（只注意支持自己观点的证据）、可得性偏差（以易想起判断概率）、锚定效应（受首信息影响）、损失厌恶（损失比收益更敏感）。",
     "认知科学", "E4", "Kahneman-Tversky启发式与偏差研究，可验证"),
    ("元认知", "元认知：对自身认知过程的认知与监控——知道什么不知道（校准）、信心判断、策略选择。对应协议诚实边界（知道自己不知道=元认知的诚实表现）。",
     "认知科学", "E4", "Flavell 1979元认知概念，可验证"),
    ("认知负荷理论", "认知负荷理论：工作记忆容量有限，学习材料超过容量→认知超载→学习效率下降。三种负荷：内在（材料复杂度）、外在（呈现方式）、相关（图式建构）。",
     "认知科学", "E4", "Sweller 1988认知负荷理论，可验证"),
    ("概念形成", "概念形成：人如何获得概念——原型理论（以典型样例为参照）、样例理论（以具体实例比较）、理论观（概念嵌入知识网络）。对应知识卡的组织方式。",
     "认知科学", "E4", "Rosch原型理论/样例理论，可验证"),
    ("注意机制", "注意机制：认知资源的选择性分配——选择性注意（聚焦）、分散注意（多任务）、持续注意（警觉）。对应协议注意力/检索聚焦（CSPMN只匹配激活条件空间）。",
     "认知科学", "E4", "Posner注意模型/认知心理学标准概念，可验证"),
]

REJECT = ("我觉得", "我认为", "最好", "美丽", "值得", "重要", "必须",
          "所有人", "总是", "从不")


def audit(ans, reason):
    for w in REJECT:
        if w in ans:
            return False, f"含主观词「{w}」"
    for w in ("好", "坏"):
        for m in re.finditer(w, ans):
            i = m.start()
            prev = ans[i - 1] if i > 0 else " "
            nxt = ans[i + 1] if i + 1 < len(ans) else " "
            if (prev in "，。；、（）\s" or not prev.isalpha()) and \
                    (nxt in "，。；、（）\s" or not nxt.isalpha()):
                return False, f"含独立主观词「{w}」"
    if len(ans) < 20:
        return False, "答案过短"
    if not reason:
        return False, "缺审核说明"
    return True, reason


def main():
    for db in (DB, DB_W):
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        now = time.time()
        added = skipped = rejected = 0
        for name, ans, domain, edu, reason in ENTRIES:
            ok, note = audit(ans, reason)
            if not ok:
                print(f"  ✗ 拒绝 [{domain}] {name[:14]}：{note}")
                rejected += 1
                continue
            cur.execute("SELECT COUNT(*) FROM nodes WHERE content LIKE ?",
                        ('%' + ans[:20] + '%',))
            if cur.fetchone()[0] > 0:
                print(f"  — 已存在 [{domain}] {name[:14]}")
                skipped += 1
                continue
            node_id = f"kp_archaeo_{int(time.time()*1000)}"
            cs = json.dumps({"observation_position": "知识考古补全",
                             "observation_tool": "前沿既有知识（审核后）",
                             "time_window": [now, now + 31536000],
                             "existence_constraint": "复杂系统/认知科学标准定义"}, ensure_ascii=False)
            sa = json.dumps({"name": name, "domain": domain, "level": 4,
                             "status": "verified",
                             "response": {"trigger": [name]}}, ensure_ascii=False)
            cur.execute(
                "INSERT INTO nodes (id, content, modality, spatial_coordinates, temporal_coordinate, "
                "condition_space, importance, confidence, layer, access_count, last_access, created_at, "
                "tags, semantic_coordinates, state_attributes, entity_id) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (node_id, ans, "text", "{}", now, cs, 0.8, 0.9, "knowledge", 0, now, now,
                 json.dumps(["知识飞轮", "知识考古", f"domain:{domain}", f"edu:{edu}",
                             "verified", "前沿知识"], ensure_ascii=False),
                 "{}", sa, None))
            added += 1
            print(f"  ✓ [{domain}] {name[:16]} → {ans[:36]}...")
        conn.commit()
        print(f"库 {db[-36:]}: 添加 {added} / 跳过 {skipped} / 拒绝 {rejected}")
        conn.close()


if __name__ == "__main__":
    main()
