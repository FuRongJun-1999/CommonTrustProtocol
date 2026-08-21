# -*- coding: utf-8 -*-
"""知识考古 · 批次1 补卡（2026-08-21）

#6 信息论（9卡）+ #8 动力学系统（5卡）+ #9 信号处理与谱分析（5卡）
= 19 张前沿知识卡 → 图谱（主库 + 随包库）

审核纪律（知识飞轮沿用）：
  - 物理基底可验证（香农熵公式/奈奎斯特定理/STDP 机制——客观定义）
  - 拒绝主观词（独立成词的 好/坏/我觉得/应该）
  - 每条带审核说明 + 条件空间 + 学科域/学段标签
  - 不宣称首创：既有知识，贡献在纳入协议坐标系
"""
import sys, io, json, sqlite3, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DB = r"C:\Users\FuRongJun\.dsh\profiles\web\data\lingshu.db"
DB_W = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db"

# (概念名, 答案, 学科域, 学段, 审核说明)
ENTRIES = [
    # ============ #6 信息论 ============
    ("香农熵", "香农熵 H(X) = -Σ p(x)·log₂p(x)，度量随机变量的不确定性——确定性系统熵为0，均匀分布熵最大。熵是信息量的期望，是信息差D_norm的数学底座（协议：信息差增定律对应熵增）。",
     "信息论", "E4", "香农1948《通信的数学理论》定义，可验证"),
    ("互信息", "互信息 I(X;Y) = H(X) - H(X|Y) = ΣΣ p(x,y)·log[p(x,y)/(p(x)p(y))]，度量两个变量共享的信息量——观测Y后X不确定性的减少。互信息为0当且仅当X、Y独立。是图谱结构学习的度量。",
     "信息论", "E4", "信息论标准定义，可验证"),
    ("KL散度", "KL散度 D_KL(P‖Q) = Σ p(x)·log[p(x)/q(x)]，度量分布P相对于Q的信息损失（非对称、非负、为0当且仅当P=Q）。不是距离（不满足对称性/三角不等式）。是条件空间距离的度量。",
     "信息论", "E4", "信息论标准定义，可验证"),
    ("信道容量", "信道容量 C = max I(X;Y)，是信道能可靠传输的最大信息率。香农信道编码定理：只要码率R<C，存在编码使错误率任意小；R>C则无法可靠传输。",
     "信息论", "E4", "香农信道编码定理，可验证"),
    ("率失真理论", "率失真理论：在给定失真上限D时，最小码率 R(D)——信息压缩的边界。语音/图像/视频压缩的理论基础（MP3/JPEG/H.264）。",
     "信息论", "E4", "香农率失真理论，可验证"),
    ("信息瓶颈", "信息瓶颈：寻找表示T，最大化T与目标Y的互信息、最小化T与输入X的互信息——压缩输入保留相关信息。是最优表示的数学框架。",
     "信息论", "E4", "Tishby 1999信息瓶颈原理，可验证"),
    ("Kolmogorov复杂度", "Kolmogorov复杂度 K(x)：生成字符串x的最短程序长度——算法信息论的核心，与香农熵互补（熵=统计不确定性，K=算法复杂度）。最小描述长度MDL据此选择模型。",
     "信息论", "E4", "Kolmogorov 1965定义，可验证"),
    ("奈奎斯特-香农采样定理", "奈奎斯特-香农采样定理：采样率须≥信号最高频率的2倍（fs≥2f_max）才能无失真重建。低于奈奎斯特率→混叠（aliasing）。是观测物理边界的数学表述。",
     "信息论", "E4", "奈奎斯特1928/香农1949定理，可验证"),
    ("数据压缩熵界", "无损压缩的下界是信源熵：任何无损编码的平均码长≥H(X)（香农源编码定理）。霍夫曼编码/算术编码逼近此界。",
     "信息论", "E4", "香农源编码定理，可验证"),
    # ============ #8 动力学系统 ============
    ("相空间与吸引子", "相空间：系统全部状态构成的几何空间。吸引子：系统长期演化的收敛集合——固定点（稳定态）、极限环（周期振荡）、奇怪吸引子（混沌）。认知状态可视为相空间中的轨迹。",
     "动力学系统", "E4", "动力学系统标准概念，可验证"),
    ("李雅普诺夫稳定性", "李雅普诺夫稳定性：若系统从平衡点附近出发始终留在附近→稳定；且最终收敛→渐近稳定。李雅普诺夫函数V(x)>0且dV/dt<0是稳定的充分条件。",
     "动力学系统", "E4", "李雅普诺夫1892稳定性理论，可验证"),
    ("分岔理论", "分岔：参数微小变化导致系统定性行为突变——鞍结分岔（平衡点成对出现/消失）、霍普夫分岔（固定点→极限环振荡）。是相变/认知切换的数学描述。",
     "动力学系统", "E4", "动力系统分岔理论，可验证"),
    ("Kuramoto模型", "Kuramoto模型：dφ_i/dt = ω_i + (K/N)·Σ sin(φ_j-φ_i)，描述耦合振子的相位同步——耦合强度K超过临界值K_c时，振子自发锁相。蜂群广播节律同步的数学底（信任=耦合权重）。",
     "动力学系统", "E4", "Kuramoto 1975模型，可验证"),
    ("混沌与蝴蝶效应", "混沌：确定性系统对初始条件敏感依赖——微小差异指数放大（李雅普诺夫指数>0）。蝴蝶效应是混沌的通俗表达。混沌≠随机（有确定规则）。",
     "动力学系统", "E4", "洛伦兹1963混沌研究，可验证"),
    # ============ #9 信号处理与谱分析 ============
    ("傅里叶变换", "傅里叶变换：把时域信号分解为不同频率的正弦分量叠加——F(ω)=∫f(t)e^(-iωt)dt。逆变换无损恢复。频域视角下：卷积变乘法（卷积定理），高频=快速变化=细节，低频=趋势=结构。",
     "信号处理", "E4", "傅里叶1822热分析理论，可验证"),
    ("小波变换", "小波变换：多尺度时频分析——用不同尺度的小波基分解信号，同时保留时间与频率信息（弥补FFT只给全局频率的缺陷）。是信息分型处理（CNN权值共享）的数学对应。",
     "信号处理", "E4", "Mallat 1989小波多分辨率分析，可验证"),
    ("滤波器组", "滤波器组：一组带通滤波器将信号分解到不同频段（低通/带通/高通），可重构。多分辨率分析的基础，对应五层记忆的频段模型（锚点=DC/结构=低频/知识=中频/情境=高频）。",
     "信号处理", "E4", "信号处理滤波器组理论，可验证"),
    ("自适应滤波", "自适应滤波：滤波器系数随输入统计变化自动调整——LMS（最小均方）通过梯度下降最小化误差。是信息差驱动的学习（预测误差→调整）的经典实现。",
     "信号处理", "E4", "Widrow 1960 LMS算法，可验证"),
    ("功率谱密度", "功率谱密度 S(ω)=|F(ω)|²：信号能量在频率上的分布。频谱能量=该频段的信息量/结构偏离程度（协议：频谱能量=信息差的分频段度量）。",
     "信号处理", "E4", "信号处理功率谱定义，可验证"),
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
                             "existence_constraint": "数学/信息论/动力学/信号处理标准定义"}, ensure_ascii=False)
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
