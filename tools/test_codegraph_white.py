# -*- coding: utf-8 -*-
"""test_codegraph_white.py · 白箱代码理解测试（第五阶段·codegraph 模式落地）
验证：①IR 提取（函数/类/导入/调用）②调用图 ③影响分析 ④环检测 ⑤无调用函数"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from codegraph_white import extract_code_ir, build_call_graph, impact_analysis, detect_cycles

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

SAMPLE = '''
import math
import os

def parse(data):
    return split(data)

def split(data):
    return data.split(",")

def compute(tokens):
    return parse(tokens)

def main():
    result = compute("a,b")
    print(result)

class Service:
    def handle(self, req):
        return compute(req)

def recursive(n):
    if n <= 1:
        return 1
    return n * recursive(n - 1)

def standalone():
    return 42
'''
ir = extract_code_ir(SAMPLE, "sample.py")
names = [f["name"] for f in ir["functions"]]

# ① IR 提取
check('①a 函数提取', "parse" in names and "compute" in names and "recursive" in names,
      f'{len(ir["functions"])} 函数: {names}')
check('①b 类方法提取', "Service" in [c["name"] for c in ir["classes"]]
      and "Service.handle" in names, '类+方法')
check('①c 导入提取', any(i["module"] == "os" for i in ir["imports"])
      and any(i["module"] == "math" for i in ir["imports"]), str(ir["imports"]))
check('①d 调用提取', "parse" in [f["calls"] for f in ir["functions"] if f["name"] == "compute"][0],
      'compute 调用 parse')

# ② 调用图
g = build_call_graph(ir)
check('② 调用图', g.get("compute") == ["parse"] and "compute" in g.get("main", []),
      f'compute->{g.get("compute")}, main->{g.get("main")}')

# ③ 影响分析：改 compute → main/Service.handle 受影响
r = impact_analysis(ir, "compute", max_depth=3)
check('③a 影响面含 main', "main" in r["callers"], f'callers={r["callers"]}')
check('③b 影响面含 Service.handle', "Service.handle" in r["callers"], str(r["callers"]))
check('③c 直接调用者深度1', r["depth"].get("main") == 1, str(r["depth"]))

# ④ 环检测：parse→split 无环；recursive 自环不计；构造 A→B→A 环
check('④a 无环样本', detect_cycles(ir) == [], str(detect_cycles(ir)))
SAMPLE_CYCLE = '''
def a():
    return b()
def b():
    return c()
def c():
    return a()
'''
ir2 = extract_code_ir(SAMPLE_CYCLE, "cycle.py")
cycles = detect_cycles(ir2)
check('④b 调用环检出', len(cycles) == 1 and set(cycles[0]) == {"a", "b", "c"},
      f'cycles={cycles}')

# ⑤ 无调用函数（孤立节点）
check('⑤ 孤立函数处理', impact_analysis(ir, "standalone")["callers"] == [],
      f'standalone callers={impact_analysis(ir, "standalone")["callers"]}')

print(f'\n=== 白箱代码理解测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
