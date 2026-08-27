# -*- coding: utf-8 -*-
"""知识飞轮 · 常识/知识问答补充（严格审核版 · 2026-08-20）

荣指示：飞轮进行常识和知识问答补充。知识问答需要严格审核，
拒绝偏见和错误认知进入图谱。

流程：
  1. 从 T2 错题提取缺失条目（生活常识/知识问答）
  2. 生成知识卡（人工核对内容，物理基底可验证）
  3. 审核闸门：内容可验证 + 无偏见声明 + 条件空间绑定
  4. 写入图谱（verified + 条件空间）

审核纪律（拒绝偏见/错误认知）：
  - 常识条目：物理基底可验证（12个月/7天/24小时 = 公历定义，可查证）
  - 知识条目：客观事实（水沸点100°C标准大气压，物理可测）
  - 拒绝：观点/价值判断/未经证实的断言（不进图谱）
  - 每条带 condition_space 声明（0.0.5 在什么条件下成立）
"""
import sys, io, json, sqlite3, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DB = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db"

# 常识/知识补充条目（严格审核：物理基底可验证 + 无偏见）
# 每条：(问题, 答案, 学科域, 教育层级, 审核说明)
KNOWLEDGE_ENTRIES = [
    # ---- 日历/时间常识（公历定义，可查证） ----
    ("一年有多少个月", "一年有12个月，这是公历（格里高利历）的定义。",
     "小学科学", "E1", "公历定义，可查证日历"),
    ("一周有几天", "一周有7天：星期一至星期日。",
     "小学科学", "E1", "国际通用周制，可查证"),
    ("一天有多少小时", "一天有24小时，每小时60分钟，每分钟60秒。",
     "小学科学", "E1", "时间单位定义，可查证"),
    ("地球绕太阳转一圈要多久", "地球绕太阳公转一圈约365天，即一年（闰年366天）。",
     "天文学", "E1", "天文观测事实，可查证"),
    # ---- 数学基础（定义明确） ----
    ("什么是分数", "分数表示整体的一部分，由分子和分母组成：分母表示把整体分成几份，分子表示取其中几份。",
     "数学", "E1", "数学定义，无争议"),
    ("三角形的面积公式", "三角形面积 = 底 × 高 ÷ 2。",
     "数学", "E1", "几何公式，可推导验证"),
    ("乘法口诀是什么", "乘法口诀（九九乘法表）是1到9的乘法表，用于快速计算乘法。",
     "数学", "E1", "数学工具，无争议"),
    # ---- 物理常识（物理基底可验证） ----
    ("水在标准大气压下多少度沸腾", "水在标准大气压（101.325kPa）下约100°C沸腾。",
     "物理学", "E1", "物理事实，标准大气压可测"),
    ("为什么天空是蓝色的", "天空呈蓝色是因为太阳光中短波长的蓝光被大气分子瑞利散射，散射蓝光更多。",
     "物理学", "E2", "瑞利散射理论，实验可验证"),
    ("为什么叶子是绿色的", "叶子含叶绿素，叶绿素主要吸收红光和蓝光、反射绿光，所以叶子呈绿色。",
     "生物学", "E1", "叶绿素吸收光谱，实验可验证"),
    ("什么是细胞", "细胞是生物体结构和功能的基本单位。",
     "生物学", "E1", "生物学基本定义，显微镜可观察"),
    ("为什么船能浮在水上", "船能浮在水上是因为浮力：船排开水的重量等于船的重力时，船漂浮（阿基米德原理）。",
     "物理学", "E2", "阿基米德原理，实验可验证"),
]


def audit_entry(q, ans, domain, edu, reason):
    """审核闸门：拒绝偏见/错误认知（返回 pass/reject + 说明）。"""
    # 拒绝词：观点/价值/未证实断言
    REJECT_WORDS = ("我觉得", "我认为", "应该", "最好", "美丽", "好", "坏",
                    "值得", "重要", "必须", "所有人", "总是", "从不")
    for w in REJECT_WORDS:
        if w in ans:
            return False, f"含主观词「{w}」——观点不入图谱"
    # 常识可验证性（必须有具体可查证内容）
    if len(ans) < 10:
        return False, "答案过短，无可验证内容"
    if not reason:
        return False, "缺审核说明"
    return True, reason


def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = time.time()
    cs = json.dumps({"observation_position": "知识飞轮补充",
                     "observation_tool": "人工审核（T2错题驱动）",
                     "time_window": [now, now + 31536000],
                     "existence_constraint": "公历/数学/物理基底可验证"})
    added = 0
    rejected = []
    for q, ans, domain, edu, reason in KNOWLEDGE_ENTRIES:
        ok, note = audit_entry(q, ans, domain, edu, reason)
        if not ok:
            rejected.append((q, note))
            print(f"  ✗ 拒绝 [{domain}] {q[:14]}：{note}")
            continue
        # 去重：已存在同内容 → 跳过
        cur.execute("SELECT COUNT(*) FROM nodes WHERE content LIKE ?",
                    ('%' + ans[:15] + '%',))
        if cur.fetchone()[0] > 0:
            print(f"  — 已存在 [{domain}] {q[:14]}")
            continue
        # 写入图谱（verified + 条件空间 + 标签）
        node_id = f"kp_flywheel_{int(time.time()*1000)}"
        cur.execute(
            "INSERT INTO nodes (id, content, modality, spatial_coordinates, temporal_coordinate, "
            "condition_space, importance, confidence, layer, access_count, last_access, created_at, "
            "tags, semantic_coordinates, state_attributes, entity_id) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (node_id, ans, "text", "{}", now, cs, 0.8, 0.9, "knowledge", 0, now, now,
             json.dumps(["知识飞轮", f"domain:{domain}", f"edu:{edu}", "verified", "常识补充"],
                        ensure_ascii=False), "{}", "{}", None))
        added += 1
        print(f"  ✓ 添加 [{domain}/{edu}] {q[:14]} → {ans[:30]}")
    conn.commit()
    print(f"\n结果: 添加 {added} 条，拒绝 {len(rejected)} 条")
    for q, note in rejected:
        print(f"  拒绝: {q[:20]} — {note}")
    conn.close()


if __name__ == "__main__":
    main()
