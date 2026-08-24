# -*- coding: utf-8 -*-
"""test_graph_db.py · 图数据库白箱自举测试（第六阶段·目标6 初级复现）
流程：图数据库单元库 → 白箱生成 → 三层自校验（L1 语法/L2 样例）
→ 外部校准（组装：单元互相调用 + 对照条件路由图语义）
"""
import sys, ast
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from graph_db_units import GRAPH_UNITS, route_graph_unit

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

generated = {}
for uid, u in GRAPH_UNITS.items():
    tree = ast.parse(u["pattern"])
    ns = {}
    exec(compile(tree, "<unit>", "exec"), ns)
    # 图存储单元提供 Graph 类——其它单元注入
    if uid != "图存储-节点边":
        ns["Graph"] = generated["图存储-节点边"][0]["Graph"]
    fn_names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    fn = ns[fn_names[0]] if fn_names else None
    l2_ok, detail = True, ""
    if fn or uid == "图存储-节点边":
        for args, expect in u["cases"]:
            try:
                if args == "call":
                    if uid == "图持久化-序列化":
                        g = generated["图存储-节点边"][0]["Graph"]()
                        got = ns["graph_to_json"](g)
                    elif uid == "图持久化-文件":
                        got = ns["graph_file_ops"]()
                    elif uid in ("图遍历-路径枚举", "条件路由图-查询"):
                        g = generated["图存储-节点边"][0]["Graph"]()
                        g.add_edge("气压低", "沸点降")
                        g.add_edge("沸点降", "煮不熟")
                        g.add_edge("气压低", "缺氧")
                        g.add_edge("缺氧", "煮不熟")
                        got = fn(g, "气压低", "煮不熟") if uid == "图遍历-路径枚举" \
                            else fn(g, "气压低")
                    else:
                        got = ns["graph_ops"]()
                elif uid == "图遍历-BFS" or uid == "图遍历-路径":
                    # 注入图：条件链图（气压低→沸点降→煮不熟）
                    g = generated["图存储-节点边"][0]["Graph"]()
                    g.add_edge("气压低", "沸点降")
                    g.add_edge("沸点降", "煮不熟")
                    got = fn(g, *args[1:]) if isinstance(args, tuple) else fn(g, args)
                elif uid == "条件路由图-映射":
                    units = {"沸点降": {"conditions": ["气压低"]},
                             "煮不熟": {"conditions": ["沸点降"]}}
                    got = fn(units)
                    got = got.neighbors("气压低")  # 期望输出：气压低 的后继
                else:
                    got = fn(*args) if isinstance(args, tuple) else fn(args)
                if got != expect:
                    l2_ok, detail = False, f"{args} → {got!r} ≠ {expect!r}"
                    break
            except Exception as e:
                l2_ok, detail = False, f"{args} → 异常 {e}"
                break
    check(f'L2 样例[{uid}]', l2_ok, detail)
    if l2_ok:
        generated[uid] = (ns, fn)

# 外部校准：组装端到端——条件单元库 → 条件路由图 → 遍历（影响传播）
if "条件路由图-映射" in generated and "图遍历-BFS" in generated:
    map_ns = generated["条件路由图-映射"][0]
    bfs_fn = generated["图遍历-BFS"][1]
    g = map_ns["units_to_graph"]({"沸点降": {"conditions": ["气压低"]},
                                  "煮不熟": {"conditions": ["沸点降"]}})
    reach = bfs_fn(g, "气压低")
    check('校准① 条件路由图遍历(气压低→沸点降→煮不熟)', reach == ["气压低", "沸点降", "煮不熟"],
          str(reach))

# 校准②：持久化往返（存储层）
if "图持久化-序列化" in generated:
    ser = generated["图持久化-序列化"][0]
    g = generated["图存储-节点边"][0]["Graph"]()
    g.add_edge("气压低", "沸点降")
    text = ser["graph_to_json"](g)
    g2 = ser["graph_from_json"](text)
    check('校准② 图持久化往返', g2.nodes == g.nodes
          and g2.neighbors("气压低") == ["沸点降"], f'nodes={sorted(g2.nodes)}')

# 校准③：任务识别
check('校准③ 任务识别', route_graph_unit("图遍历怎么做") == "图遍历-BFS"
      and route_graph_unit("图序列化") == "图持久化-序列化", '')

print(f'\n=== 图数据库白箱自举测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
