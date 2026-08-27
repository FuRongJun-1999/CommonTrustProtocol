# -*- coding: utf-8 -*-
"""bootstrap_loop.py · 白箱自举后台循环（长期任务执行体）

角色纪律（荣 2026-08-28）：代码/数据/规则由白箱自己编写；
外部协作者仅提供规范（任务书）与外部校准（验收测试）。

通道 A（本轮启用的全自动闭环）：
  路由缺口扫描（白箱自检）→ triggers 补丁生成 → 独立验证 → 固化
  任一补丁验证失败即撤销该补丁（快照纪律），不影响其它补丁。

用法：
  python tools/bootstrap_loop.py --interval 300          # 每 5 分钟一轮，长期跑
  python tools/bootstrap_loop.py --once                  # 单轮（校准用）
  python tools/bootstrap_loop.py --once --max-patches 5  # 限补丁数
日志：tools/bootstrap_log.jsonl（每轮一行结果）
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WISDOM = os.path.join(ROOT, "aeis", "wisdom")
sys.path.insert(0, WISDOM)
sys.path.insert(0, HERE)

LOG = os.path.join(HERE, "bootstrap_log.jsonl")
STATE = os.path.join(HERE, "bootstrap_state.json")


def log_event(evt: dict) -> None:
    evt["ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(evt, ensure_ascii=False) + "\n")


# ---------------- 通道 A · 路由缺口扫描与补丁 ----------------
def scan_route_gaps(limit_units: int | None = None) -> list[dict]:
    """白箱自检：全量单元逐一探测——生效条件/名称构造探测问题，
    domain_route 未命中本单元 = 路由缺口。"""
    from code_compose import domain_route, DOMAIN_UNITS

    gaps = []
    domains = list(DOMAIN_UNITS.keys())
    total = sum(len(DOMAIN_UNITS[d]) for d in domains)
    count = 0
    for dom in domains:
        for uid, unit in DOMAIN_UNITS[dom].items():
            count += 1
            if limit_units and count > limit_units:
                return gaps
            # 探测问题：名称 + 任务词（最长信息优先的可读形式）
            triggers = [t for t in (unit.get("triggers") or []) if len(t) >= 2]
            probe_terms = [uid] + ([triggers[0]] if triggers else [])
            probe = f"写一个{uid}单元（{triggers[0] if triggers else unit.get('task', '')}）"
            try:
                r = domain_route(probe)
            except Exception as e:
                gaps.append({"domain": dom, "unit": uid,
                             "probe": probe, "error": str(e)[:60]})
                continue
            hit_unit = r.get("unit")
            if hit_unit != uid or not r.get("ok"):
                gaps.append({"domain": dom, "unit": uid, "probe": probe,
                             "got": hit_unit or r.get("reason", "?"),
                             "suggest_triggers": [t for t in triggers]})
    return gaps


def build_trigger_patch(gap: dict) -> dict | None:
    """缺口 → triggers 补丁：按连字符分词取长段（保子串可命中性）。"""
    uid = gap["unit"]
    parts = [p for p in uid.split("-") if len(p) >= 2]
    if not parts:
        return None
    return {"domain": gap["domain"], "unit": uid, "add_triggers": parts[:3]}


def apply_patch(patch: dict) -> bool:
    """补丁应用：写入单元 triggers（幂等——已有词不重复）。"""
    from code_compose import DOMAIN_UNITS
    unit = DOMAIN_UNITS.get(patch["domain"], {}).get(patch["unit"])
    if unit is None:
        return False
    cur = set(unit.get("triggers") or [])
    new = [t for t in patch["add_triggers"] if t not in cur and len(t) >= 2]
    if not new:
        return True          # 无新增=无需变更，视为成功
    unit["triggers"] = (unit.get("triggers") or []) + new
    return True


def verify_patch(patch: dict) -> bool:
    """补丁双重验证：①应用态 probe 命中本单元；②同域其它单元探测
    不被本补丁新词抢走（回归保护——快照纪律粒度）。"""
    from code_compose import domain_route
    uid = patch["unit"]
    dom_units = DOMAIN_TRIGGERS.get(patch["domain"], {})
    triggers = dom_units.get(uid) or []
    probe = f"写一个{uid}单元（{triggers[0] if triggers else uid}）"
    r = domain_route(probe)
    if not (r.get("unit") == uid and r.get("ok")):
        return False
    # 反向抽查：同域其它单元的 probe 仍命中自己
    for other_uid, other_trig in dom_units.items():
        if other_uid == uid:
            continue
        op = f"写一个{other_uid}单元（{other_trig[0] if other_trig else other_uid}）"
        ro = domain_route(op)
        if ro.get("unit") and ro.get("unit") != other_uid:
            return False
    return True


# 全局 triggers 镜像（apply_patch 写内存，verify 后才落盘）
DOMAIN_TRIGGERS: dict[str, dict[str, list]] = {}


def load_source_units() -> None:
    """读源码态单元定义（内存镜像，供补丁生成/验证/落盘）。"""
    global DOMAIN_TRIGGERS
    from code_compose import DOMAIN_UNITS
    DOMAIN_TRIGGERS = {dom: {uid: (u.get("triggers") or []) for uid, u in units.items()}
                       for dom, units in DOMAIN_UNITS.items()}


def persist_triggers_to_source() -> int:
    """验证通过的补丁落盘：把内存 triggers 写回单元源文件（最小 diff）。"""
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
    for dom, path in files.items():
        if not os.path.exists(path):
            continue
        units_dom = DOMAIN_TRIGGERS.get(dom, {})
        if not units_dom:
            continue
        src = open(path, encoding="utf-8").read()
        n_before = src
        for uid, trig in units_dom.items():
            if not trig:
                continue
            # 单元定义行后插入 triggers 行（若尚无 triggers 字段）
            pat = re.compile(r'(\n(\s*)"' + re.escape(uid) + r'": \{\n)')
            if f'"{uid}"' in src and f'"triggers"' not in _unit_block(src, uid):
                m = pat.search(src)
                if m:
                    ind = m.group(2)
                    trig_json = json.dumps(trig, ensure_ascii=False)
                    src = src[:m.end(1)] + f'{ind}    "triggers": {trig_json},\n' + src[m.end(1):]
                    changed += 1
        if src != n_before:
            open(path, "w", encoding="utf-8").write(src)
    return changed


def _unit_block(src: str, uid: str) -> str:
    """取单元定义块（粗略：从 uid 行起 30 行内）。"""
    import re
    m = re.search(r'"' + re.escape(uid) + r'": \{[\s\S]{0,1200}', src)
    return m.group(0) if m else ""


# ---------------- 主循环 ----------------
def run_once(max_patches: int = 20) -> dict:
    import semantic_translate as _  # 确保模块环境
    load_source_units()

    result = {"gaps": 0, "patches_applied": 0, "patches_verified": 0,
              "patches_failed": 0, "persisted_files": 0}

    # ① 白箱自检：路由缺口扫描
    gaps = scan_route_gaps()
    result["gaps"] = len(gaps)
    if not gaps:
        log_event({"round": "scan", "result": "no_gaps"})
        return result

    # ② 补丁生成（白箱：数据自扩展）
    patches = []
    for g in gaps[:max_patches]:
        p = build_trigger_patch(g)
        if p and p["add_triggers"]:
            patches.append(p)

    # ③ 逐补丁应用+验证（失败撤销单个补丁——快照纪律粒度）
    persisted = []
    for p in patches:
        if not apply_patch(p):
            result["patches_failed"] += 1
            continue
        if verify_patch(p):
            result["patches_verified"] += 1
            persisted.append(p)
        else:
            # 撤销：从内存镜像移除刚加的词
            unit_m = DOMAIN_TRIGGERS.get(p["domain"], {}).get(p["unit"], [])
            for t in p["add_triggers"]:
                if t in unit_m:
                    unit_m.remove(t)
            result["patches_failed"] += 1
    result["patches_applied"] = len(persisted)

    # ④ 固化落盘（验证全过后一次性写源文件）
    if persisted:
        result["persisted_files"] = persist_triggers_to_source()

    log_event({"round": "bootstrap", **{k: v for k, v in result.items()}})
    return result


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="白箱自举后台循环")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--interval", type=int, default=300)
    ap.add_argument("--max-patches", type=int, default=20)
    ap.add_argument("--max-rounds", type=int, default=0, help="0=无限")
    args = ap.parse_args()

    rnd = 0
    while True:
        rnd += 1
        try:
            r = run_once(args.max_patches)
            print(f"[轮 {rnd}] 缺口 {r['gaps']} | 补丁 {r['patches_applied']} | "
                  f"验证过 {r['patches_verified']} | 落盘文件 {r['persisted_files']}")
        except Exception as e:
            log_event({"round": rnd, "error": f"{type(e).__name__}: {str(e)[:120]}"})
            print(f"[轮 {rnd}] 异常隔离: {e}")
        if args.once:
            break
        if args.max_rounds and rnd >= args.max_rounds:
            break
        time.sleep(args.interval)
    return 0


if __name__ == "__main__":
    sys.exit(main())
