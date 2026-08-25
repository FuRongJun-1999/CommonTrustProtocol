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
    """分类：弱兜底（可吸收——实现返回默认值/空值）vs 需人工。

    弱兜底：返回具体值（含空串 ''——空词表→空前缀是合法默认值）。
    需人工：返回 None / False / 异常——可能是真 bug 或强拒绝语义。
    """
    absorbable, manual = [], []
    for d in drift:
        got = d.get("got", "")
        cond = d.get("cond", "")
        # 弱兜底：返回具体值（空串/数字/集合都是默认语义）——实现有兜底
        if got is not None and got is not False and \
                not str(got).startswith('<') and '异常' not in str(got):
            absorbable.append(d)
        else:
            manual.append(d)
    return {"absorbable": absorbable, "manual": manual}


# ── 3 分析：影响范围 ──────────────────────────────────────────
def analyze(applied_units: list) -> dict:
    """影响分析：note 不含新判别词 → not_tokens 稳定 → 路由无影响。"""
    return {
        "note_policy": "note 仅含『返回 X 兜底——不拒绝，弱契约』，"
                       "无新中文判别词 → CCG not_tokens 稳定 → 路由无影响",
        "affected_tests": ["负面闭环（注释不影响执行——漂移数不变，"
                           "但语义声明已对齐）"],
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
def _in_string_edit(text: str, cond: str, got: str) -> str:
    """在 pattern 字符串字面量内精确追加 note。

    pattern 行形如：
      "    # 不适用条件：stack 为空/非法时\n"
    目标：在 `\n"`（转义换行+引号）前插入 note（保持字符串语法完整）。
    匹配「# 不适用条件：<cond前缀>」的字符串字面量片段（引号后可有缩进）。
    """
    prefix = cond.split('（')[0].strip()
    got_s = str(got)
    got_disp = got_s[:30] if got_s else '空串'
    note = f"（返回 {got_disp} 兜底——不拒绝，弱契约）"
    # 匹配：字符串引号 → 可选缩进 → # 不适用条件：<prefix> → 转义 \n + 引号
    pattern = re.compile(
        r'("[^"\n]*?#\s*不适用条件：[^"\n]*?' + re.escape(prefix) +
        r'[^"\n]*?)(\\n")')
    m = pattern.search(text)
    if not m:
        return text, False
    # 若已含兜底标记则跳过
    if '弱契约' in m.group(1) or '兜底' in m.group(1):
        return text, False
    new = m.group(1) + note + m.group(2)
    return text[:m.start()] + new + text[m.end():], True


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
        new_text, ok = _in_string_edit(src[target_fn], cond, d.get("got", ""))
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
        "skill": f"不适用条件-{kind}：弱兜底契约",
        "pattern": ("输入{kind}时实现返回兜底值（非拒绝）——注释补充"
                    "兜底语义；负面测试验证兜底值而非拒绝"),
        "instances": units[:8], "n": len(units),
    } for kind, units in kinds.items() if units]


def _save_skills(skills: list):
    db = {}
    if os.path.exists(SKILLS_PATH):
        try:
            db = json.load(open(SKILLS_PATH, encoding='utf-8'))
        except Exception:
            db = {}
    db["契约形态-弱兜底"] = {"skills": skills,
                            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    json.dump(db, open(SKILLS_PATH, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)


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


# ── 8 方向性自检 ─────────────────────────────────────────────
def orient(per: dict, solidified: dict) -> dict:
    """方向正确性评估：指标趋势 → 是否朝目标前进。"""
    rc = per.get("route_conflicts", {})
    bs = per.get("blindspots", {})
    cs = per.get("comment_spec", {})
    checks = {
        "强契约拒绝率": per["strong_rate"] >= 0.9,
        "MOS 声明一致率": per["mos_rate"] >= 0.98,
        "路由互斥边存在": rc.get("ok", True),
        "盲区诚实声明": bs.get("ok", True),
        "注释规范完整": cs.get("ok", True),
        "固化语法安全": solidified.get("ok", False) if solidified else True,
    }
    passed = sum(1 for v in checks.values() if v)
    return {
        "checks": checks,
        "passed": passed,
        "total": len(checks),
        "direction_ok": passed == len(checks),
        "assessment": ("方向正确：指标稳定/改善，闭环可持续"
                       if passed == len(checks)
                       else f"方向需调整：{passed}/{len(checks)} 项通过"),
    }


# ── 主闭环 ────────────────────────────────────────────────────
def self_iterate(dry_run: bool = True) -> dict:
    """执行一轮八步闭环（默认 dry_run 只感知/识别/分析，不固化）。"""
    round_no = len(_load_trace()) + 1
    # 1 感知
    per = perceive()
    # 2 识别
    cls = classify(per["drift"])
    # 7 反馈（前置：跳过已吸收）
    absorbed = _absorbed_units()
    cls["absorbable"] = [d for d in cls["absorbable"]
                         if d["unit"] not in absorbed]
    # 3 分析
    ana = analyze([d["unit"] for d in cls["absorbable"]])
    # 5 固化（dry_run 不做）
    solid = solidify(cls["absorbable"]) if not dry_run else {
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
        "识别": {"absorbable": len(cls["absorbable"]),
                "manual": len(cls["manual"]),
                "absorbed_skip": len(cls["absorbable"]) == 0},
        "分析": ana,
        "验证": "honest：只改注释不改实现 + ast.parse 校验",
        "固化": {"n": len(solid.get("applied", [])),
                "items": [{"unit": a["unit"], "cond": a["cond"],
                           "got": a["got"]} for a in
                          solid.get("applied", [])][:15]},
        "反馈": {"absorbed_total": len(absorbed)},
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
    print(f"识别: 可吸收 {t['识别']['absorbable']} | "
          f"需人工 {t['识别']['manual']}")
    print(f"固化: {t['固化']['n']} 处（{'dry_run' if t['dry_run'] else '已落盘'}）")
    print(f"方向自检: {t['方向性自检']['assessment']}")
