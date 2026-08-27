# -*- coding: utf-8 -*-
"""test_glm_flash.py · GLM-5.3-Flash 白箱编码效果测试

目的：量化 GLM-5.3-Flash 在白箱自举编程任务上的真实效果——
「生成 → 白箱校验器（verifier）校验」闭环的通过率。

用法：
  # 用智谱开放平台 key（openai 兼容端点）
  python test_glm_flash.py --api-key sk-xxx --base-url https://open.bigmodel.cn/api/paas/v4 \
      --model glm-4.6-flash
  # 用 Z.ai anthropic 兼容端点
  python test_glm_flash.py --api-key xxx.yyy --base-url https://api.z.ai/api/anthropic \
      --model glm-5.3-flash --anthropic

输出：每个任务的 通过层（L1语法/L2样例/L3边界）、耗时、一次通过率。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "aeis"))

from verifier import VerifyRequest, Verifier  # noqa: E402

# 代表性任务：六域 Python 单元里挑 6 个（算法域 + 不同 pattern）
TASK_IDS = ["排序-冒泡", "去重-保序", "计数-频率", "最大", "最大公约数", "斐波那契"]

SYSTEM_PROMPT = (
    "你是一名白箱代码生成器。输出**纯 Python 函数实现**，遵守：\n"
    "1. 只输出代码（含 def 签名），不要解释、不要 markdown 代码块围栏\n"
    "2. 纯函数：无 I/O、无副作用、不依赖全局状态\n"
    "3. 只用标准库（collections/typing/math 等）\n"
    "4. 函数签名与要求完全一致\n"
    "5. 正确处理边界（空输入、单元素、重复元素）\n"
)


def build_prompt(unit: dict) -> str:
    """从白箱单元构建生成 prompt（任务 + 输入输出规范）。"""
    task = unit["task"]
    pattern = unit.get("pattern", "?")
    cases = unit.get("cases", [])
    # 从 cases 推导签名：取第一条输入结构
    sig_hint = ""
    if cases:
        first = cases[0]
        # cases 结构可能是 {"input": [...], "expected": ...} 或 (input, expected)
        if isinstance(first, dict) and "input" in first:
            inp = first["input"]
            sig_hint = f"输入参数：{json.dumps(inp, ensure_ascii=False)[:80]}；期望输出：{json.dumps(first.get('expected'), ensure_ascii=False)[:60]}"
    prompt = (
        f"任务：实现「{task}」（pattern: {pattern}）。\n"
        f"{sig_hint}\n"
        f"请给出函数定义。要求：输入输出类型与上面样例一致（列表→列表、数字→数字等），"
        f"函数名自拟但语义清晰。"
    )
    return prompt


def call_llm(api_key: str, base_url: str, model: str, anthropic: bool, prompt: str) -> str:
    """调 LLM 生成代码（支持 anthropic / openai 两种兼容端点）。"""
    if anthropic:
        url = base_url.rstrip("/") + "/v1/messages"
        payload = {
            "model": model,
            "max_tokens": 800,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        }
    else:
        url = base_url.rstrip("/") + "/chat/completions"
        payload = {
            "model": model,
            "max_tokens": 800,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        }
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read())
    if anthropic:
        return "".join(c.get("text", "") for c in body.get("content", []))
    return body["choices"][0]["message"]["content"]


def strip_code(text: str) -> str:
    """去掉 markdown 围栏，只留代码。"""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-key", required=True)
    ap.add_argument("--base-url", default="https://open.bigmodel.cn/api/paas/v4")
    ap.add_argument("--model", default="glm-4.6-flash")
    ap.add_argument("--anthropic", action="store_true")
    ap.add_argument("--tasks", default=",".join(TASK_IDS))
    ap.add_argument("--trials", type=int, default=2, help="每任务重复次数（测稳定性）")
    args = ap.parse_args()

    from wisdom.code_compose import CODE_UNITS  # noqa: E402

    task_ids = [t.strip() for t in args.tasks.split(",") if t.strip()]
    verifier = Verifier()
    results = []

    for tid in task_ids:
        unit = CODE_UNITS.get(tid)
        if unit is None:
            print(f"⚠️ 跳过未知任务: {tid}")
            continue
        for trial in range(args.trials):
            prompt = build_prompt(unit)
            t0 = time.time()
            try:
                raw = call_llm(args.api_key, args.base_url, args.model, args.anthropic, prompt)
                code = strip_code(raw)
            except urllib.error.HTTPError as e:
                print(f"❌ [{tid} t{trial}] API 错误 {e.code}: {e.read().decode()[:200]}")
                results.append({"task": tid, "trial": trial, "pass": False, "reason": f"api {e.code}"})
                continue
            except Exception as e:  # noqa: BLE001
                print(f"❌ [{tid} t{trial}] 异常: {e}")
                results.append({"task": tid, "trial": trial, "pass": False, "reason": str(e)})
                continue
            dt = time.time() - t0
            # 白箱校验：L1 语法 + L2 样例 + L3 边界
            req = VerifyRequest(
                unit_id=tid,
                source_code=code,
                cases=unit.get("cases", []),
                expected_structure={"task": unit["task"], "pattern": unit.get("pattern")},
            )
            res = verifier.verify(req)
            passed = res.ok and res.layer_reached >= 3
            results.append({"task": tid, "trial": trial, "pass": passed,
                            "layer": getattr(res, "layer_reached", 0),
                            "detail": getattr(res, "detail", "")[:100], "secs": round(dt, 1)})
            print(f"{'✅' if passed else '❌'} [{tid} t{trial}] 层{getattr(res,'layer_reached','?')} "
                  f"{round(dt,1)}s {getattr(res,'detail','')[:60]}")

    print("\n===== 汇总 =====")
    n = len(results)
    ok = sum(1 for r in results if r["pass"])
    print(f"总执行: {n} | 通过: {ok} ({ok/max(n,1)*100:.0f}%)")
    by_task: dict[str, list] = {}
    for r in results:
        by_task.setdefault(r["task"], []).append(r)
    for tid, rs in by_task.items():
        t_ok = sum(1 for r in rs if r["pass"])
        print(f"  {tid}: {t_ok}/{len(rs)} 通过")


if __name__ == "__main__":
    main()
