# -*- coding: utf-8 -*-
"""test_multilang_ir.py · 多语言代码理解测试（第五阶段·统一 IR 跨语言）
验证：①三语言函数提取 ②JS 调用/导入 ③Rust 调用/导入 ④统一 IR 喂影响分析 ⑤诚实标注"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from multilang_ir import extract_ir, detect_language
from codegraph_white import build_call_graph, impact_analysis

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ① 三语言函数提取（统一 IR 结构）
py = extract_ir("def parse(data):\n    return split(data)\n\ndef split(d):\n    return d.split(',')\n", "a.py")
js = extract_ir("import { fs } from 'fs'\nfunction parse(data) {\n    return split(data);\n}\nconst split = (d) => d.split(',');\n", "b.js")
rs = extract_ir("use std::collections::HashMap;\nfn parse(data: &str) -> Vec<&str> {\n    split(data)\n}\nfn split(d: &str) -> Vec<&str> {\n    d.split(',').collect()\n}\n", "c.rs")
check('①a Python 提取', "parse" in [f["name"] for f in py["functions"]], str(py["lang"]))
check('①b JS 提取', "parse" in [f["name"] for f in js["functions"]]
      and "split" in [f["name"] for f in js["functions"]], str(js["functions"]))
check('①c Rust 提取', "parse" in [f["name"] for f in rs["functions"]]
      and "split" in [f["name"] for f in rs["functions"]], str(rs["functions"]))

# ② JS 调用/导入
js_parse = [f for f in js["functions"] if f["name"] == "parse"][0]
check('②a JS 调用提取', "split" in js_parse["calls"], str(js_parse["calls"]))
check('②b JS 导入提取', any(i["module"] == "fs" for i in js["imports"]), str(js["imports"]))

# ③ Rust 调用/导入
rs_parse = [f for f in rs["functions"] if f["name"] == "parse"][0]
check('③a Rust 调用提取', "split" in rs_parse["calls"], str(rs_parse["calls"]))
check('③b Rust 导入提取', any(i["module"] == "std" for i in rs["imports"]), str(rs["imports"]))

# ④ 统一 IR 喂 codegraph_white 影响分析（跨语言复用）
r = impact_analysis(rs, "split")
check('④ Rust IR 影响分析', "parse" in r["callers"], f'callers={r["callers"]}')

# ⑤ 诚实标注：JS/Rust light=True，Python 完整解析无 light
check('⑤a JS 诚实标注', js.get("light") is True, '')
check('⑤b Rust 诚实标注', rs.get("light") is True, '')
check('⑤c Python 完整解析', "light" not in py, '')

# ⑥ 语言检测
check('⑥a 扩展名检测', detect_language("", "x.rs") == "rust"
      and detect_language("", "x.js") == "javascript"
      and detect_language("", "x.py") == "python", '')

print(f'\n=== 多语言代码理解测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
