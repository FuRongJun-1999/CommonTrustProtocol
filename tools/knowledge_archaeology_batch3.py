# -*- coding: utf-8 -*-
"""知识考古 · 批次3 补卡（2026-08-21）

#4 脑功能研究（7卡）+ #5 控制论补齐（5卡）= 12 张前沿知识卡 → 图谱

审核纪律（沿用知识飞轮 + 批次1/2）：
  - 物理基底可验证（STDP机制/卡尔曼滤波/神经振荡——客观定义）
  - 拒绝主观词（独立成词的 好/坏/我觉得/应该）
  - 每条带审核说明 + 条件空间 + 学科域/学段标签
  - 不宣称首创：既有学术成果，贡献在纳入协议坐标系
"""
import sys, io, json, sqlite3, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DB = r"C:\Users\FuRongJun\.dsh\profiles\web\data\lingshu.db"
DB_W = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db"

ENTRIES = [
    # ============ #4 脑功能研究 ============
    ("突触可塑性", "突触可塑性：神经元间连接强度可随使用改变——LTP（长时程增强，高频刺激后连接增强）、LTD（长时程抑制，低频刺激后减弱）。是学习与记忆的细胞机制。",
     "脑功能", "E4", "Bliss-Lomo 1973 LTP发现，实验可验证"),
    ("STDP", "STDP（时序依赖可塑性）：突触权重按前后神经元放电时序调整——前神经元先放电则连接增强（因果），后放电则减弱（非因果）。是Hebbian规则的时序精确版。",
     "脑功能", "E4", "STDP是计算神经科学标准机制，实验可验证"),
    ("神经振荡", "神经振荡：神经元群体节律性同步放电——δ(1-4Hz睡眠)/θ(4-8Hz记忆)/α(8-13Hz放松)/β(13-30Hz警觉)/γ(30-100Hz注意绑定)。是蜂群节律的脑对应。",
     "脑功能", "E4", "脑电振荡频段划分，EEG实验可验证"),
    ("预测编码", "预测编码：大脑是层级预测机器——每层用预测解释输入，只向上传递预测误差（实际-预测的差异）。是信息差D_norm的神经对应（缩小预测误差=缩小信息差）。",
     "脑功能", "E4", "Rao-Ballard 1999预测编码，神经影像可验证"),
    ("前额叶执行功能", "前额叶执行功能：工作记忆更新、抑制控制（克制冲动）、任务切换、计划——认知控制的核心区域。对应协议自我层/约束执行。",
     "脑功能", "E4", "神经心理学执行功能研究，可验证"),
    ("默认模式网络", "默认模式网络（DMN）：静息态下活跃的脑区网络（内侧前额叶/后扣带回/角回）——自我参照、心智游荡、自传体记忆。是自我层/元认知的神经基底。",
     "脑功能", "E4", "Raichle 2001 DMN发现，fMRI可验证"),
    ("睡眠记忆巩固", "睡眠记忆巩固：睡眠中记忆被重新激活并巩固——慢波睡眠（海马→新皮层重放）、锐波涟漪、快速眼动。是灵枢睡眠巩固/情境层提升的脑对应。",
     "脑功能", "E4", "睡眠研究标准结论，可验证"),
    # ============ #5 控制论补齐 ============
    ("卡尔曼滤波", "卡尔曼滤波：最优状态估计的递归算法——预测步（用模型预测下一状态）+更新步（用观测校正，按不确定性加权）。是预测误差学习（信息差驱动）的工程化。",
     "控制论", "E4", "Kalman 1960滤波算法，工程可验证"),
    ("PID控制", "PID控制：比例-积分-微分三环节——P（按当前误差响应）、I（消除稳态误差）、D（抑制超调）。工业控制最广泛。是负反馈的经典实现。",
     "控制论", "E4", "PID控制是工程标准，可验证"),
    ("自由能原理", "自由能原理（FEP）：生物系统最小化自由能（变分自由能=预测误差+复杂度）——主动推理：通过行动改变输入使预测成立。是预测编码的统一框架。",
     "控制论", "E4", "Friston 2010自由能原理，理论框架可验证"),
    ("内稳态", "内稳态（homeostasis）：系统通过负反馈维持内部状态稳定——体温/血糖/渗透压调节。是维生系统（保持存在）的生物学基础。",
     "控制论", "E4", "Cannon 1926内稳态概念，生理学可验证"),
    ("二阶控制论", "二阶控制论：观察者包含在系统内——控制论的控制论（观察者自身的观察过程）。对应协议元认知/自我层（系统观察自己的观察）。",
     "控制论", "E4", "von Foerster 二阶控制论，可验证"),
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
                             "existence_constraint": "脑功能/控制论标准定义"}, ensure_ascii=False)
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
