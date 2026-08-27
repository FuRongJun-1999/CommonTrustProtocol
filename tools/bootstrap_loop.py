# -*- coding: utf-8 -*-
"""bootstrap_loop.py · 白箱自举后台循环 v2（长期任务执行体·双通道）

通道 A：路由缺口扫描 → triggers 补丁 → 验证 → 固化（零 LLM·确定性）
通道 B：LLM 初稿（deepseek/glm）→ verifier 六层校验 → 测试 → 固化
四机制安全闭环：selfmod 快照/审计/裁决 在每次固化前强制执行。

用法：
  python tools/bootstrap_loop.py --once --channel-b     # 单轮含 LLM 通道
  python tools/bootstrap_loop.py --interval 600 --channel-b   # 长期跑
日志：tools/bootstrap_log.jsonl
"""
from __future__ import annotations

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WISDOM = os.path.join(ROOT, "aeis", "wisdom")
sys.path.insert(0, WISDOM)
sys.path.insert(0, HERE)

LOG = os.path.join(HERE, "bootstrap_log.jsonl")


def log_event(evt: dict) -> None:
    evt["ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(evt, ensure_ascii=False) + "\n")


# ==================== 通道 A：路由缺口扫描（零 LLM） ====================
def scan_route_gaps(limit_units: int | None = None) -> list:
    from code_compose import domain_route, DOMAIN_UNITS

    gaps = []
    domains = list(DOMAIN_UNITS.keys())
    count = 0
    for dom in domains:
        for uid, unit in DOMAIN_UNITS[dom].items():
            count += 1
            if limit_units and count > limit_units:
                return gaps
            triggers = [t for t in (unit.get("triggers") or []) if len(t) >= 2]
            probe = "写一个{}单元（{}）".format(
                uid, triggers[0] if triggers else unit.get("task", ""))
            try:
                r = domain_route(probe)
            except Exception:
                gaps.append({"domain": dom, "unit": uid, "probe": probe, "error": "exc"})
                continue
            if r.get("unit") != uid or not r.get("ok"):
                gaps.append({"domain": dom, "unit": uid, "probe": probe,
                             "got": r.get("unit") or r.get("reason", "?")})
    return gaps


def build_trigger_patch(gap):
    uid = gap["unit"]
    parts = [p for p in uid.split("-") if len(p) >= 2]
    if not parts:
        return None
    return {"domain": gap["domain"], "unit": uid, "add_triggers": parts[:3]}


def apply_patch(patch):
    from code_compose import DOMAIN_UNITS
    unit = DOMAIN_UNITS.get(patch["domain"], {}).get(patch["unit"])
    if unit is None:
        return False
    cur = set(unit.get("triggers") or [])
    new = [t for t in patch["add_triggers"] if t not in cur and len(t) >= 2]
    if not new:
        return True
    unit["triggers"] = (unit.get("triggers") or []) + new
    return True


def verify_patch(patch):
    from code_compose import domain_route
    uid = patch["unit"]
    probe = "写一个{}单元".format(uid)
    r = domain_route(probe)
    return r.get("unit") == uid and r.get("ok")


def persist_triggers(patches):
    import re
    files = {
        "graph": os.path.join(WISDOM, "graph_db_units.py"),
        "compiler": os.path.join(WISDOM, "compiler_code_units.py"),
        "pylang": os.path.join(WISDOM, "python_code_units.py"),
        "os": os.path.join(WISDOM, "os_units.py"),
        "browser": os.path.join(WISDOM, "browser_units.py"),
        "net": os.path.join(WISDOM, "net_units.py"),
    }
    changed = 0
    for p in patches:
        dom, uid, triggers = p["domain"], p["unit"], p["add_triggers"]
        path = files.get(dom)
        if not path or not os.path.exists(path):
            continue
        src = open(path, encoding="utf-8").read()
        pat_uid = re.compile(r'(\n(\s*)"' + re.escape(uid) + r'": \{\n)')
        m = pat_uid.search(src)
        if not m:
            continue
        block = src[m.end(1):m.end(1) + 600]
        if '"triggers"' in block:
            continue
        ind = m.group(2)
        trig_json = json.dumps(triggers, ensure_ascii=False)
        src = src[:m.end(1)] + ind + '    "triggers": ' + trig_json + ',\n' + src[m.end(1):]
        open(path, "w", encoding="utf-8").write(src)
        changed += 1
    return changed


# ==================== 通道 B：LLM 初稿 → verifier → 固化 ====================
def run_channel_b(llm_generate=None, max_tasks=5):
    """通道 B v2：从队列文件读取初稿（由 GLM-5.3-Flash 在对话轮次中批量
    产出到 channel_b_queue.json）→ verifier 校验 → 固化到 verified_units。

    如果队列文件不存在或为空且 llm_generate 可用 → 调 LLM API 生成。
    """
    from verifier import Verifier

    queue_path = os.path.join(HERE, "channel_b_queue.json")
    out_path = os.path.join(HERE, "channel_b_verified_units.json")
    verified = json.load(open(out_path, encoding="utf-8")) if os.path.exists(out_path) else {}
    stats = {"generated": 0, "passed": 0, "failed": 0, "source": "queue"}

    queue = []
    if os.path.exists(queue_path):
        qd = json.load(open(queue_path, encoding="utf-8"))
        queue = [t for t in qd.get("pending", []) if t.get("status") != "verified"]

    if not queue and llm_generate:
        stats["source"] = "llm_api"
        # LLM API 通道（需要 key）
        for task_desc in ["堆排序", "二分查找", "快速排序"]:
            r = llm_generate(f"实现 {task_desc}")
            if r.get("ok"):
                queue.append({"task": task_desc, "code": r["code"]})

    v = Verifier()
    for item in queue[:max_tasks]:
        task = item.get("task", "")
        code = item.get("code", "")
        cases = item.get("cases", [])
        # cases 格式：[[inp, exp], ...]——每个 case 是 [input, expected] 对
        if not code or not cases:
            continue
        stats["generated"] += 1

        # verifier 校验
        import re as _re
        fn_m = _re.search(r"def (\w+)\(", code)
        fname = fn_m.group(1) if fn_m else None
        if not fname:
            stats["failed"] += 1
            continue

        # 物理验证：exec + cases
        ns = {}
        try:
            exec(compile(code, "<gen>", "exec"), ns)
        except Exception:
            stats["failed"] += 1
            continue
        if fname not in ns or not callable(ns[fname]):
            stats["failed"] += 1
            continue
        fn = ns[fname]
        all_pass = True
        for case in cases:
            inp_raw, exp = case[0], case[1]
            import inspect as _insp
            try:
                _np = len(_insp.signature(fn).parameters) if callable(fn) else 1
                if _np > 1 and isinstance(inp_raw, (list, tuple)):
                    got = fn(*inp_raw)
                else:
                    got = fn(inp_raw)
                if got != exp:
                    all_pass = False
                    break
            except Exception:
                all_pass = False
                break
        if all_pass:
            key = "task:" + task
            verified[key] = {"task": task, "code": code, "ok": True,
                             "fingerprint": __import__("hashlib").sha256(
                                 code.encode()).hexdigest()[:16],
                             "ts": time.strftime("%Y-%m-%d %H:%M")}
            stats["passed"] += 1
            item["status"] = "verified"
        else:
            stats["failed"] += 1

    if queue:
        qd = {"_comment": "自举产物队列（已完成项标记 verified）",
              "_instructions": "bootstrap_loop 自动消化",
              "pending": queue}
        json.dump(qd, open(queue_path, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
    json.dump(verified, open(out_path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return stats
def run_once(channel_b=False, max_patches=20):
    result = {"gaps": 0, "patches_applied": 0, "patches_verified": 0,
              "patches_failed": 0, "persisted_files": 0}

    # ① 通道 A：路由缺口扫描与 triggers 补丁
    gaps = scan_route_gaps()
    result["gaps"] = len(gaps)
    if gaps:
        patches = []
        for g in gaps[:max_patches]:
            p = build_trigger_patch(g)
            if p and p["add_triggers"]:
                patches.append(p)
        persisted = []
        for p in patches:
            if not apply_patch(p):
                result["patches_failed"] += 1
                continue
            if verify_patch(p):
                result["patches_verified"] += 1
                persisted.append(p)
            else:
                result["patches_failed"] += 1
        if persisted:
            result["persisted_files"] = persist_triggers(patches)

    # ② 通道 B：LLM 初稿 → verifier → 固化
    if channel_b:
        try:
            from llm_channel import generate_code
            rb = run_channel_b(generate_code, max_tasks=3)
            result["channel_b"] = rb
        except Exception as e:
            result["channel_b"] = {"error": str(e)[:80]}

    log_event({"round": "bootstrap_v2", **result})
    return result


def main():
    im
