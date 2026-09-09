#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""先验陷阱测试集 v1 · 可复现 runner（零第三方依赖，仅标准库）。

复现《白箱智能系列·第五篇：让AI真正装上记忆》的 A/B 实证：
同一批题目、同一系统提示，只切换「无记忆 / 有记忆」一个变量。

用法：
    # 云端（任意 OpenAI 兼容端点）
    python run_prior_trap_v1.py --model deepseek-v4.1-flash-expires-on-0910 \
        --base https://api.deepseek.com/v1 --key $DEEPSEEK_API_KEY

    # 本地（LM Studio / Ollama / vLLM 均可）
    python run_prior_trap_v1.py --model smegmma-deluxe-9b-v1 \
        --base http://localhost:1234/v1 --key lm-studio --out results_local.json

说明：
    · mem 臂直接注入 case.lesson（等价于原实验 recall_hit_rate=100% 的情形）。
    · 每例跑 3 种循环排列，使每个候选在 3 个位置各出现一次——按内容选才能 3/3。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor


def chat(base, key, model, messages, timeout, max_tokens, temperature):
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }).encode("utf-8")
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions", data=payload,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {key}"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return (data["choices"][0]["message"].get("content") or "",
            data.get("usage") or {}, time.time() - t0)


def parse_pick(raw, n):
    """从模型输出里抠出候选编号（1..n）；解析失败返回 None。"""
    s = raw or ""
    i, j = s.find("{"), s.rfind("}")
    if i >= 0 and j > i:
        try:
            obj = json.loads(s[i:j + 1])
            p = obj.get("pick")
            if isinstance(p, str) and p.strip().isdigit():
                p = int(p.strip())
            if isinstance(p, (int, float)) and 1 <= int(p) <= n:
                return int(p)
        except ValueError:
            pass
    m = re.search(r"\b([1-9])\b", s)
    if m and 1 <= int(m.group(1)) <= n:
        return int(m.group(1))
    return None


def rotations(base_order):
    return [base_order[i:] + base_order[:i] for i in range(3)]


def user_prompt(case, kinds, memory):
    lines = []
    if memory:
        lines.append("【本项目规范 / 历史经验（来自记忆库，请自行判断相关性）】")
        lines.append(memory.strip())
        lines.append("")
    lines.append("场景：")
    lines.append(case["task"])
    lines.append("")
    lines.append("候选做法：")
    for idx, kind in enumerate(kinds, 1):
        lines.append(f"{idx}. {case['options'][kind]}")
    lines.append("")
    lines.append("请选择最符合本项目规范的做法。")
    return "\n".join(lines)


def run_one(spec, case, kinds, correct_pos, memory, cfg):
    messages = [{"role": "system",
                 "content": spec["protocol"]["system_prompt"]},
                {"role": "user",
                 "content": user_prompt(case, kinds, memory)}]
    raw, usage, dt = chat(cfg["base"], cfg["key"], cfg["model"], messages,
                          cfg["timeout"], cfg["max_tokens"], cfg["temperature"])
    pick = parse_pick(raw, len(kinds))
    kind = "invalid" if pick is None else kinds[pick - 1]
    return {"pick": pick, "kind": kind, "correct": pick == correct_pos,
            "tokens": int(usage.get("total_tokens") or 0),
            "latency": round(dt, 2)}


def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="先验陷阱测试集 v1 · 可复现 runner")
    ap.add_argument("--testset",
                    default=os.path.join(here, "prior_trap_testset_v1.json"))
    ap.add_argument("--model", required=True)
    ap.add_argument("--base", default="https://api.deepseek.com/v1")
    ap.add_argument("--key", default="")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max-tokens", type=int, default=2000)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out", default="", help="结果 JSON 输出路径")
    a = ap.parse_args(argv)

    key = a.key or os.environ.get("DEEPSEEK_API_KEY") or ""
    if not key:
        print("[error] 需要 --key 或环境变量 DEEPSEEK_API_KEY")
        return 2

    with open(a.testset, encoding="utf-8") as f:
        spec = json.load(f)
    cfg = {"model": a.model, "base": a.base, "key": key,
           "timeout": a.timeout, "max_tokens": a.max_tokens,
           "temperature": a.temperature}

    tasks = []
    for case in spec["cases"]:
        for ri, kinds in enumerate(rotations(case["base_order"])):
            correct_pos = kinds.index("fix") + 1
            for arm in ("none", "mem"):
                tasks.append((case, ri, kinds, correct_pos, arm))

    def work(t):
        case, ri, kinds, correct_pos, arm = t
        mem = case["lesson"] if arm == "mem" else None
        try:
            r = run_one(spec, case, kinds, correct_pos, mem, cfg)
        except Exception as exc:                    # noqa: BLE001
            r = {"pick": None, "kind": "error", "correct": False,
                 "tokens": 0, "latency": 0.0,
                 "error": f"{type(exc).__name__}: {exc}"}
        r.update({"case": case["id"], "arm": arm, "rotation": ri})
        print(f"  {case['id']} {arm:<4} rot={ri} -> pick={r['pick']} "
              f"{r['kind']:<7} tok={r['tokens']:>5} ({r['latency']:.1f}s)",
              flush=True)
        return r

    with ThreadPoolExecutor(max_workers=max(1, a.workers)) as ex:
        rows = list(ex.map(work, tasks))

    agg = {}
    for arm in ("none", "mem"):
        rs = [r for r in rows if r["arm"] == arm]
        n = len(rs)
        agg[arm] = {
            "n": n,
            "content_acc": sum(1 for r in rs if r["correct"]) / n,
            "trap_rate": sum(1 for r in rs if r["kind"] == "trap") / n,
            "invalid_rate": sum(1 for r in rs
                                if r["kind"] in ("invalid", "error")) / n,
            "avg_tokens": sum(r["tokens"] for r in rs) / n,
            "avg_latency_s": sum(r["latency"] for r in rs) / n,
            "recall_hit_rate": 1.0 if arm == "mem" else None,
            "pos_dist": [sum(1 for r in rs if r["pick"] == p)
                         for p in (1, 2, 3)],
        }

    def pct(x):
        return f"{100.0 * x:.1f}%"

    print("\n" + "-" * 70)
    print(f"模型：{a.model}   样本 {agg['none']['n']} 次/臂（用例 × 排列）")
    print(f"{'指标':<16}{'arm_none':>14}{'arm_mem':>14}")
    print("-" * 70)
    print(f"{'content_acc':<16}{pct(agg['none']['content_acc']):>14}"
          f"{pct(agg['mem']['content_acc']):>14}")
    print(f"{'trap_rate':<16}{pct(agg['none']['trap_rate']):>14}"
          f"{pct(agg['mem']['trap_rate']):>14}")
    print(f"{'invalid_rate':<16}{pct(agg['none']['invalid_rate']):>14}"
          f"{pct(agg['mem']['invalid_rate']):>14}")
    print(f"{'avg_tokens':<16}{agg['none']['avg_tokens']:>14.1f}"
          f"{agg['mem']['avg_tokens']:>14.1f}")
    print(f"{'avg_latency_s':<16}{agg['none']['avg_latency_s']:>14.2f}"
          f"{agg['mem']['avg_latency_s']:>14.2f}")
    print(f"{'pos_dist':<16}"
          f"{'/'.join(map(str, agg['none']['pos_dist'])):>14}"
          f"{'/'.join(map(str, agg['mem']['pos_dist'])):>14}")

    print("\n逐用例 content_acc（按内容选对次数 / 该例排列数）：")
    for case in spec["cases"]:
        an = [r for r in rows
              if r["case"] == case["id"] and r["arm"] == "none"]
        am = [r for r in rows
              if r["case"] == case["id"] and r["arm"] == "mem"]
        print(f"  {case['id']}  none {sum(r['correct'] for r in an)}/{len(an)}"
              f"   mem {sum(r['correct'] for r in am)}/{len(am)}"
              f"   {case['task'][:36]}")

    if a.out:
        out = {"testset": spec["name"], "model": a.model,
               "date": time.strftime("%Y-%m-%d"),
               "temperature": a.temperature, "max_tokens": a.max_tokens,
               "metrics": agg, "rows": rows}
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"\n已写出：{a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
