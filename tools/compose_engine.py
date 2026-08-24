# -*- coding: utf-8 -*-
"""compose_engine.py · 白箱自举原型 v2——条件化单元 + 方向推理 + 组合生成 + 内部自校验
理论依据：《白箱自举设计_条件化单元与组合引擎.md》（§八b v2 方向推理设计）
v1 结果（2026-08-23）：组合结构成立 7/7，但暴露缺方向推理（晾干→沸腾/结霜→熔化错配）
v2 修复：
  ① 单元加 direction（物态变化方向）→ 期望方向优先匹配
  ② 结论生成模板：场景事实 → 因果演绎 → 生成「新答案句」（非完整答案查表）
  ③ 自校验加强：方向一致性 + 因果链完整性 → 白箱自己发现 v1 的错配错误
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')


# ============ 一、条件化单元库（v2：带 direction + conclusion 模板） ============
# direction: 物态变化方向（组合匹配用）| conclusion: 结论生成模板（{...} 为占位）

CONDITION_UNITS = {
    "沸点-气压": {
        "conditions": ["气压"],
        "direction": "气压效应",
        "rule": {"低": "沸点降低", "高": "沸点升高", "标准": "沸点=100°C"},
        "default": "标准大气压下纯水沸点 100°C",
        # 结论模板：气压效应 → 温度后果 → 生活影响（占位代入）
        "conclusion": {
            "低": "气压低 → {液体}沸点降至100°C以下 → {液体}达不到100°C就沸腾",
            "高": "气压高 → {液体}沸点升至100°C以上 → {液体}能到100°C以上才沸腾",
        },
        "examples": ["高原(0.65atm)水沸点约88°C", "高压锅(2atm)水沸点约120°C"],
        "domain": "物态变化",
        "source": "沸点与气压簇蒸馏（条件化重构）",
    },
    "沸腾-条件": {
        "conditions": ["液体", "供热"],
        "direction": "液→气(剧烈)",
        "rule": "达到沸点+持续供热 → 内部与表面同时剧烈汽化",
        "default": "沸腾=液体内部与表面同时汽化的剧烈蒸发",
        "conclusion": {"default": "{液体}达到沸点且持续供热 → 剧烈沸腾（温度保持沸点不再升）"},
        "examples": ["水烧开=沸腾", "沸腾时温度不再升高"],
        "domain": "物态变化",
        "source": "沸腾簇蒸馏",
    },
    "蒸发-条件": {
        "conditions": ["液体", "温度", "表面积", "通风"],
        "direction": "液→气(缓慢)",
        "rule": {"温度": "温度↑→蒸发越快", "表面积": "表面积↑→蒸发越快",
                 "通风": "通风↑→蒸发越快"},
        "default": "蒸发=液体表面在任何温度下都能发生的缓慢汽化",
        "conclusion": {
            "温度": "{液体}温度越高 → 蒸发越快 → 干得越快",
            "表面积": "{液体}摊开面积越大 → 蒸发越快 → 干得越快",
            "通风": "{液体}表面风越大 → 蒸发越快 → 干得越快",
        },
        "examples": ["晾衣摊开干得快", "夏天干得快", "有风干得快"],
        "domain": "物态变化",
        "source": "蒸发簇蒸馏",
    },
    "液化-条件": {
        "conditions": ["气体", "降温"],
        "direction": "气→液",
        "rule": {"降温": "气体降温 → 液化（遇冷凝结）"},
        "default": "液化=气体遇冷/受压变为液体（放热）",
        "conclusion": {"降温": "{气体}遇冷 → 液化成小水珠（镜片起雾=水蒸气液化）"},
        "examples": ["镜片起雾", "液化石油气"],
        "domain": "物态变化",
        "source": "液化簇蒸馏",
    },
    "凝固-条件": {
        "conditions": ["液体", "降温"],
        "direction": "液→固",
        "rule": {"降温": "液体降温到凝固点 → 凝固（放热）"},
        "default": "凝固=液体变为固体，放热",
        "conclusion": {"降温": "{液体}降温到凝固点 → 凝固成{固体}（水结冰=凝固）"},
        "examples": ["水结冰=凝固", "北方泼水成冰"],
        "domain": "物态变化",
        "source": "凝固簇蒸馏",
    },
    "熔化-条件": {
        "conditions": ["固体", "升温"],
        "direction": "固→液",
        "rule": {"升温": "固体升温到熔点 → 熔化（吸热）"},
        "default": "熔化=固体变为液体，吸热",
        "conclusion": {"升温": "{固体}升温到熔点 → 熔化成液体（冰化成水=熔化）"},
        "examples": ["冰化成水", "铁在高温下熔化"],
        "domain": "物态变化",
        "source": "熔化簇蒸馏",
    },
    "升华-条件": {
        "conditions": ["固体", "升温"],
        "direction": "固→气",
        "rule": {"升温": "固体直接变为气体 → 升华（吸热）"},
        "default": "升华=固态直接变气态，不经过液态",
        "conclusion": {
            "升温": "{固体}直接变为气体 → 升华（吸热）",
            "default": "{固体}直接变为气体 → 升华（樟脑丸放久变小=升华）",
        },
        "examples": ["樟脑丸变小", "干冰直接变气", "冰冻衣服晾干"],
        "domain": "物态变化",
        "source": "升华簇蒸馏",
    },
    "凝华-条件": {
        "conditions": ["气体", "降温"],
        "direction": "气→固",
        "rule": {"降温": "气体直接变为固体 → 凝华（放热）"},
        "default": "凝华=气态直接变固态，不经过液态",
        "conclusion": {"降温": "{气体}遇冷直接变为固体 → 凝华（霜=水蒸气凝华）"},
        "examples": ["霜=凝华", "窗花冰花=凝华"],
        "domain": "物态变化",
        "source": "凝华簇蒸馏",
    },
}

# 方向 → 候选单元（期望方向优先匹配）
DIR_INDEX = {}
for uid, unit in CONDITION_UNITS.items():
    DIR_INDEX.setdefault(unit["direction"], []).append(uid)

# 维度 → 候选单元（兜底匹配）
DIM_INDEX = {}
for uid, unit in CONDITION_UNITS.items():
    for dim in unit["conditions"]:
        DIM_INDEX.setdefault(dim, []).append(uid)


# ============ 二、场景条件事实表（问题中抽取的事实，不是答案） ============

SCENE_FACTS = {
    "高原":   {"气压": "低",   "海拔": "高",   "液体": "水"},
    "珠峰":   {"气压": "低",   "海拔": "极高", "液体": "水"},
    "高压锅": {"气压": "高",   "密封": "增压", "液体": "水", "固体": "食物"},
    "标准大气": {"气压": "标准"},
    "晾衣":   {"液体": "衣服上的水", "表面积": "大", "通风": "好", "温度": "环境温度"},
    "夏天":   {"温度": "高",   "液体": "衣服上的水"},
    "有风":   {"通风": "好",   "液体": "衣服上的水"},
    "冰箱":   {"温度": "低",   "环境": "湿", "气体": "水蒸气"},
    "冷天":   {"温度": "低",   "液体": "湖水", "固体": "冰"},
    "热天":   {"温度": "高"},
    "镜片":   {"气体": "水蒸气", "降温": "冷镜片"},
    "樟脑":   {"固体": "樟脑丸"},
}

SCENE_ALIAS = {
    "高原": ["高原", "西藏", "青海", "海拔高", "山上"],
    "珠峰": ["珠峰", "珠穆朗玛峰", "喜马拉雅"],
    "高压锅": ["高压锅", "压力锅"],
    "标准大气": ["标准大气", "平原地", "常温常压", "正常情况下"],
    "晾衣": ["晾衣", "晒衣服", "衣服", "晾晒"],
    "夏天": ["夏天", "暴晒", "阳光下", "夏天晒"],
    "有风": ["有风", "刮风", "通风", "风"],
    "冰箱": ["冰箱", "冷冻", "冷藏", "结霜", "除霜"],
    "冷天": ["冬天", "寒冷", "低温", "结冰", "冻", "湖面"],
    "热天": ["高温", "热"],
    "镜片": ["镜片", "眼镜", "起雾"],
    "樟脑": ["樟脑", "樟脑丸"],
}

DIM_KEYWORDS = {
    "气压": ["气压", "高压", "低压", "高原", "海拔", "珠峰", "压力", "密封", "增压", "大气"],
    "温度": ["温度", "高温", "低温", "加热", "降温", "冷", "热", "夏天", "冬天", "晒", "冻"],
    "表面积": ["表面积", "摊开", "面积", "展开"],
    "通风": ["风", "通风", "吹"],
    "液体": ["水", "液体", "油", "汤", "汁", "湖水"],
    "固体": ["冰", "固体", "铁", "樟脑", "干冰", "食物"],
    "气体": ["蒸气", "蒸汽", "气体", "水蒸气", "气"],
    "供热": ["烧", "煮", "加热", "供热", "火"],
}

# ============ 三、方向识别（v2 核心：问题动词 → 期望物态变化方向） ============
# 「晾干」期望 液→气(蒸发)；「结霜」期望 气→固(凝华)——v1 缺失的推理

DIRECTION_KEYWORDS = {
    "气压效应": ["沸点", "烧不", "煮不", "煮饭", "熟", "不到100", "不到一百", "提前开"],
    "液→气(缓慢)": ["干", "晾", "晒干", "蒸发", "变干"],
    "液→气(剧烈)": ["烧开", "沸腾", "开", "煮开", "冒泡"],
    "气→液": ["起雾", "凝结", "液化", "水珠", "雾", "挂水"],
    "液→固": ["结冰", "凝固", "冻住", "冻"],
    "固→液": ["融化", "熔化", "化", "融", "化成水"],
    "固→气": ["变小", "消失", "升华", "不见了"],
    "气→固": ["结霜", "凝华", "霜", "窗花", "冰花", "雪"],
}

# 方向推理：动词比维度更具体 → 优先用方向匹配单元
def identify_direction(query):
    """识别问题的期望物态变化方向
    场景优先：高原/珠峰问题即使含「开/沸腾」，方向是气压效应（气压低→沸点低）"""
    scene = identify_scene(query)
    if scene in ("高原", "珠峰") and any(k in query for k in ("开", "烧", "沸")):
        return "气压效应"
    for direction, kws in DIRECTION_KEYWORDS.items():
        if any(k in query for k in kws):
            return direction
    return None


# ============ 四、已验证事实库（自校验对照基准） ============

VERIFIED_FACTS = [
    {"content": "标准大气压下纯水沸点100°C", "domain": "物态变化"},
    {"content": "高原上水沸点降低（约88°C）", "domain": "物态变化"},
    {"content": "高压锅内水沸点升高（约120°C）", "domain": "物态变化"},
    {"content": "沸腾时温度不再升高", "domain": "物态变化"},
    {"content": "水蒸气遇冷液化成小水珠（镜片起雾）", "domain": "物态变化"},
    {"content": "水结冰是凝固（放热）", "domain": "物态变化"},
    {"content": "冰化成水是熔化（吸热）", "domain": "物态变化"},
    {"content": "樟脑丸变小是升华", "domain": "物态变化"},
    {"content": "霜是水蒸气凝华形成的", "domain": "物态变化"},
    {"content": "晾晒衣服干得快（蒸发加快）", "domain": "物态变化"},
    {"content": "有风时衣服干得更快", "domain": "物态变化"},
    {"content": "冬天湖面结冰是凝固", "domain": "物态变化"},
    {"content": "冰箱结霜是水蒸气凝华", "domain": "物态变化"},
]


# ============ 五、组合引擎 v2（方向优先 → 单元匹配 → 结论生成 → 自校验） ============

def identify_scene(query):
    for scene, aliases in SCENE_ALIAS.items():
        if any(a in query for a in aliases):
            return scene
    return None


def identify_condition_dims(query):
    """识别问题的条件维度（词面 → 条件域，v1 保留作兜底）"""
    dims = []
    for dim, kws in DIM_KEYWORDS.items():
        if any(k in query for k in kws):
            dims.append(dim)
    return dims


def match_units_by_direction(direction, dims):
    """② 期望方向优先匹配单元；无方向则按维度兜底"""
    if direction and direction in DIR_INDEX:
        # 方向匹配：取该方向首个单元；若场景事实提供更具体维度，再精化
        uid = DIR_INDEX[direction][0]
        return [(uid, CONDITION_UNITS[uid])]
    # 维度兜底（v1 逻辑）
    chain = []
    for dim in dims:
        uids = DIM_INDEX.get(dim, [])
        if uids:
            chain.append((uids[0], CONDITION_UNITS[uids[0]]))
    return chain


def generate_conclusion(unit, scene, facts, direction):
    """③ 结论生成：单元结论模板 + 场景事实代入 → 新答案句（未预写）"""
    conclusion = unit.get("conclusion", {})
    if not conclusion:
        return unit["default"]
    # 选模板：气压效应按 低/高 选；蒸发按事实维度选；其他按场景事实优先
    key = None
    temp = facts.get("温度", "")
    if unit["direction"] == "气压效应" and facts.get("气压") in ("低", "高"):
        key = facts["气压"]
    elif unit["direction"].startswith("液→气(缓慢)") and direction == "液→气(缓慢)":
        for dim in ("温度", "表面积", "通风"):
            if dim in facts and dim in conclusion:
                key = dim
                break
    elif "降温" in conclusion and (facts.get("降温") or ("低" in temp or "冷" in temp)):
        key = "降温"
    elif "升温" in conclusion and (facts.get("升温") or ("高" in temp or "热" in temp)):
        key = "升温"
    elif "default" in conclusion:
        key = "default"
    if key is None:
        return unit["default"]
    tpl = conclusion[key]
    # 占位代入：{液体}{固体}{气体} 来自场景事实或问题本身
    fill = {
        "液体": facts.get("液体", "水"),
        "固体": facts.get("固体", "冰"),
        "气体": facts.get("气体", "水蒸气"),
    }
    for k, v in fill.items():
        tpl = tpl.replace("{" + k + "}", v)
    return tpl


def compose_answer(query):
    """组合生成：方向识别 → 单元匹配 → 结论生成"""
    scene = identify_scene(query)
    direction = identify_direction(query)
    dims = identify_condition_dims(query)
    if not dims and not direction:
        return None, "条件不足（诚实边界）", None, None, None

    chain = match_units_by_direction(direction, dims)
    if not chain:
        return None, "无匹配单元（条件链不完整）", None, None, None

    facts = SCENE_FACTS.get(scene, {}) if scene else {}
    answer = generate_conclusion(chain[0][1], scene, facts, direction)
    return scene, answer, chain, facts, direction


def scene_direction_conflict(scene, facts, direction, answer, query):
    """场景-方向相容性：场景事实与期望方向/生成结论矛盾检测（白箱自发现错误）
    注：高原/珠峰不算「低温不能沸腾」——珠峰沸腾真实存在（气压低→沸点低），
    由气压效应解释，非温度矛盾"""
    temp = facts.get("温度", "")
    # ① 低温场景不能剧烈沸腾（沸腾需达到沸点的高温；冷天/冰箱温度低）
    if direction == "液→气(剧烈)" and ("低" in temp or "冷" in temp
                                        or scene in ("冷天", "冰箱")):
        return "低温场景不能剧烈沸腾：{scene}温度低，水达不到沸点".format(scene=scene or "该场景")
    # ② 气压低场景（高原/珠峰）水达不到高温——问题却期望「特别热/烫」
    if scene in ("高原", "珠峰") and any(w in query for w in ("特别热", "烫", "很热", "温度高")):
        return "气压低场景水达不到高温：问题期望「热」与事实「气压低→沸点低」矛盾"
    # ③ 高温场景不能结冰/凝华
    if direction in ("液→固", "气→固") and ("高" in temp or "热" in temp):
        return "高温场景不会{dir}：场景温度高，与期望方向矛盾".format(dir=direction)
    return None


def self_check(scene, answer, chain, facts, direction, query):
    """自校验 v2：方向一致性 + 因果链完整性 + 事实一致性 + 场景相容性（白箱自己发现错误）"""
    checks = []
    ok = True
    uid, unit = chain[0]

    # ① 方向一致性：生成单元方向 vs 问题期望方向（v1 错配的检测器）
    if direction and unit["direction"] != "气压效应" and unit["direction"] != direction:
        ok = False
        checks.append(f"✗ 方向错配：问题期望[{direction}]，匹配到[{unit['direction']}]单元"
                      f"（{uid}）——应匹配方向一致单元")
    elif direction and unit["direction"] == "气压效应" and "沸点" not in answer:
        ok = False
        checks.append("✗ 气压效应未落地：问题含沸点/气压期望，生成未体现沸点变化")

    # ② 场景-方向相容性（v2b：矛盾问题检测）
    conflict = scene_direction_conflict(scene, facts, direction, answer, query)
    if conflict:
        ok = False
        checks.append(f"✗ 场景矛盾：{conflict}")

    # ③ 因果链完整性：答案应有「前提→结论」结构（含 → 因果连词）
    if "→" not in answer:
        ok = False
        checks.append(f"✗ 因果链不完整：生成「{answer}」无 前提→结论 结构")

    # ④ 事实一致性：与已验证事实矛盾检测
    for fact in VERIFIED_FACTS:
        fc = fact["content"]
        if scene in ("高原", "珠峰") and "高原" in fc and "降低" in fc:
            if "升高" in answer:
                ok = False
                checks.append(f"✗ 事实矛盾：{scene}气压低却生成「沸点升高」——与「{fc}」冲突")
        if scene == "高压锅" and "高压锅" in fc and "升高" in fc:
            if "降低" in answer:
                ok = False
                checks.append(f"✗ 事实矛盾：高压锅气压高却生成「沸点降低」——与「{fc}」冲突")
        if "结霜" in fc and direction == "气→固" and "凝华" not in answer and "霜" not in answer:
            ok = False
            checks.append(f"✗ 事实矛盾：结霜应凝华，生成未体现——与「{fc}」冲突")
        if "结冰" in fc and direction == "液→固" and "凝固" not in answer:
            ok = False
            checks.append(f"✗ 事实矛盾：结冰应凝固，生成未体现——与「{fc}」冲突")

    return ok, checks


def route_compose(query):
    """组合引擎统一入口（Route 递归，输出含证据链，可解释）"""
    scene, answer, chain, facts, direction = compose_answer(query)
    if chain is None:
        return {"query": query, "ok": False, "reason": answer,
                "scene": scene, "chain": None, "checks": []}
    ok, checks = self_check(scene, answer, chain, facts, direction, query)
    return {
        "query": query, "scene": scene, "direction": direction,
        "units": [c[0] for c in chain],
        "answer": answer, "ok": ok, "checks": checks,
        "chain_evidence": [c[1]["source"] for c in chain],
    }


# ============ 六、自举判定统计 ============

def bootstrap_report(results, error_queries=None):
    total = len(results)
    gen_ok = sum(1 for r in results if r.get("answer") and not r["answer"].startswith(("条件不足", "无匹配")))
    selfcheck_ok = sum(1 for r in results if r["ok"])
    # 错误检测率：故意设计的矛盾问题应被自校验抓住（✘=自发现错误=成功）
    if error_queries:
        caught = sum(1 for r in results
                     if r["query"] in error_queries and not r["ok"])
        print("=== 白箱自举判定（物态域 v2） ===")
        print(f"组合生成成功率: {gen_ok}/{total} = {gen_ok/total*100:.0f}% （目标≥80%）")
        print(f"正常问题自校验通过率: {selfcheck_ok}/{total - len(error_queries)} "
              f"= {selfcheck_ok/(total-len(error_queries))*100:.0f}% （目标≥90%）")
        print(f"矛盾问题检测率: {caught}/{len(error_queries)} = {caught/len(error_queries)*100:.0f}% "
              f"（白箱自己发现生成错误——自举核心）")
    else:
        print("=== 白箱自举判定（物态域 v2） ===")
        print(f"组合生成成功率: {gen_ok}/{total} = {gen_ok/total*100:.0f}% （目标≥80%）")
        print(f"内部自校验通过率: {selfcheck_ok}/{total} = {selfcheck_ok/total*100:.0f}% （目标≥90%）")
    print(f"注: 组合生成 = 未预写完整答案，由 方向推理+场景事实×规律单元 演绎拼出")


if __name__ == "__main__":
    demos = [
        "高原上煮饭为什么不容易熟？",
        "高压锅为什么煮得快？",
        "珠峰上烧水为什么不到100°C就开？",
        "为什么夏天晾衣服干得快？",
        "为什么有风的时候衣服干得更快？",
        "冰箱为什么会结霜？",
        "为什么冬天湖面会结冰？",
        "为什么冬天眼镜会起雾？",
        "樟脑丸为什么放久了变小？",
        # 自校验演示：白箱应自己发现这些矛盾问题
        "高原上水为什么烧得特别热？",
        "冬天湖面为什么会沸腾？",
    ]
    error_queries = {"高原上水为什么烧得特别热？", "冬天湖面为什么会沸腾？"}
    results = []
    for q in demos:
        r = route_compose(q)
        results.append(r)
        mark = "✔" if r["ok"] else "✘"
        print(f"\nQ: {q}")
        print(f"  [方向={r.get('direction')} 场景={r.get('scene')} 单元={r.get('units')}]")
        print(f"  {mark} 组合生成: {r['answer']}")
        if r["ok"] and r.get("chain_evidence"):
            print(f"    证据源: {r['chain_evidence']}")
        for c in r["checks"]:
            print(f"    {c}")
    print()
    bootstrap_report(results, error_queries)
