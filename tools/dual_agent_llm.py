# -*- coding: utf-8 -*-
"""dual_agent_llm.py · 双智能体 LLM 通道接入（2026-08-29 心跳）

双智能体架构（dual_agent.py）接真实 LLM：反思=GLM-5.3-flash 出候选，
验证=物理基底实跑（Python 真执行比对——非 LLM 自评，独立纪律强化）。

这是「双智能体最小活体」的真实认知分工形态：反思通道产码，物理基底裁决。
演示任务：实现 insert_end(lst, x)——把 x 追加到列表副本末尾并返回。
"""
import sys, os, json, tempfile, subprocess
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dual_agent import (FixedRecord, FixedOutput, ReflectAgent,
                        VerifyAgent, DualAgentSystem)

# ---- 反思通道：GLM-5.3-flash 出代码 ----
def glm_implement(task, attempt, failing):
    key = os.environ.get("BIGMODEL_API_KEY", "")
    if not key:
        return None   # 无 key → 反思通道不可用（调用方降级）
    import urllib.request, re
    prompt = (f"实现 Python 函数：{task['desc']}\n"
              f"只输出一个代码块。函数签名：def insert_end(lst, x)")
    if failing:
        prompt += f"\n上次未通过验证：{failing}\n请修正。"
    body = json.dumps({"model": "glm-5.3-flash", "temperature": 0,
                       "max_tokens": 8192,   # 思考常开：须覆盖 reasoning 链（防 content 被截为空）
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions", data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {key}"})
    import time as _t
    last_err = None
    for retry in range(3):   # 网络瞬时波动重试（SSL/read timeout）
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                text = json.loads(resp.read())["choices"][0]["message"]["content"]
            last_err = None
            break
        except Exception as e:
            last_err = e
            _t.sleep(5 * (retry + 1))
    if last_err is not None:
        raise last_err
    m = re.search(r"```(?:python)?\s*(.+?)```", text, re.S)
    return (m.group(1) if m else text).strip()

# ---- 验证基底：Python 真实执行比对（物理裁决，非 LLM 自评）----
TESTS = [
    (([1, 2], 3), [1, 2, 3]),
    (([], 9), [9]),
    (([0], 0), [0, 0]),
]

def make_physical_judge(task):
    def judge(code):
        if code is None:
            return False, "反思通道未产出候选"
        td = tempfile.mkdtemp(prefix="da_llm_")
        # 每次裁决同目录写 impl+probe（-I 隔离模式不认 cwd 之外的 sys.path，
        # 但认脚本所在目录——impl.py 与 probe.py 必须同目录）
        with open(os.path.join(td, "impl.py"), "w", encoding="utf-8") as f:
            f.write(code)
        checks = []
        for (args, want) in TESTS:
            probe = ("import sys, os; "
                     "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"
                     f"import impl\nr = impl.insert_end({list(args[0])}, {args[1]})\n"
                     f"assert r == {want}, f'{{r}} != {want}'\n"
                     f"assert {list(args[0])} == {list(args[0])}, '原列表被修改'\n")
            with open(os.path.join(td, "probe.py"), "w", encoding="utf-8") as f:
                f.write(probe)
            probe = os.path.join(td, "probe.py")
            rr = subprocess.run([sys.executable, "-I", probe],
                                capture_output=True, text=True,
                                encoding="utf-8", timeout=10)
            if rr.returncode != 0:
                return False, f"case {args} 失败: {(rr.stderr or '')[-120:]}"
            checks.append(f"{args}->{want}")
        return True, "物理裁决 " + "; ".join(checks)
    return judge

if __name__ == "__main__":
    td = tempfile.mkdtemp(prefix="da_llm_run_")
    record = FixedRecord(os.path.join(td, "record.jsonl"))
    output = FixedOutput(os.path.join(td, "output.jsonl"))
    task = {"desc": "实现 insert_end(lst, x)：把 x 追加到列表的**副本**末尾并返回新列表"
                    "（不得修改原列表）。示例：insert_end([1,2], 3) == [1,2,3]",
            "arr": None}
    system = DualAgentSystem(
        ReflectAgent(glm_implement),
        VerifyAgent(make_physical_judge(task)),
        record, output, max_attempts=3)
    r = system.execute("insert-end-impl", task)
    print(json.dumps(r, ensure_ascii=False)[:300])
    sys.exit(0 if r["status"] == "accepted" else 1)
