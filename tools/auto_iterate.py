# -*- coding: utf-8 -*-
"""auto_iterate.py · 自动自迭代引擎（荣：长期任务自动运行，协议 §19）

八步闭环自动循环：感知 → 识别 → 固化（可吸收时）→ 记录 → 方向自检
→ 间隔 → 下一轮。稳态检测防空转；崩溃隔离防中断；安全模式默认只感知。

用法：
  python auto_iterate.py --interval 60 --apply        # 自动循环+自动固化
  python auto_iterate.py --max-rounds 3               # 限轮数（安全感知）
  python auto_iterate.py --steady-rounds 5 --apply    # 稳态后退出
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import self_iterate as si

STATE_PATH = os.path.join(HERE, 'auto_iterate_state.json')


def _load_state() -> dict:
    if os.path.exists(STATE_PATH):
        try:
            return json.load(open(STATE_PATH, encoding='utf-8'))
        except Exception:
            return {}
    return {}


def _save_state(state: dict):
    json.dump(state, open(STATE_PATH, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)


def run_one_round(apply: bool) -> dict:
    """执行一轮：感知 → 识别 → （可吸收且 apply）固化 → 记录。"""
    round_no = len(si._load_trace()) + 1
    per = si.perceive()
    cls = si.classify(per["drift"])
    already = si._blindspot_declared()
    new_blindspot = [d for d in cls["blindspot"]
                     if d["unit"] not in already]
    # 固化（隐式盲区且 apply 时——字符串内替换 + 语法校验）
    solid = {"ok": True, "applied": [], "skills": []}
    if new_blindspot and apply:
        solid = si.solidify(new_blindspot)
    # 方向自检
    ori = si.orient(per, solid)
    # 记录
    trace = {
        "round": round_no,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "auto": True,
        "感知": {"n_drift": per["n_drift"],
                "strong_rate": per["strong_rate"],
                "mos_rate": per["mos_rate"],
                "route_excl": per.get("route_conflicts", {}).get("n_excl_units", 0),
                "blindspot": per.get("blindspots", {}).get("n_blindspot", 0),
                "spec_fail": per.get("comment_spec", {}).get("n_spec_fail", 0)},
        "识别": {"blindspot": len(cls["blindspot"]),
                "new_blindspot": len(new_blindspot),
                "manual": len(cls["manual"])},
        "固化": {"n": len(solid.get("applied", [])),
                "items": [{"unit": a["unit"], "cond": a["cond"]}
                          for a in solid.get("applied", [])][:10]},
        "方向性自检": ori,
    }
    si.record(trace)
    return trace


def main():
    ap = argparse.ArgumentParser(description="自动自迭代引擎")
    ap.add_argument("--interval", type=int, default=60, help="轮间隔秒")
    ap.add_argument("--max-rounds", type=int, default=0, help="最大轮数(0=无限)")
    ap.add_argument("--apply", action="store_true", help="允许自动固化")
    ap.add_argument("--steady-rounds", type=int, default=5,
                    help="连续无吸收轮数达此值→报告稳态退出")
    args = ap.parse_args()

    state = _load_state()
    state.setdefault("total_rounds", 0)
    state.setdefault("steady_streak", 0)
    state.setdefault("solidified_total", 0)
    state.setdefault("started_at", time.strftime("%Y-%m-%d %H:%M:%S"))
    _save_state(state)

    print(f"[自动自迭代] 启动 | interval={args.interval}s "
          f"apply={args.apply} steady={args.steady_rounds}轮"
          f"{' | 无限轮' if args.max_rounds == 0 else f' | 限{args.max_rounds}轮'}")
    round_no = 0
    try:
        while args.max_rounds == 0 or round_no < args.max_rounds:
            round_no += 1
            try:
                t = run_one_round(args.apply)
                n_new = t["识别"]["new_blindspot"]
                n_solid = t["固化"]["n"]
                state["total_rounds"] += 1
                state["solidified_total"] += n_solid
                if n_new == 0:
                    state["steady_streak"] += 1
                else:
                    state["steady_streak"] = 0
                _save_state(state)
                print(f"[轮{t['round']}] 漂移{t['感知']['n_drift']} "
                      f"新可吸收{n_new} 固化{n_solid} "
                      f"方向{('✓' if t['方向性自检']['direction_ok'] else '✗')} "
                      f"稳态连击{state['steady_streak']}")
                # 稳态退出
                if state["steady_streak"] >= args.steady_rounds:
                    print(f"[稳态] 连续 {args.steady_rounds} 轮无新吸收——"
                          f"闭环健康，退出（累计固化 {state['solidified_total']} 处）")
                    break
            except Exception as e:
                # 崩溃隔离：单轮失败记录不中断
                print(f"[轮{round_no} 异常] {str(e)[:80]}——本轮跳过")
                state["total_rounds"] += 1
                _save_state(state)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n[停止] 收到中断，保存状态")
    _save_state(state)
    print(f"[结束] 总轮数 {state['total_rounds']} | "
          f"累计固化 {state['solidified_total']} 处 | "
          f"状态 {STATE_PATH}")


if __name__ == "__main__":
    main()
