# -*- coding: utf-8 -*-
"""m23_demo.py · M2.3 端到端 demo：查卡 → 实现 → code_test 物理裁决

代码图架构战略行动项 2 收口（M2.1 定案 + M2.2 工具后的闭环验证）：
1. card_route 白箱查卡（0 LLM token）→ declaration 注入
2. LLM 实现一次（glm-5.3-flash）
3. code_test 物理裁决（与 MCP 工具同源分支逻辑）
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "aeis"))  # 包根最优先（防 site-packages 旧拷贝缓存）
sys.path.insert(1, os.path.join(ROOT, "aeis", "wisdom"))
sys.stdout.reconfigure(encoding="utf-8")

TASK = ("实现函数 insertion_sort(arr)，返回升序排列的新列表（不修改原列表，"
        "逐个取元素插入前方已有序区间的正确位置）。")
TESTS = [
    "a=[3,1,2]; assert ns['insertion_sort'](a)==[1,2,3] and a==[3,1,2]",
    "assert ns['insertion_sort']([])==[]",
    "assert ns['insertion_sort']([2,2,1])==[1,2,2]",
    "assert ns['insertion_sort']([5])==[5]",
]

# ---- 1. 白箱查卡（0 LLM token）----
from wisdom_book import ConditionDex
from semantic_translate import card_route

dex = ConditionDex(db_path=os.path.join(ROOT, "aeis", "wisdom", "wisdom-book-cloud.db"),
                   fresh=False)
cards = []
for h in card_route(dex, "插入排序", limit=1):
    if h.get("_card_hit"):
        node = dex.store.get_node(h.get("id"))
        cm = (node.state_attributes or {}).get("comment", {}) if node else {}
        cards.append(f"- 卡「{h.get('name')}」生效条件 {cm.get('生效条件', [])}；"
                     f"不适用条件 {cm.get('不适用条件', [])}")
print("[1] 白箱查卡:", cards or "未命中（0 LLM token 消耗）")

# ---- 2. LLM 实现（1 次调用）----
key = os.environ.get("BIGMODEL_API_KEY", "")
impl_code = None
if key:
    import urllib.request
    body = json.dumps({
        "model": "glm-5.3-flash", "temperature": 0, "max_tokens": 2000,
        "messages": [{"role": "user", "content":
                      f"实现以下任务，只输出一个 Python 代码块：\n{TASK}\n\n"
                      + ("知识库条件空间声明（边界参考）：\n" + "\n".join(cards)
                         if cards else "")}]}).encode()
    req = urllib.request.Request(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions", data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        text = json.loads(resp.read())["choices"][0]["message"]["content"]
    import re
    m = re.search(r"```(?:python)?\s*(.+?)```", text, re.S)
    impl_code = (m.group(1) if m else text).strip()
    print("[2] LLM 实现完成（1 次调用）")
else:
    print("[2] 无 BIGMODEL_API_KEY——用已知正确实现演示裁决链路")
    impl_code = ("def insertion_sort(a):\n    out = list(a)\n"
                 "    for i in range(1, len(out)):\n"
                 "        k = out[i]; j = i - 1\n"
                 "        while j >= 0 and out[j] > k:\n"
                 "            out[j+1] = out[j]; j -= 1\n"
                 "        out[j+1] = k\n    return out")

# ---- 3. code_test 物理裁决（与 MCP 工具同源分支）----
from aeis.mcp.server import _CODE_TEST_RUNNER
td = tempfile.mkdtemp()
with open(os.path.join(td, "impl.py"), "w", encoding="utf-8") as f:
    f.write(impl_code)
with open(os.path.join(td, "tests.json"), "w", encoding="utf-8") as f:
    json.dump(TESTS, f, ensure_ascii=False)
with open(os.path.join(td, "runner.py"), "w", encoding="utf-8") as f:
    f.write(_CODE_TEST_RUNNER)
r = subprocess.run([sys.executable, "-I", os.path.join(td, "runner.py")],
                   cwd=td, capture_output=True, text=True,
                   encoding="utf-8", timeout=15)
payload = json.loads(r.stdout)
print("[3] code_test 物理裁决:")
for x in payload["results"]:
    print("   ", "[✔]" if x["ok"] else "[✘]", str(x["test"])[:55], x["error"] or "")
passed = all(x["ok"] for x in payload["results"])
print("\n=== 端到端判定 ===")
print("查卡(0 tok) → 实现(1 LLM) → 物理裁决:", "PASS ✅" if passed else "FAIL ❌")
sys.exit(0 if passed else 1)
