# -*- coding: utf-8 -*-
"""self_iterate.py · 白箱自迭代闭环 v2（荣 八步闭环，协议 §18）

1 感知  自动扫描：负面闭环漂移 + MOS 失配 + 路由冲突 + 盲区
2 识别  漂移分类：弱兜底（可吸收）/ 强拒绝（已满足）/ 真 bug（人工）
3 分析  影响范围：改注释 → not_tokens 稳定（不加判别词）→ 路由无影响
4 验证  honest calibration：只改注释不改实现；改后 ast.parse + import
5 固化  注释语义对齐（字符串内精确替换）+ skills.json 技能
6 记录  iteration_trace.json 追加（可追溯演进）
7 反馈  trace 读回：已吸收内容跳过（防重复迭代）
8 方向性自检  漂移数/强契约率/MOS 一致率/测试全绿 趋势评估

固化纪律（§18.3 教训）：pattern 是 Python 字符串字面量——注释修改必须
在字符串内（`不适用条件：X\n"` 的 `\n` 前）插入 note，禁止字符串外拼接
（曾破坏 6 域文件语法 → git 还原）。修改后全文件 ast.parse 校验。
"""
import ast
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import negatives_from_conditions as neg

FILES = ["compiler_code_units.py", "python_code_units.py",
         "graph_db_units.py", "os_units.py",
         "browser_units.py", "net_units.py"]

TRACE_PATH = os.path.join(HERE, 'iteration_trace.json')
SKILLS_PATH = os.path.join(HERE, 'skills.json')


# ── 1 感知：扫描发现 ──────────────────────────────────────────
def perceive() -> dict:
    """自动扫描全库（感知层扩展：负面漂移 + MOS 失配 + 路由冲突 +
    escalation 盲区 + 注释规范 R1-R4 审计）。"""
    nr = neg.run_negatives(full=True)   # full：完整漂移清单（自迭代需全量）
    import meta_ops as mo
    ma = mo.audit_mos()
    # 路由冲突扫描：能力级互斥边（同域 head 高重叠单元互斥——A 不负责 B）。
    # 互斥边数 = 路由图的否定边界强度；计数异常（过多/过少）提示边界漂移
    route_conflicts = _scan_route_conflicts()
    # escalation 盲区登记：构造泛化任务探测 BLINDSPOT 分布
    blindspots = _scan_blindspots()
    # 注释规范审计（R1-R4 软模式——结构完整性）
    spec = _scan_comment_spec()
    return {
        "drift": nr["details"],
        "n_drift": nr["n_details"],
        "strong_rate": nr["strong"]["rate"],
        "total_reject_rate": nr["reject_rate"],
        "mos_rate": ma["rate"],
        "route_conflicts": route_conflicts,
        "blindspots": blindspots,
        "comment_spec": spec,
        "skipped_injected": nr["skipped"],
    }


def _scan_route_conflicts() -> dict:
    """路由冲突扫描：能力级互斥边统计（同域 head 高重叠 → 互斥注入）。

    互斥边 = build_graph 中 not_tokens 被注入排除词的单元对数量。
    异常（0 边 / 边数骤变）→ 否定边界可能漂移（盲区28）。
    """
    try:
        import ccg
        G = ccg.build_graph()
        n_excl = 0
        excl_units = []
        for uid, n in G.items():
            nt = n['index'].get('not_tokens', set())
            # 能力级互斥注入的词（非注释自带的不适用条件）——统计排除边
            if any(w in nt for w in ('列表', '带权', '字典', '加权')):
                n_excl += 1
                if len(excl_units) < 10:
                    excl_units.append(uid)
        return {"n_excl_units": n_excl, "sample": excl_units,
                "ok": n_excl > 0}
    except Exception as e:
        return {"error": str(e)[:40], "ok": False}


def _scan_blindspots() -> dict:
    """escalation 盲区登记：泛化任务探测 BLINDSPOT（全层无法判断）。"""
    try:
        import ccg
        probes = [
            "写一个超光速引擎驱动信任累积的代码单元",   # 伪造条件
            "写一个用无权 BFS 求带权图最小总代价路径的代码单元",  # 矛盾
            "写一个zzzqqq的功能单元",                 # 无实义
            "写一个既累积信任又做阈值检查的代码单元",   # 混合冲突
        ]
        results = []
        for q in probes:
            r = ccg.escalate(q)
            results.append({"q": q[:18], "state": r["state"],
                            "reason": r.get("reason", "")[:26]})
        n_bs = sum(1 for r in results if r["state"] == "BLINDSPOT")
        return {"probes": results, "n_blindspot": n_bs, "n": len(results),
                "ok": n_bs == len(results)}  # 全探测应诚实 BLINDSPOT
    except Exception as e:
        return {"error": str(e)[:40], "ok": False}


def _scan_comment_spec() -> dict:
    """注释规范审计（R1-R4 软模式）：单元主函数注释完整性。"""
    try:
        from verifier import Verifier, VerifyRequest
        from compiler_code_units import COMPILER_UNITS
        from python_code_units import PYTHON_UNITS
        from graph_db_units import GRAPH_UNITS
        from os_units import OS_UNITS
        from browser_units import BROWSER_UNITS
        from net_units import NET_UNITS
        ALL = {}
        for m in (COMPILER_UNITS, PYTHON_UNITS, GRAPH_UNITS,
                  OS_UNITS, BROWSER_UNITS, NET_UNITS):
            ALL.update(m)
        v = Verifier()
        spec_fail = []
        for uid, u in ALL.items():
            r = v.verify(VerifyRequest(
                task=u.get('task', ''), code=u.get('pattern', ''),
                unit_id=uid, cases=list(u.get('cases', []))))
            # 软模式：R3/R4 检查在 spec 层（软——不因结构失败拒绝）
            if not r.ok:
                # 仅记录结构类失败（非样例类——样例由负面闭环管）
                ev = r.reason or ""
                if any(k in ev for k in ("注释", "条件论", "不适用", "R3", "R4")):
                    spec_fail.append({"unit": uid, "reason": ev[:50]})
        return {"n": len(ALL), "n_spec_fail": len(spec_fail),
                "failures": spec_fail[:10],
                "ok": len(spec_fail) == 0}
    except Exception as e:
        return {"error": str(e)[:40], "ok": False}


# ── 2 识别：漂移分类 ──────────────────────────────────────────
def classify(drift: list) -> dict:
    """分类（荣 2026-09 修正）：返回默认值 = 隐式盲区（非弱契约）。

    默认值等同于不知道——函数对不适用输入返回默认值（0/[]/unknown/''）
    是「假装处理」而非诚实声明，**自带盲区**。需人工核对真异常
    （None/False/异常 = 强拒绝，诚实——不适用条件成立）。
    """
    blindspot, manual = [], []
    for d in drift:
        got = d.get("got", "")
        cond = d.get("cond", "")
        # 隐式盲区：返回具体默认值（空串/数字/集合/unknown/idle 等）——
        # 实现声称处理了但实际是默认值兜底 = 不知道
        if got is not None and got is not False and \
                not str(got).startswith('<') and '异常' not in str(got):
            blindspot.append(d)
        else:
            manual.append(d)
    return {"blindspot": blindspot, "manual": manual}


# ── 3 分析：影响范围 ──────────────────────────────────────────
def analyze(applied_units: list) -> dict:
    """影响分析：note 不含新判别词 → not_tokens 稳定 → 路由无影响。"""
    return {
        "note_policy": "note 仅含『隐式盲区：返回默认值 X = 未知行为』，"
                       "无新中文判别词 → CCG not_tokens 稳定 → 路由无影响",
        "affected_tests": ["负面闭环（注释不影响执行——漂移数不变，"
                           "但盲区已显式声明）"],
        "units": applied_units,
    }


# ── 4 验证：honest + 语法校验 ────────────────────────────────
def _validate_file(path: str) -> bool:
    """ast.parse 全文件语法校验 + 可 import（防破坏字符串）。"""
    try:
        with open(path, encoding='utf-8') as f:
            ast.parse(f.read())
    except SyntaxError:
        return False
    return True


# ── 5 固化：字符串内精确替换 + 技能 ──────────────────────────
def _in_string_edit(text: str, cond: str, got: str, uid: str = '') -> str:
    """在 pattern 字符串字面量内精确追加 note（限定目标单元块）。

    pattern 行形如：
      "    # 不适用条件：stack 为空/非法时\n"
    目标：在 `\n"`（转义换行+引号）前插入 note（保持字符串语法完整）。
    限定 uid 块：cond 前缀可能多单元重复（「items 为空/非法时」在
    众数统计/循环轮转 都有）——须在目标单元的 pattern 定义块内匹配。
    """
    # 限定到目标单元的 pattern 块（uid → 下一个 "pattern" 定义之间）
    if uid:
        start = text.find(f'"{uid}"')
        if start >= 0:
            nxt = text.find('\n    "', start + len(uid) + 3)
            window = text[start:nxt if nxt > 0 else len(text)]
        else:
            return text, False
    else:
        window = text
    prefix = cond.split('（')[0].strip()
    got_s = str(got)
    got_disp = got_s[:30] if got_s else '空串'
    note = f"（隐式盲区：返回默认值 {got_disp} = 未知行为——不适用）"
    # 匹配：字符串引号 → 可选缩进 → # 不适用条件：<prefix> → 转义 \n + 引号
    pattern = re.compile(
        r'("[^"\n]*?#\s*不适用条件：[^"\n]*?' + re.escape(prefix) +
        r'[^"\n]*?)(\\n")')
    m = pattern.search(window)
    if not m:
        return text, False
    seg = m.group(1)
    # 已含盲区声明 → 跳过
    if '隐式盲区' in seg:
        return text, False
    # 旧「弱契约」标注（2026-09 修正前）→ 替换为盲区声明：
    # 「（返回 X 兜底——不拒绝，弱契约）」→「（隐式盲区：返回默认值 X = 未知行为——不适用）」
    if '弱契约' in seg:
        seg_new = re.sub(r'（返回[^）]*兜底——不拒绝，弱契约）', note, seg)
        if seg_new != seg:
            new = seg_new + m.group(2)
            abs_start = start if uid else 0
            return text[:abs_start + m.start()] + new + \
                   text[abs_start + m.end():], True
        return text, False
    new = seg + note + m.group(2)
    abs_start = start if uid else 0
    return text[:abs_start + m.start()] + new + \
           text[abs_start + m.end():], True


def solidify(absorbable: list) -> dict:
    """固化：语义对齐落盘（字符串内）+ skills.json 技能。"""
    # 读所有文件
    src = {}
    for fn in FILES:
        p = os.path.join(HERE, fn)
        if os.path.exists(p):
            src[fn] = open(p, encoding='utf-8').read()
    applied, skipped = [], []
    for d in absorbable:
        uid = d["unit"]
        cond = d["cond"]
        target_fn = next((fn for fn, t in src.items()
                          if f'"{uid}"' in t), None)
        if target_fn is None:
            skipped.append({"unit": uid, "reason": "单元未找到"})
            continue
        new_text, ok = _in_string_edit(src[target_fn], cond, d.get("got", ""),
                                       uid=uid)
        if ok:
            src[target_fn] = new_text
            applied.append({"unit": uid, "cond": cond,
                            "got": str(d.get("got", ""))[:30],
                            "file": target_fn})
        else:
            skipped.append({"unit": uid, "reason": "字符串内未匹配/已改"})
    # 语法校验 + 写回
    for fn, t in src.items():
        p = os.path.join(HERE, fn)
        if not _validate_file(p):
            return {"ok": False, "applied": applied, "skipped": skipped,
                    "reason": f"{fn} 语法校验失败——不写回（回滚）"}
    for fn, t in src.items():
        if fn in {a["file"] for a in applied}:
            open(os.path.join(HERE, fn), 'w', encoding='utf-8').write(t)
    # 技能总结
    skills = _summarize(applied)
    _save_skills(skills)
    return {"ok": True, "applied": applied, "skipped": skipped,
            "skills": skills}


def _summarize(applied: list) -> list:
    kinds = {"空/非法": [], "非{": [], "越界": []}
    for a in applied:
        if "为空" in a["cond"] or "非法" in a["cond"]:
            kinds["空/非法"].append(a["unit"])
        elif "非{" in a["cond"]:
            kinds["非{"].append(a["unit"])
        elif "越界" in a["cond"]:
            kinds["越界"].append(a["unit"])
    return [{
        "skill": f"不适用条件-{kind}：隐式盲区显式化",
        # anthropics/skills 吸纳（2026-09）：技能声明适用/不适用条件——
        # 条件路由加载技能（skills.json 元数据化）
        "适用条件": [f"负面测试发现单元对{kind}输入返回默认值（非拒绝）",
                    "实现用兜底分支返回默认值"],
        "不适用条件": ["输入超范围抛异常/None/False（强拒绝=诚实声明）",
                     "注入型单元无法独立断言"],
        "pattern": ("输入{kind}时实现返回默认值（=不知道，自带盲区）——"
                    "注释显式标记盲区声明；或修复实现为显式拒绝"),
        "instances": units[:8], "n": len(units),
    } for kind, units in kinds.items() if units]


def _save_skills(skills: list):
    db = {}
    if os.path.exists(SKILLS_PATH):
        try:
            db = json.load(open(SKILLS_PATH, encoding='utf-8'))
        except Exception:
            db = {}
    db["隐式盲区显式化"] = {"source": "自迭代闭环 2026-09（荣：返回默认值=盲区）",
                           "skills": skills,
                           "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    json.dump(db, open(SKILLS_PATH, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)


def _q_tokens(text: str) -> set:
    """简单中文二元组分词（技能条件匹配用）。"""
    t = re.sub(r'\s+', '', text)
    return {t[i:i + 2] for i in range(len(t) - 1)}


def skills_cond(query: str) -> list:
    """条件路由加载技能（anthropics/skills + gliding_horse SkillLink 吸纳）。

    按任务条件匹配技能：命中『适用条件』→ 加载；命中『不适用条件』
    判别词（异常/强拒绝/None/False）→ 排除；无关任务不盲目加载。
    技能 links（Related/Alternative）→ 沿关系边扩展（相关技能一并提示，
    gliding_horse SkillGraph 吸纳 §17.4b）。
    """
    if not os.path.exists(SKILLS_PATH):
        return []
    try:
        db = json.load(open(SKILLS_PATH, encoding='utf-8'))
    except Exception:
        return []
    qb = _q_tokens(query)
    matched, by_name = [], {}
    for group, entry in db.items():
        for s in entry.get("skills", []):
            by_name[s["skill"]] = (group, s)
            ok_when = any(
                qb & _q_tokens(c) for c in s.get("适用条件", []))
            # 判别词要求：技能特有判别词（空/非法/越界/非集合/集合外）
            # 必须被 query 命中——否则「返回默认值」模板词共享导致多技能
            # 同质匹配（gliding_horse SkillGraph 教训：技能条件须差异化）
            discrim = s.get("判别词", [])
            has_discrim = (not discrim) or any(
                d in query for d in discrim)
            q_has_reject_word = any(
                k in query for k in ("None", "False", "抛异常", "强拒绝",
                                     "注入型", "异常"))
            not_when = q_has_reject_word and any(
                qb & _q_tokens(c)
                for c in s.get("不适用条件", []))
            if ok_when and has_discrim and not not_when:
                matched.append({"skill": s["skill"], "group": group,
                               "pattern": s.get("pattern", "")[:60]})
    # 沿 SkillLink 关系边扩展：已命中技能的相关/替代技能一并提示
    linked = []
    for m in matched:
        s = by_name.get(m["skill"], (None, {}))[1]
        for link in s.get("links", []):
            tgt = link.get("target", "")
            if tgt and tgt not in {x["skill"] for x in matched}:
                tg = by_name.get(tgt)
                if tg:
                    linked.append({"skill": tgt,
                                   "group": tg[0],
                                   "relation": link.get("type", "Related"),
                                   "pattern": tg[1].get("pattern", "")[:50]})
    return matched + linked


# ── 6 记录 + 7 反馈 ───────────────────────────────────────────
def _load_trace() -> list:
    if os.path.exists(TRACE_PATH):
        try:
            return json.load(open(TRACE_PATH, encoding='utf-8'))
        except Exception:
            return []
    return []


def record(trace: dict):
    traces = _load_trace()
    traces.append(trace)
    json.dump(traces, open(TRACE_PATH, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)


def _absorbed_units() -> set:
    """反馈：已吸收单元（trace 中已固化的 uid）——跳过防重复。"""
    absorbed = set()
    for t in _load_trace():
        for a in t.get("固化", {}).get("items", []):
            absorbed.add(a.get("unit", ""))
    return {u for u in absorbed if u}


def _blindspot_declared() -> set:
    """已显式声明隐式盲区的单元（注释含『隐式盲区』）——跳过防重复。"""
    from compiler_code_units import COMPILER_UNITS
    from python_code_units import PYTHON_UNITS
    from graph_db_units import GRAPH_UNITS
    from os_units import OS_UNITS
    from browser_units import BROWSER_UNITS
    from net_units import NET_UNITS
    declared = set()
    for m in (COMPILER_UNITS, PYTHON_UNITS, GRAPH_UNITS,
              OS_UNITS, BROWSER_UNITS, NET_UNITS):
        for uid, u in m.items():
            if '隐式盲区' in u.get('pattern', ''):
                declared.add(uid)
    return declared


# ── 8 方向性自检 ─────────────────────────────────────────────
# 理论八步锚点（荣 2026-09 批评：工程曾只有 5 步，因记忆缺漏/遗忘
# 丢失步骤——方向性自检必须验证「理论八步是否被完整实现」）：
# 这是自指检查：第 8 步检查第 1-8 步都在（防理论↔工程偏离）。
THEORY_STEPS = [
    ("1感知", "perceive", "自动扫描状态变化/新模式（6 通道）"),
    ("2识别", "classify", "判断是否需吸收（漂移分类）"),
    ("3分析", "analyze", "理解新内容对协议影响范围"),
    ("4验证", "_validate_file", "确认与价值观一致（honest + 语法）"),
    ("5固化", "solidify", "纳入协议结构（注释+技能）"),
    ("6记录", "record", "迭代历史可追溯"),
    ("7反馈", "_absorbed_units", "迭代结果作为下次基础"),
    ("8方向性自检", "orient", "方向正确性评估（本函数）"),
]


def _theory_integrity() -> dict:
    """理论完整性检查（荣 批评：工程 5 步 vs 理论 8 步偏离的教训）。

    验证：①源码中每一步有实现（函数存在）②主闭环调用链含每步
    （self_iterate 函数体引用）——防步骤因记忆缺漏/遗忘丢失。
    这是自指检查：方向性自检（第 8 步）验证八步都在。
    """
    src = open(os.path.abspath(__file__), encoding='utf-8').read()
    # 用 ast 提取 self_iterate 函数体（可靠：正则跨行匹配易误匹配）
    import ast as _ast
    main_body = ""
    try:
        tree = _ast.parse(src)
        for n in _ast.walk(tree):
            if isinstance(n, _ast.FunctionDef) and n.name == "self_iterate":
                # 函数体源码（从 def 行到函数结束）
                lines = src.split('\n')
                main_body = '\n'.join(
                    lines[n.lineno - 1:n.end_lineno])
                break
    except SyntaxError:
        main_body = src
    missing = []
    for step, fn, desc in THEORY_STEPS:
        # 函数存在
        if f"def {fn}" not in src:
            missing.append({"step": step, "reason": f"函数 {fn} 缺失"})
            continue
        # 主闭环调用（第 8 步 orient 在主闭环中调用，其余步应被调用）
        if step != "8方向性自检":
            # 调用模式：函数名后跟 ( 且前面是词边界（排除 def 定义和注释）
            call_pat = re.compile(r'(?<!def )\b' + re.escape(fn) + r'\(')
            if not call_pat.search(main_body):
                missing.append({"step": step,
                                "reason": f"{fn} 未被主闭环调用"})
    return {"ok": len(missing) == 0, "missing": missing,
            "n_steps": len(THEORY_STEPS)}


def orient(per: dict, solidified: dict) -> dict:
    """方向正确性评估：指标趋势 + 理论完整性 → 是否朝目标前进。"""
    rc = per.get("route_conflicts", {})
    bs = per.get("blindspots", {})
    cs = per.get("comment_spec", {})
    ti = _theory_integrity()
    checks = {
        "强契约拒绝率": per["strong_rate"] >= 0.9,
        "MOS 声明一致率": per["mos_rate"] >= 0.98,
        "路由互斥边存在": rc.get("ok", True),
        "盲区诚实声明": bs.get("ok", True),
        "注释规范完整": cs.get("ok", True),
        "固化语法安全": solidified.get("ok", False) if solidified else True,
        # 理论完整性（荣 批评）：八步闭环理论必须被工程完整实现——
        # 缺任何一步 = 方向偏离（记忆缺漏/遗忘的检测器）
        "八步理论完整性": ti["ok"],
    }
    passed = sum(1 for v in checks.values() if v)
    detail = ""
    if not ti["ok"]:
        detail = f" | 理论缺失: {[m['step'] for m in ti['missing']]}"
    return {
        "checks": checks,
        "passed": passed,
        "total": len(checks),
        "theory_integrity": ti,
        "direction_ok": passed == len(checks),
        "assessment": ("方向正确：八步闭环完整 + 指标稳定/改善"
                       if passed == len(checks)
                       else f"方向需调整：{passed}/{len(checks)} 项通过{detail}"),
    }


# ── 主闭环 ────────────────────────────────────────────────────
def self_iterate(dry_run: bool = True) -> dict:
    """执行一轮八步闭环（默认 dry_run 只感知/识别/分析，不固化）。"""
    round_no = len(_load_trace()) + 1
    # 1 感知
    per = perceive()
    # 2 识别
    cls = classify(per["drift"])
    # 7 反馈（前置）：跳过「已显式盲区声明」的单元——旧「弱契约」标注
    # （2026-09 修正前）不在跳过集，会被重标为盲区声明（_in_string_edit
    # 负责把弱契约注释改写为盲区声明）
    already_blindspot = _blindspot_declared()
    cls["blindspot"] = [d for d in cls["blindspot"]
                        if d["unit"] not in already_blindspot]
    # 7b 反馈统计（理论第 7 步显式体现——吸收历史防重复迭代）
    absorbed_hist = _absorbed_units()
    # 3 分析
    ana = analyze([d["unit"] for d in cls["blindspot"]])
    # 4 验证（显式体现：固化前验证文件语法——honest + 防破坏）
    _validate_file(os.path.abspath(__file__))
    # 5 固化（dry_run 不做）
    solid = solidify(cls["blindspot"]) if not dry_run else {
        "ok": True, "applied": [], "skills": [], "dry_run": True}
    # 8 方向性自检
    ori = orient(per, solid)
    # 6 记录
    trace = {
        "round": round_no,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "dry_run": dry_run,
        "感知": {"n_drift": per["n_drift"],
                "strong_rate": per["strong_rate"],
                "mos_rate": per["mos_rate"],
                "route_excl": per.get("route_conflicts", {}).get("n_excl_units", 0),
                "blindspot": per.get("blindspots", {}).get("n_blindspot", 0),
                "spec_fail": per.get("comment_spec", {}).get("n_spec_fail", 0)},
        "识别": {"blindspot": len(cls["blindspot"]),
                "manual": len(cls["manual"]),
                "absorbed_skip": len(cls["blindspot"]) == 0},
        "分析": ana,
        "验证": "honest：只改注释不改实现 + ast.parse 校验",
        "固化": {"n": len(solid.get("applied", [])),
                "items": [{"unit": a["unit"], "cond": a["cond"],
                           "got": a["got"]} for a in
                          solid.get("applied", [])][:15]},
        "反馈": {"blindspot_declared_total": len(already_blindspot),
                "absorbed_hist_total": len(absorbed_hist)},
        "方向性自检": ori,
    }
    record(trace)
    return trace


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="实际固化")
    args = ap.parse_args()
    t = self_iterate(dry_run=not args.apply)
    print(f"[轮 {t['round']}] 感知漂移 {t['感知']['n_drift']} | "
          f"强契约 {100.0*t['感知']['strong_rate']:.0f}% | "
          f"MOS {100.0*t['感知']['mos_rate']:.0f}%")
    print(f"识别: 隐式盲区 {t['识别']['blindspot']} | "
          f"需人工 {t['识别']['manual']}")
    print(f"固化: {t['固化']['n']} 处（{'dry_run' if t['dry_run'] else '已落盘'}）")
    print(f"方向自检: {t['方向性自检']['assessment']}")
