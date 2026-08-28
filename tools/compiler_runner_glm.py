# -*- coding: utf-8 -*-
"""compiler_runner_glm.py · T9-2b GLM 端 runner（与 deepseek 端交叉验证）

同源纪律：任务/片段清单/语法骨架/路由指令/验收器直接 import dsh 端
compiler_runner2（单一来源——清单变更自动同步，杜绝两端漂移）。
仅替换：模型通道（glm-5.3-flash / BIGMODEL_API_KEY）。
统计口径与 dsh 端一致：prompt / visible（completion−reasoning）/ reasoning 分列。
"""
import os
import sys
import io
import json
import time
import urllib.request


def setup_stdout():
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass


setup_stdout()

DSH_TOKEN_TEST = r"D:\Program Files\2_ai\dsh-memory\llm-adapter-poc\token_test"
sys.path.insert(0, DSH_TOKEN_TEST)

# 同源导入：任务清单/骨架/路由/白箱检索/验收器（单一来源，防两端漂移）
from compiler_runner2 import (  # noqa: E402
    TASKS, SKELETON, ROUTING, whitebox_units, verify_program, extract_program,
)

# ---------- GLM 通道 ----------
BASE = "https://open.bigmodel.cn/api/paas/v4"
MODEL = "glm-5.3-flash"


def get_key():
    return os.environ.get("BIGMODEL_API_KEY", "")


KEY = get_key()


def llm_chat(messages, max_tokens=10000, retries=2):
    body = json.dumps({
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
    }).encode()
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(f"{BASE}/chat/completions",
                data=body, headers={"Authorization": f"Bearer {KEY}",
                                    "Content-Type": "application/json"})
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode())
            dt = time.time() - t0
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return content, usage, dt
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"LLM 调用失败（{retries} 次）: {last_err}")


# ---------- 单任务（逻辑与 dsh 端 run_task 同构，仅通道不同） ----------
def run_task(task, with_lingshu, max_rounds=5):
    history = {"prompt": 0, "completion": 0, "reasoning": 0, "visible": 0,
               "total": 0, "rounds": 0}
    rounds_log = []

    def noise_block(round_idx):
        n = task["doc_noise"]
        half = len(n) // 2
        return "\n".join(n[:half] if round_idx == 0 else n[half:])

    if with_lingshu:
        wb = whitebox_units(task["whitebox_units"])
        system = ROUTING + ("\n\n" + wb if wb else "")
        info_r0 = noise_block(0)
        user0 = (f"任务：{task['task']}\n{SKELETON}\n"
                 f"{info_r0}\n请输出完整的中文协议程序。")
    else:
        system = "你是一个中文协议语言编译器工程师，严格按任务要求输出程序。"
        doc = "\n".join(task["doc_ok"] + task["doc_noise"])
        user0 = (f"任务：{task['task']}\n{SKELETON}\n{doc}\n"
                 f"请基于以上领域文档输出完整的中文协议程序（文档可能含过时/错误信息，请自行辨别）。")

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user0},
    ]

    for rnd in range(max_rounds):
        content, usage, dt = llm_chat(messages)
        prompt_t = usage.get("prompt_tokens", 0)
        comp_t = usage.get("completion_tokens", 0)
        detail = usage.get("completion_tokens_details", {}) or {}
        reason_t = detail.get("reasoning_tokens", 0) or 0
        visible_t = max(0, comp_t - reason_t)
        history["prompt"] += prompt_t
        history["completion"] += comp_t
        history["reasoning"] += reason_t
        history["visible"] += visible_t
        history["total"] += usage.get("total_tokens", 0)
        history["rounds"] += 1

        prog = extract_program(content)
        ok, cat, detail = verify_program(prog, task["expected"])
        rounds_log.append({
            "round": rnd + 1, "prompt": prompt_t, "comp": comp_t,
            "reasoning": reason_t, "visible": visible_t,
            "status": cat, "detail": detail, "program": prog,
        })
        print(f"      R{rnd + 1}: {cat} {detail[:60]} "
              f"(p={prompt_t} v={visible_t} r={reason_t})")
        if ok:
            return {"pass": True, "rounds": rnd + 1, **history,
                    "rounds_log": rounds_log, "program": prog}

        feedback = f"验收未通过（{cat}）：{detail}\n期望「结果」== {task['expected']}。"
        if rnd + 1 < len(task["doc_noise"]):
            feedback += f"\n\n【新收到的项目信息】\n{noise_block(rnd + 1)}"
        feedback += "\n请修正程序，输出完整的中文协议程序。"
        messages.append({"role": "assistant", "content": content})
        messages.append({"role": "user", "content": feedback})

    return {"pass": False, "rounds": max_rounds, **history,
            "rounds_log": rounds_log, "program": prog}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "both"
    task_filter = sys.argv[2].split(",") if len(sys.argv) > 2 else None
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "compiler_token_results_glm.json")
    # 续跑：已有结果加载（补跑不丢已完成组）
    results = {"裸LLM": [], "灵枢+白箱": [], "engine": MODEL}
    if os.path.exists(out):
        try:
            prev = json.load(open(out, encoding="utf-8"))
            results["裸LLM"] = prev.get("裸LLM", [])
            results["灵枢+白箱"] = prev.get("灵枢+白箱", [])
        except Exception:
            pass

    for t in TASKS:
        if task_filter and t["id"] not in task_filter:
            continue
        print(f"\n===== 任务{t['id']} {t['name']}（{t['complexity']}·期望 {t['expected']}） =====")
        for label, flag, key in [("裸LLM", False, "裸LLM"),
                                 ("灵枢+白箱", True, "灵枢+白箱")]:
            if (mode == "bare" and flag) or (mode == "lingshu" and not flag):
                continue
            # 续跑幂等：同任务同组已有通过记录则跳过
            if any(r.get("task") == t["id"] and r.get("pass") for r in results[key]):
                print(f"  [{label}] 任务{t['id']} 已有通过记录，跳过")
                continue
            try:
                r = run_task(t, flag)
            except Exception as e:
                print(f"  [{label}] run_task 异常: {e}", file=sys.stderr)
                continue
            # 覆盖同任务同组旧的非通过记录（补跑结果替换）
            results[key] = [r0 for r0 in results[key]
                            if not (r0.get("task") == t["id"] and not r0.get("pass"))]
            results[key].append({**r, "task": t["id"], "name": t["name"],
                                 "complexity": t["complexity"],
                                 "expected": t["expected"]})
            json.dump(results, open(out, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)  # 每任务落盘（防卡死丢进度）
            print(f"  [{label}] pass={r['pass']} rounds={r['rounds']} "
                  f"prompt={r['prompt']} visible={r['visible']} "
                  f"reasoning={r['reasoning']} total={r['total']}")

    print("\n\n========== 汇总（GLM 端） ==========")
    for label in ["裸LLM", "灵枢+白箱"]:
        rs = results[label]
        if not rs:
            continue
        prompt = sum(r["prompt"] for r in rs)
        visible = sum(r["visible"] for r in rs)
        reasoning = sum(r["reasoning"] for r in rs)
        rounds = sum(r["rounds"] for r in rs)
        pass_n = sum(1 for r in rs if r["pass"])
        print(f"\n{label}: 输入token={prompt} 可见输出={visible} "
              f"(推理={reasoning}) 总轮次={rounds} 通过={pass_n}/3")

    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print(f"\n结果已保存: {out}")


if __name__ == "__main__":
    main()
