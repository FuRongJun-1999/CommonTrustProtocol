# -*- coding: utf-8 -*-
"""dual_agent_llm_nodes.py · 双智能体蜂群化 × LLM 通道（完整组合，2026-08-29）

反思节点接 GLM-5.3-flash 出码（真实认知），验证节点物理裁决（独立基底），
两节点经总线闭环——多智能体协作的完整形态：
真实 LLM 认知 + 蜂群分布式 + 物理裁决三合一。
"""
import sys, os, json, tempfile
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "aeis"))
from dual_agent_nodes import run_dual_node_session
from dual_agent_llm import glm_implement, make_physical_judge

if __name__ == "__main__":
    task = {"desc": "实现 remove_dup(lst)：去除列表重复元素，保持首次出现顺序，返回新列表。"
                    "示例：remove_dup([1,2,1,3]) == [1,2,3]"}
    judge = make_physical_judge(task)
    r = run_dual_node_session(
        os.path.join(tempfile.gettempdir(), "dal_nodes"),
        task,
        propose=lambda t, rnd, fail: glm_implement(t, rnd, fail),
        judge=judge, max_rounds=3)
    print("组合形态:", json.dumps(r, ensure_ascii=False)[:280])
    print("双智能体蜂群化×LLM:", "PASS ✅" if r["status"] == "accepted" else "FAIL")
    sys.exit(0 if r["status"] == "accepted" else 1)
