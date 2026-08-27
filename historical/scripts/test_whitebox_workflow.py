# -*- coding: utf-8 -*-
"""test_whitebox_workflow.py · 白箱能力工作流化（荣 建议：仿 ComfyUI，§17）

ComfyUI 模型：node{class_type, inputs} + 边（inputs 引用上游）+ prompt 图
→ 拓扑执行 → 缓存/复用 → 工作流 JSON 保存/加载。
验证：①拓扑执行 ②数据流边（上游引用）③循环依赖检测 ④JSON 保存/加载
⑤跨域链工作流（§7.3 的工作流化形态）。
"""
import sys, os, json
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import whitebox_workflow as wf

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

HERE = os.path.dirname(os.path.abspath(__file__))

# ── ① 拓扑执行：router → code_unit → mos_declare ─────────────
wf1 = {
    "n1": {"class_type": "router",
           "inputs": {"question": "写一个在无权图上求最短路径的代码单元"}},
    "n2": {"class_type": "code_unit", "capability_id": "推导式-列表推导",
           "inputs": {"args": ([1, 2, 3], lambda x: x * 2)}},
    "n3": {"class_type": "mos_declare", "capability_id": "推导式-列表推导",
           "inputs": {}},
}
r1 = wf.execute_workflow(wf1)
ok1 = (r1["ok"] and r1["order"] == ["n1", "n2", "n3"]
       and r1["outputs"]["n1"]["hits"]
       and r1["outputs"]["n2"]["result"] == [2, 4, 6]
       and r1["outputs"]["n3"]["capability"] == "推导式-列表推导")
print(f'  拓扑序 {r1["order"]} | n1 命中 {r1["outputs"]["n1"]["hits"][:2]} '
      f'| n2 {r1["outputs"]["n2"]["result"]}')
check('① 拓扑执行：router→code_unit→mos_declare 三节点', ok1)

# ── ② 数据流边（上游引用 ["node", idx]）────────────────────
wf2 = {
    "a": {"class_type": "pass", "inputs": {"value": 5}},
    "b": {"class_type": "pass", "inputs": {"x": ["a", 0]}},  # b 引用 a 输出
}
r2 = wf.execute_workflow(wf2)
ok2 = (r2["ok"] and r2["order"] == ["a", "b"]
       and r2["outputs"]["b"] == 5)
print(f'  边引用: b 收到 a 输出 = {r2["outputs"]["b"]}（应为 5）')
check('② 数据流边：inputs 引用上游输出（拓扑依赖）', ok2)

# ── ③ 循环依赖检测 ───────────────────────────────────────────
wf3 = {
    "a": {"class_type": "pass", "inputs": {"v": ["b", 0]}},
    "b": {"class_type": "pass", "inputs": {"v": ["a", 0]}},
}
r3 = wf.execute_workflow(wf3)
ok3 = not r3["ok"] and "循环" in r3.get("error", "")
print(f'  循环依赖 → {r3.get("error","")[:30]}')
check('③ 循环依赖检测：报错不执行（ComfyUI 同款保护）', ok3)

# ── ④ 工作流 JSON 保存/加载（可移植/复用）──────────────────
save_path = os.path.join(HERE, 'workflow_sample.json')
r4 = wf.execute_workflow(wf1, save_to=save_path)
loaded = wf.load_workflow(save_path)
ok4 = (r4["ok"] and r4.get("saved_to") and loaded["n2"]["class_type"] == "code_unit"
       and loaded["n2"]["capability_id"] == "推导式-列表推导")
print(f'  保存 {r4.get("saved_to","")[-22:]} | 加载 n2 = '
      f'{loaded["n2"]["class_type"]}/{loaded["n2"]["capability_id"]}')
check('④ 工作流 JSON 保存/加载（可移植/共享/复用）', ok4)

# ── ⑤ 跨域链工作流（§7.3 工作流化：编译链数据流）───────────
# 两段 code_unit：信任累积 → 阈值检查（信任引擎跨单元链）
wf5 = {
    "acc": {"class_type": "code_unit", "capability_id": "VM-信任累积",
            "inputs": {"args": (0.5, 0.4)}},
    "chk": {"class_type": "code_unit", "capability_id": "校验-信任检查",
            "inputs": {"args": (0.3, 0.7)}},
}
r5 = wf.execute_workflow(wf5)
acc = r5["outputs"]["acc"]["result"]
chk = r5["outputs"]["chk"]["result"]
ok5 = r5["ok"] and acc == 0.9 and chk == 'fail'
print(f'  信任链: 累积(0.5,0.4)={acc} | 检查(0.3,0.7)={chk}')
check('⑤ 跨单元链工作流（累积→检查 独立节点并行执行）', ok5)

report = {
    "experiment": "白箱能力工作流化（荣：仿 ComfyUI，§17）",
    "topo_execution": ok1, "dataflow_edge": ok2,
    "cycle_detection": ok3, "json_persist": ok4,
    "cross_unit_chain": ok5,
    "model": {"node": "{class_type, inputs, capability_id}",
              "edge": "inputs 引用 [上游node, idx]",
              "execution": "拓扑排序 → 逐节点 → 结果缓存",
              "persist": "工作流 JSON 保存/加载/复用"},
    "conclusion": ("白箱能力 = 节点 + 边 + 工作流（ComfyUI 模型）——"
                   "代码单元/路由/MOS 声明都是能力节点；工作流可保存/加载/"
                   "复用；代码只是白箱能力的一个方向"),
}
rp = os.path.join(HERE, 'workflow_report.json')
json.dump(report, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
check('⑥ workflow_report.json 落盘', os.path.exists(rp), 'workflow_report.json')

print(f'\n=== 白箱能力工作流化: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
