# -*- coding: utf-8 -*-
"""solidify_demo.py · 生成自举闭环演示——组合生成 → 自校验 → 固化 → 直答
自举纪律：自校验通过的知识才固化（错误生成不得固化）。
固化后：同问法/触发词变体直接直答（不再重新组合），且持久化跨进程生效。"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import compose_engine as ce

print('=== 生成自举闭环：组合生成 → 自校验 → 固化 → 直答 ===\n')

# ① 组合生成新知识（未预写）+ 自校验
q1 = '为什么金属勺放进热汤会烫手？'
r1 = ce.route_compose(q1)
print(f'① 组合生成「{q1}」')
print(f'   自校验: {"✔ 通过" if r1["ok"] else "✘ 失败"} | 生成: {r1["answer"]}')

# ② 固化（自校验通过才固化）
entry = ce.solidify(q1, triggers=['金属勺', '热汤', '烫手'])
print(f'② 固化: {"✔ 已固化（触发词: 金属勺/热汤/烫手）" if entry else "✘ 未固化（自校验未过）"}')
print(f'   持久化: {ce._SOLIDIFY_FILE}')

# ③ 固化后：同问法直接直答（不走组合）
r2 = ce.route_compose(q1)
print(f'\n③ 固化后同问法: {"✔ 固化直答" if r2.get("solidified") else "✘ 仍走组合"}')
print(f'   → {r2["answer"]}')

# ④ 触发词变体（生成泛化：同一固化答案覆盖变体问法）
q2 = '为什么铁勺会烫手？'
r3 = ce.route_compose(q2)
print(f'\n④ 变体问法「{q2}」: {"✔ 触发词命中固化直答" if r3.get("solidified") else "✘ 未命中"}')
print(f'   → {r3["answer"]}')

# ⑤ 自举纪律：矛盾问题自校验失败 → 不得固化
q3 = '高原上水为什么烧得特别热？'
r4 = ce.route_compose(q3)
entry2 = ce.solidify(q3, triggers=['高原', '特别热'])
print(f'\n⑤ 自举纪律: 「{q3}」自校验 {"✘ 失败" if not r4["ok"] else "✔"} '
      f'→ 固化结果: {"✘ 拒绝固化（错误知识不固化）✔" if entry2 is None else "✘ 违规固化!"}')

# ⑥ 跨进程持久化验证：新进程重新加载固化库
import subprocess
probe = subprocess.run([sys.executable, '-c',
    "import sys; sys.path.insert(0, r'D:\\Program Files\\2_ai\\CommonTrustProtocol\\tools');"
    "import compose_engine as ce;"
    "r = ce.route_compose('为什么金属勺放进热汤会烫手？');"
    "print('新进程加载 → 固化直答:', r.get('solidified'), '|', r['answer'][:40])"],
    capture_output=True, text=True, encoding='utf-8')
print(f'\n⑥ 跨进程持久化: {probe.stdout.strip()}')

print('\n=== 生成自举闭环演示完成（生成→自校验→固化→直答 全白箱零 LLM） ===')
