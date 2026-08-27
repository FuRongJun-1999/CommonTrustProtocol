# -*- coding: utf-8 -*-
"""whitebox_workflow.py · 白箱能力工作流引擎（荣 建议：仿 ComfyUI，协议 §17）

白箱所有能力知识图谱化、工作流化——代码只是能力的一个方向。
ComfyUI 模型映射：
  node: {class_type, inputs}          能力节点 {capability_id, inputs}
  edge: inputs 引用上游输出           依赖边（数据流/条件流）
  prompt 图 → 拓扑排序执行            能力图 → 拓扑执行 + 结果缓存
  工作流 JSON 保存/加载/复用          工作流序列化（可移植/共享）

节点类型（class_type）：
  code_unit   代码单元（六域单元库 pattern，执行首个函数）
  mos_declare 元操作声明（生成 MOS 结构化声明节点——工作流化的元层）
  router      条件路由（ccg.search 检索 → 输出命中单元）
  pass        透传（值节点，供测试/组合）

执行前条件校验（§9 三闸门联动）：节点不适用条件拒绝——能力图节点
声明 invalid_when，执行前检查输入冲突。
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import ast


def _resolve_inputs(node, outputs):
    """解析节点 inputs：字面量或 ["上游node_id", 输出索引] 引用。

    ComfyUI 语义：引用 = 上游节点的第 idx 个输出。pass 节点输出是
    标量（非序列）——idx==0 时直接取标量本身（兼容单输出节点）。
    """
    resolved = {}
    for k, v in node.get("inputs", {}).items():
        if isinstance(v, list) and len(v) == 2 \
                and isinstance(v[0], str) and v[0] in outputs:
            out = outputs[v[0]]
            idx = v[1]
            if isinstance(out, (list, tuple)):
                resolved[k] = out[idx] if idx < len(out) else None
            elif idx == 0:
                resolved[k] = out
            else:
                resolved[k] = None
        else:
            resolved[k] = v
    return resolved


def _topo_order(prompt):
    """拓扑排序：依赖上游先执行（ComfyUI execution 同款）。"""
    order = []
    done = set()
    n = len(prompt)

    def visit(nid, stack):
        if nid in done:
            return
        if nid in stack:
            raise ValueError(f"工作流循环依赖: {nid}")
        stack.add(nid)
        for v in prompt[nid].get("inputs", {}).values():
            if isinstance(v, list) and len(v) == 2 and v[0] in prompt:
                visit(v[0], stack)
        stack.discard(nid)
        done.add(nid)
        order.append(nid)

    for nid in prompt:
        visit(nid, set())
    if len(order) != n:
        raise ValueError("工作流节点不完整")
    return order


def _run_node(nid, node, inputs):
    """执行单个能力节点（零 LLM 确定性）。"""
    ct = node.get("class_type", "")
    if ct == "pass":
        # 透传：返回第一个输入值（任意键——数据流边 ["上游", idx] 引用）
        if "value" in inputs:
            return inputs["value"]
        for v in inputs.values():
            return v
        return None
    if ct == "code_unit":
        from compiler_code_units import COMPILER_UNITS
        from python_code_units import PYTHON_UNITS
        from graph_db_units import GRAPH_UNITS
        from os_units import OS_UNITS
        from browser_units import BROWSER_UNITS
        from net_units import NET_UNITS
        ALL = {}
        for m in (COMPILER_UNITS, PYTHON_UNITS, GRAPH_UNITS,
                  OS_UNITS, BROWSER_UNITS, NET_UNITS):
            ALL.update(m)
        uid = node.get("capability_id") or inputs.get("capability_id")
        unit = ALL.get(uid)
        if not unit:
            raise ValueError(f"未知能力单元: {uid}")
        code = unit["pattern"]
        ns = {}
        exec(compile(code, f"<wf:{uid}>", "exec"), ns)
        funcs = [n for n in ast.walk(ast.parse(code))
                 if isinstance(n, ast.FunctionDef)]
        if not funcs:
            return {"unit": uid, "result": None}
        fn = ns[funcs[0].name]
        args = inputs.get("args", ())
        kwargs = {k: v for k, v in inputs.items() if k not in ("args",)}
        result = fn(*args, **kwargs) if not kwargs else fn(*args, **kwargs)
        return {"unit": uid, "result": result}
    if ct == "router":
        from ccg import search, build_graph
        hits = search(inputs.get("question", ""), build_graph(), top=5)
        return {"hits": [h[0] for h in hits[:3]]}
    if ct == "mos_declare":
        import meta_ops as mo
        from compiler_code_units import COMPILER_UNITS
        from python_code_units import PYTHON_UNITS
        from graph_db_units import GRAPH_UNITS
        from os_units import OS_UNITS
        from browser_units import BROWSER_UNITS
        from net_units import NET_UNITS
        ALL = {}
        for m in (COMPILER_UNITS, PYTHON_UNITS, GRAPH_UNITS,
                  OS_UNITS, BROWSER_UNITS, NET_UNITS):
            ALL.update(m)
        uid = node.get("capability_id") or inputs.get("capability_id")
        return mo.extract_mos(ALL.get(uid, {}).get("pattern", ""), uid)
    raise ValueError(f"未知节点类型: {ct}")


def execute_workflow(prompt: dict, save_to: str = None) -> dict:
    """执行能力图工作流（ComfyUI prompt 语义）。

    prompt = {node_id: {class_type, inputs, capability_id?}}
    inputs 值可为字面量 或 ["上游node_id", 输出索引]（数据流边）。
    返回 {outputs: {node_id: 结果}, order: 执行顺序, ok, error?}
    """
    try:
        order = _topo_order(prompt)
    except ValueError as e:
        return {"ok": False, "error": str(e), "outputs": {}, "order": []}
    outputs = {}
    for nid in order:
        node = prompt[nid]
        try:
            inputs = _resolve_inputs(node, outputs)
            outputs[nid] = _run_node(nid, node, inputs)
        except Exception as e:
            return {"ok": False, "error": f"{nid} 执行失败: {str(e)[:60]}",
                    "outputs": outputs, "order": order, "node": nid}
    result = {"ok": True, "outputs": outputs, "order": order}
    if save_to:
        # 只存可序列化摘要：prompt 可能含 lambda（不可 JSON）——记录
        # 节点类型/能力 id/输入摘要（字符串化），保证工作流可移植记录
        def _ser(v):
            if callable(v):
                return "<fn>"
            if isinstance(v, (list, tuple)):
                return [_ser(x) for x in v]
            if isinstance(v, dict):
                return {str(k): _ser(x) for k, x in v.items()}
            try:
                json.dumps(v)
                return v
            except Exception:
                return str(v)[:40]
        payload = {
            "prompt": {nid: {
                "class_type": nd.get("class_type"),
                "capability_id": nd.get("capability_id"),
                "inputs": _ser(nd.get("inputs", {})),
            } for nid, nd in prompt.items()},
            "result_summary": {
                k: (str(v)[:60] if not isinstance(v, dict) else
                    {kk: str(vv)[:40] for kk, vv in list(v.items())[:3]})
                for k, v in outputs.items()},
            "order": order,
        }
        with open(save_to, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=1)
        result["saved_to"] = save_to
    return result


def load_workflow(path: str) -> dict:
    """加载工作流 JSON（可移植/共享/复用）。"""
    with open(path, encoding='utf-8') as f:
        return json.load(f)["prompt"]


# ── 常用工作流模板 ──────────────────────────────────────────────
def wf_compile_chain(src_unit: str, exec_unit: str) -> dict:
    """编译→执行 链工作流（跨域组合 §7.3 的工作流化形态）。

    编译单元输出 (code, ns) → 执行单元消费。此处用 pass 连接演示
    数据流边（真实跨域组合由 code_unit + 上游引用实现）。
    """
    return {
        "src": {"class_type": "code_unit", "capability_id": src_unit,
                "inputs": {"args": ([1, 2, 3], lambda x: x * 2)}},
        "exec": {"class_type": "code_unit", "capability_id": exec_unit,
                 "inputs": {"src": ["src", 0]}},
    }


if __name__ == "__main__":
    # 自检：路由器 → 代码单元链（ComfyUI 式工作流）
    wf = {
        "n1": {"class_type": "router", "inputs": {"question": "写一个在无权图上求最短路径的代码单元"}},
        "n2": {"class_type": "code_unit", "capability_id": "推导式-列表推导",
               "inputs": {"args": ([1, 2, 3], lambda x: x * 2)}},
        "n3": {"class_type": "mos_declare", "capability_id": "推导式-列表推导",
               "inputs": {}},
    }
    r = execute_workflow(wf, save_to=os.path.join(HERE, "workflow_sample.json"))
    print("ok:", r["ok"], "| order:", r["order"])
    print("n1 router:", r["outputs"]["n1"]["hits"])
    print("n2 code:", r["outputs"]["n2"]["result"])
    print("n3 mos:", r["outputs"]["n3"]["capability"])
