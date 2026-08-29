# -*- coding: utf-8 -*-
"""selfmod.py · 自修改安全闭环（四机制合一）

《灵枢四机制细化设计_v0.1》实现：
  ① 信息差传感器——五维结构质量信号（路由/知识/代码/认知/信息差收敛），
     scan → 基线 → 自修改 → rescan 对比，退化即拦截
  ② 三臂验证——build（构建）/ audit（独立审计）/ judge（裁决）职责分离，
     审计臂不共享构建臂中间产物（防自己审自己），各留证据链
  ③ 维生显示化——心跳 / 自修改影响面 / 回滚能力 / 维生判定，ALIVE·AT_RISK 可观测
  ④ 快照纪律——自修改前自动快照（附指纹），lingshu_rollback 一条命令撤销

诚实边界：指纹证明状态一致性，不证明修改「有益」；三臂判据是规则化的，
终裁权保留设计者（护栏宪章）。

CLI：
  python selfmod.py scan                     五维传感器扫描
  python selfmod.py snapshot --intent "..."   自修改前快照
  python selfmod.py rollback <snapshot_id>    一键回滚（指纹校验）
  python selfmod.py vitality                  维生状态报告
  python selfmod.py cycle --intent "..."      完整闭环演示（快照→基线→rescan）
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WISDOM = os.path.join(os.path.dirname(HERE), "wisdom")
CLOUD_DB = os.path.join(WISDOM, "wisdom-book-cloud.db")
SNAPSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(HERE)),
                            "snapshots")
SNAP_TARGETS = [CLOUD_DB,
                os.path.join(WISDOM, "code_solidified.json"),
                os.path.join(WISDOM, "mini_python.py")]


def _sha(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


# ==================== ① 信息差传感器 ====================
def sensor_scan(db_path: str | None = None) -> dict:
    """五维结构质量信号（sentrux 闭环的 scan 步）。"""
    db_path = db_path or CLOUD_DB
    report = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "dims": {}}

    # 路由健康：KCCS 注释覆盖率 + 确定性探针
    probe = {}
    try:
        sys_path = os.path.dirname(db_path)
        if sys_path not in sys.path:
            sys.path.insert(0, sys_path)
        from semantic_translate import card_route  # noqa: E402
        from wisdom_book import ConditionDex  # noqa: E402
        dex = ConditionDex(db_path=db_path, fresh=False)
        hits = card_route(dex, "三角形内角和是多少", limit=3)
        probe["route_probe_score"] = max(
            (h.get("_card_raw_score", 0) for h in hits), default=0)
        dex.close()
    except Exception as e:
        probe["route_probe_score"] = -1
        probe["route_error"] = str(e)[:80]
    report["dims"]["路由"] = {
        "probe_score": probe.get("route_probe_score", -1),
        "ok": probe.get("route_probe_score", -1) >= 2}

    # 知识健康：kp 总数 / KCCS 完整率 / 孤儿边
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    n_kp = cur.execute(
        "SELECT COUNT(*) FROM nodes WHERE tags LIKE '%knowledge_point%'"
    ).fetchone()[0]
    kccs_ok = 0
    for (sa,) in cur.execute(
            "SELECT state_attributes FROM nodes WHERE tags LIKE '%knowledge_point%'"):
        try:
            cmt = (json.loads(sa).get("comment") or {})
            if all(cmt.get(k) for k in ("生效条件", "子功能", "执行", "不适用条件")):
                kccs_ok += 1
        except Exception:
            pass
    orphan = cur.execute(
        "SELECT COUNT(*) FROM edges e WHERE e.source_id NOT IN "
        "(SELECT id FROM nodes) OR e.target_id NOT IN (SELECT id FROM nodes)"
    ).fetchone()[0]
    conn.close()
    report["dims"]["知识"] = {
        "kp_total": n_kp, "kccs_complete": kccs_ok,
        "kccs_rate": round(kccs_ok / n_kp, 4) if n_kp else 0,
        "orphan_edges": orphan,
        "ok": orphan == 0 and (kccs_ok == n_kp)}

    # 代码健康：wisdom 包语法全检 + 硬编码残留
    syn_bad = hard = 0
    py_total = 0
    for dp, dn, fn in os.walk(WISDOM):
        dn[:] = [d for d in dn if d != "__pycache__"]
        for f in fn:
            if not f.endswith(".py"):
                continue
            py_total += 1
            p = os.path.join(dp, f)
            src = open(p, encoding="utf-8").read()
            try:
                ast.parse(src)
            except SyntaxError:
                syn_bad += 1
            if re.search(r"D:[\\\\/]Program Files", src):
                hard += 1
    report["dims"]["代码"] = {
        "py_files": py_total, "syntax_bad": syn_bad, "hardcoded": hard,
        "ok": syn_bad == 0 and hard == 0}

    # 认知健康：导航探针（复合→原子 2 层链可走通）
    try:
        sys_path2 = os.path.dirname(db_path)
        if sys_path2 not in sys.path:
            sys.path.insert(0, sys_path2)
        from navigate import navigate_retrieve  # noqa: E402
        from wisdom_book import ConditionDex as _CD  # noqa: E402
        dex2 = _CD(db_path=db_path, fresh=False)
        nav = navigate_retrieve(dex2, "婆媳矛盾怎么处理")
        dex2.close()
        nav_ok = (nav.get("status") == "resolved" and nav.get("depth_used", 0) >= 1)
        nav_detail = f"depth={nav.get('depth_used')} status={nav.get('status')}"
    except Exception as e:
        nav_ok = False
        nav_detail = str(e)[:80]
    report["dims"]["认知"] = {"navigate_ok": nav_ok, "detail": nav_detail,
                              "ok": nav_ok}

    # 信息差收敛：占位（gap_trend 由引擎运行时供给，独立观测不阻断）
    report["dims"]["信息差收敛"] = {"ok": True, "note": "由 gap_trend 外部观测"}

    report["all_ok"] = all(d.get("ok") for d in report["dims"].values())
    return report


def save_baseline(report: dict, baseline_dir: str | None = None) -> str:
    bdir = baseline_dir or os.path.join(SNAPSHOT_DIR, "baseline")
    os.makedirs(bdir, exist_ok=True)
    path = os.path.join(bdir, "baseline.json")
    json.dump(report, open(path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return path


def compare_baseline(current: dict, baseline_path: str) -> dict:
    """rescan 对比：任一维度从 ok→不 ok = 退化（自修改不得固化）。"""
    if not os.path.exists(baseline_path):
        return {"regressed": False, "note": "无基线（首次扫描）"}
    base = json.load(open(baseline_path, encoding="utf-8"))
    regressions = []
    for dim, cur_d in current["dims"].items():
        b_d = (base.get("dims") or {}).get(dim, {})
        if b_d.get("ok") and not cur_d.get("ok"):
            regressions.append(dim)
    return {"regressed": bool(regressions), "regressed_dims": regressions}


# ==================== ④ 快照纪律 ====================
def auto_snapshot(intent: str, targets: list | None = None) -> dict:
    """自修改前置快照：拷贝目标文件 + manifest 记录意图与指纹。"""
    ts = time.strftime("%Y%m%d-%H%M%S")
    sid = f"snap-{ts}"
    sdir = os.path.join(SNAPSHOT_DIR, sid)
    os.makedirs(sdir, exist_ok=True)
    manifest = {"id": sid, "intent": intent, "files": {}}
    for t in (targets or SNAP_TARGETS):
        if os.path.exists(t):
            dst = os.path.join(sdir, os.path.basename(t))
            shutil.copy2(t, dst)
            manifest["files"][t] = {"sha256": _sha(dst), "size": os.path.getsize(dst)}
    json.dump(manifest, open(os.path.join(sdir, "manifest.json"), "w",
                             encoding="utf-8"), ensure_ascii=False, indent=1)
    return manifest


def rollback(snapshot_id: str) -> dict:
    """一键回滚：先校验快照指纹（快照自身未被改），再恢复各文件。"""
    sdir = os.path.join(SNAPSHOT_DIR, snapshot_id)
    manifest_path = os.path.join(sdir, "manifest.json")
    if not os.path.exists(manifest_path):
        return {"ok": False, "error": f"快照不存在：{snapshot_id}"}
    manifest = json.load(open(manifest_path, encoding="utf-8"))
    restored, mismatch = [], []
    for path, meta in manifest["files"].items():
        snap_file = os.path.join(sdir, os.path.basename(path))
        if _sha(snap_file) != meta["sha256"]:
            mismatch.append(os.path.basename(path))
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        shutil.copy2(snap_file, path)
        restored.append(path)
    if mismatch:
        return {"ok": False, "error": f"快照指纹不匹配（快照被改）：{mismatch}"}
    return {"ok": True, "restored": restored}


def list_snapshots() -> list:
    out = []
    if not os.path.isdir(SNAPSHOT_DIR):
        return out
    for sid in sorted(os.listdir(SNAPSHOT_DIR)):
        mf = os.path.join(SNAPSHOT_DIR, sid, "manifest.json")
        if os.path.exists(mf):
            m = json.load(open(mf, encoding="utf-8"))
            out.append({"id": sid, "intent": m.get("intent", ""),
                        "files": len(m.get("files", {}))})
    return out


# ==================== ② 三臂验证 ====================
def build_arm(modification: dict) -> dict:
    """构建臂：登记自修改意图与范围（实际修改由调用方执行）。"""
    return {"arm": "build", "intent": modification.get("intent", ""),
            "targets": modification.get("targets", []),
            "ts": time.strftime("%Y-%m-%d %H:%M:%S")}


def audit_arm(db_path: str = CLOUD_DB) -> dict:
    """审计臂：独立证据采集（语法/硬编码/KCCS/指纹）——不读构建臂中间产物。"""
    evidence = {"checks": []}
    syn_ok = True
    for dp, dn, fn in os.walk(WISDOM):
        dn[:] = [d for d in dn if d != "__pycache__"]
        for f in fn:
            if not f.endswith(".py"):
                continue
            try:
                ast.parse(open(os.path.join(dp, f), encoding="utf-8").read())
            except SyntaxError as e:
                syn_ok = False
                evidence["checks"].append(
                    {"item": f"语法 {f}", "ok": False, "detail": str(e)[:60]})
    evidence["checks"].append({"item": "wisdom 包语法", "ok": syn_ok})
    cur_report = sensor_scan(db_path)
    evidence["kccs_rate"] = cur_report["dims"]["知识"]["kccs_rate"]
    evidence["hardcoded"] = cur_report["dims"]["代码"]["hardcoded"]
    evidence["checks"].append({"item": "KCCS 完整率 100%",
                               "ok": evidence["kccs_rate"] == 1.0})
    evidence["checks"].append({"item": "硬编码零残留", "ok": not evidence["hardcoded"]})
    evidence["audit_ok"] = all(c["ok"] for c in evidence["checks"])
    return evidence


def judge_arm(audit_evidence: dict, baseline_compare: dict) -> dict:
    """裁决臂：对照审计证据与基线对比做终裁（规则化；终裁权保留设计者）。"""
    if not audit_evidence.get("audit_ok"):
        return {"verdict": "revise",
                "reason": "审计臂存在未通过检查项"}
    if baseline_compare.get("regressed"):
        return {"verdict": "reject",
                "reason": f"传感器检出退化维度：{baseline_compare.get('regressed_dims')}——回滚快照"}
    return {"verdict": "pass", "reason": "审计全绿且无基线退化"}


# ==================== ③ 维生显示化 ====================
def vitality_report(db_path: str | None = None) -> dict:
    """维生状态：心跳 / 影响面 / 回滚能力 / 维生判定（ALIVE·AT_RISK）。"""
    db_path = db_path or CLOUD_DB
    heartbeat = {"db_readable": os.path.exists(db_path),
                 "engine_import": True}
    try:
        import aeis.core  # noqa: F401
    except Exception as e:
        heartbeat["engine_import"] = False
        heartbeat["engine_error"] = str(e)[:60]
    nav_probe = False
    nav_detail = ""
    try:
        sys_p = os.path.dirname(db_path)
        if sys_p not in sys.path:
            sys.path.insert(0, sys_p)
        from navigate import navigate_retrieve as _nr  # noqa: E402
        from wisdom_book import ConditionDex as _CD  # noqa: E402
        d2 = _CD(db_path=os.path.abspath(db_path), fresh=False)
        nav = _nr(d2, "婆媳矛盾怎么处理")
        d2.close()
        nav_probe = nav.get("status") == "resolved"
        nav_detail = f"depth={nav.get('depth_used')}"
    except Exception as e:
        nav_detail = f"{type(e).__name__}: {str(e)[:70]}"
    heartbeat["navigation_probe"] = nav_probe
    heartbeat["navigation_detail"] = nav_detail
    heartbeat_ok = heartbeat["db_readable"] and heartbeat["navigation_probe"]

    snaps = list_snapshots()
    rollback_ready = bool(snaps)
    impact = {"uncommitted_hint": "git status 另行查看",
              "snapshots_available": len(snaps)}

    vitality = "ALIVE" if (heartbeat_ok and rollback_ready) else \
        ("AT_RISK" if heartbeat_ok else "CRITICAL")
    return {"vitality": vitality,
            "heartbeat": heartbeat,
            "impact": impact,
            "rollback_ready": rollback_ready,
            "latest_snapshot": snaps[-1] if snaps else None}


# ==================== 闭环编排 ====================
def selfmod_cycle(intent: str, modify_fn=None) -> dict:
    """完整闭环：快照→基线→执行→审计→裁决→rescan→（退化回滚）→报告。"""
    log = []
    snap = auto_snapshot(intent)
    log.append(f"快照 {snap['id']}（{len(snap['files'])} 文件）")
    baseline = sensor_scan(CLOUD_DB)
    save_baseline(baseline)
    log.append("传感器基线已保存")
    build = build_arm({"intent": intent})
    if modify_fn:
        modify_fn()
        log.append("修改已执行")
    audit = audit_arm(CLOUD_DB)
    compare = compare_baseline(sensor_scan(CLOUD_DB),
                               os.path.join(SNAPSHOT_DIR, "baseline",
                                            "baseline.json"))
    judge = judge_arm(audit, compare)
    log.append(f"裁决: {judge['verdict']}（{judge['reason']}）")
    rolled_back = False
    if judge["verdict"] == "reject":
        rb = rollback(snap["id"])
        rolled_back = rb.get("ok", False)
        log.append(f"已回滚: {rolled_back}")
    return {"snapshot": snap["id"], "build": build, "audit_ok": audit["audit_ok"],
            "judge": judge, "rolled_back": rolled_back, "log": log}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="自修改安全闭环（四机制）")
    ap.add_argument("cmd", choices=["scan", "snapshot", "rollback",
                                    "vitality", "cycle", "list"])
    ap.add_argument("--intent", default="手动操作")
    ap.add_argument("extra", nargs="*", default=[])
    a = ap.parse_args()
    if a.cmd == "scan":
        print(json.dumps(sensor_scan(CLOUD_DB), ensure_ascii=False, indent=1))
    elif a.cmd == "snapshot":
        print(json.dumps(auto_snapshot(a.intent), ensure_ascii=False, indent=1))
    elif a.cmd == "rollback":
        print(json.dumps(rollback(a.extra[0] if a.extra else ""), ensure_ascii=False))
    elif a.cmd == "vitality":
        print(json.dumps(vitality_report(CLOUD_DB), ensure_ascii=False, indent=1))
    elif a.cmd == "list":
        print(json.dumps(list_snapshots(), ensure_ascii=False))
    elif a.cmd == "cycle":
        print(json.dumps(selfmod_cycle(a.intent), ensure_ascii=False, indent=1))
