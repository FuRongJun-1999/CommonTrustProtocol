# -*- coding: utf-8 -*-
"""
可复现纪律校验（发布闸门）· REPRO-GATE-001
==========================================
白箱测试基准与随包数据绑定校验——发布前必须通过，否则禁止发布。

背景（2026-08-19 测试报告）：声称 80% 的基准与实际随包图谱脱节，
实测 41-44%——「白箱=可复现」铁律反例。本脚本把「基准」与「随包数据」
绑定：发布时校验当前随包图谱跑出的成绩 == 锁定的基准，不一致即阻断。

校验项：
1. 图谱完整性：随包图谱含学科卡 + 知识点子图（subject_card/knowledge_point）
2. 基准复现：跑 T1 知识测试（110 题）→ 正确率 ≥ 锁定阈值
3. 直接回答率：direct_answer 可用性（非「只导航不回答」）
4. 一致性：各副本图谱哈希一致

用法：
    python repro_gate.py              # 发布前校验（阻断式）
    python repro_gate.py --record     # 记录当前基准（更新锁定阈值）
    python repro_gate.py --quick      # 只查图谱完整性（不跑全量测试）
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

# 锁定基准（2026-08-19 图谱补全后实测）：低于此值 = 回归，阻断发布
# 注意：历史声称 80% 不可复现（图谱/代码已变），基准按当前真实成绩锁定
LOCKED_MIN_SCORE = 0.40          # T1 正确率下限（当前 44%，留 4pp 容差）
LOCKED_MIN_DIRECT = 0.50         # 直接回答率下限（非导航兜底比例）
LOCKED_MIN_KNOWLEDGE_POINTS = 1000  # 知识点子图节点下限（证明学科卡已合入）

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_graph_integrity(db_path: str) -> dict:
    """图谱完整性：学科卡 + 知识点子图。"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM nodes")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM nodes WHERE tags LIKE '%knowledge_point%'")
    kp = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM nodes WHERE tags LIKE '%subject_card%'")
    sc = cur.fetchone()[0]
    conn.close()
    return {"total": total, "knowledge_point": kp, "subject_card": sc}


def run_t1_test() -> dict:
    """跑 T1 知识测试（110 题），返回正确率与直接回答率。"""
    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(REPO_ROOT))
    from extend_test_100 import QUESTIONS
    sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
    from aeis.api import Agent

    agent = Agent(identity="灵枢", db_path=os.environ.get("AEIS_DB", ":memory:"))
    import re as _re

    def score(reply, keys):
        r = reply or ""
        rn = _re.sub(r"[\s^]", "", r).replace("²", "2").replace("³", "3").replace("√", "")
        kn = [_re.sub(r"[\s^]", "", k).replace("²", "2").replace("³", "3") for k in keys]
        return 1.0 if any(k in r or k in rn for k in kn) else 0.0

    correct = 0
    direct = 0  # 有实质回答（非「只导航不回答」）的比例
    # 纯导航判定：回答以「可以看/你说的这个」开头（无答案内容，仅指路）
    nav_prefixes = ("这个可以看「", "你说的这个，可以看「", "可以看「")
    for q, keys, cat in QUESTIONS:
        try:
            r = agent.chat(q, session_id="repro_gate")
            reply = r.get("reply", "")
        except Exception:
            reply = ""
        correct += score(reply, keys)
        stripped = (reply or "").lstrip()
        if reply and not stripped.startswith(nav_prefixes):
            direct += 1
    agent.close()
    n = len(QUESTIONS)
    return {"total": n, "correct": correct,
            "accuracy": correct / n if n else 0,
            "direct_rate": direct / n if n else 0}


def check_replicas(wisdom_db: str) -> dict:
    """副本一致性：site-packages/CTP/1_ai/3_ai 图谱哈希一致。"""
    h = sha256(wisdom_db)
    replicas = [
        r"D:\Program Files\2_ai\CommonTrustProtocol\aeis\wisdom\wisdom-book-cloud.db",
        r"D:\Program Files\3_ai\lingshu-wisdom\wisdom\wisdom-book-cloud.db",
    ]
    ok = True
    for rp in replicas:
        if os.path.exists(rp) and sha256(rp) != h:
            ok = False
    return {"hash": h[:12], "replicas_match": ok}


def main() -> int:
    ap = argparse.ArgumentParser(description="可复现纪律校验（发布闸门）")
    ap.add_argument("--record", action="store_true", help="记录当前基准（更新锁定值）")
    ap.add_argument("--quick", action="store_true", help="只查图谱完整性")
    ap.add_argument("--db", default=r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
    args = ap.parse_args()

    print("=== 可复现纪律校验 REPRO-GATE-001 ===\n")

    # 1. 图谱完整性
    g = check_graph_integrity(args.db)
    print(f"[1] 图谱完整性: 节点={g['total']} 知识点={g['knowledge_point']} 学科卡={g['subject_card']}")
    g_ok = g["knowledge_point"] >= LOCKED_MIN_KNOWLEDGE_POINTS
    print(f"    → {'✓ 学科卡+知识点子图已合入' if g_ok else '✗ 知识点子图不足'}")

    # 2. 副本一致性
    rep = check_replicas(args.db)
    print(f"[2] 副本一致性: hash={rep['hash']} 各副本一致={'✓' if rep['replicas_match'] else '✗'}")

    if args.quick:
        print("\n（快速模式：未跑测试）")
        return 0 if (g_ok and rep["replicas_match"]) else 1

    # 3. T1 测试（完整或记录模式）
    print("\n[3] T1 知识测试（110 题）…")
    t0 = time.time()
    t = run_t1_test()
    elapsed = time.time() - t0
    print(f"    正确率={t['accuracy']*100:.1f}% ({t['correct']}/{t['total']}) 直接回答率={t['direct_rate']*100:.1f}% ({elapsed:.0f}s)")

    if args.record:
        # 记录当前基准（更新锁定阈值）
        new_min = round(t["accuracy"] - 0.04, 2)
        print(f"\n记录模式：当前正确率 {t['accuracy']*100:.1f}%，锁定下限 {new_min*100:.0f}%")
        # 写基准记录文件
        rec = {"date": time.strftime("%Y-%m-%d"), "accuracy": t["accuracy"],
               "direct_rate": t["direct_rate"], "graph_nodes": g["total"],
               "knowledge_points": g["knowledge_point"], "locked_min_score": new_min,
               "note": "可复现纪律锁定基准（随包图谱 + 当前代码）"}
        out = HERE / "repro_baseline.json"
        out.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"    基准已记录 → {out}")
        return 0

    # 4. 通过判定
    acc_ok = t["accuracy"] >= LOCKED_MIN_SCORE
    direct_ok = t["direct_rate"] >= LOCKED_MIN_DIRECT
    print(f"\n=== 判定 ===")
    print(f"  图谱完整性: {'✓' if g_ok else '✗'}")
    print(f"  副本一致: {'✓' if rep['replicas_match'] else '✗'}")
    print(f"  正确率 ≥{LOCKED_MIN_SCORE*100:.0f}%: {'✓' if acc_ok else '✗'} ({t['accuracy']*100:.1f}%)")
    print(f"  直接回答率 ≥{LOCKED_MIN_DIRECT*100:.0f}%: {'✓' if direct_ok else '✗'} ({t['direct_rate']*100:.1f}%)")
    passed = g_ok and rep["replicas_match"] and acc_ok and direct_ok
    print(f"\n{'✓ 通过——可发布' if passed else '✗ 未通过——禁止发布（先补全图谱/修检索）'}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
