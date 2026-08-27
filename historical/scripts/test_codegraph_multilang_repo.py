# -*- coding: utf-8 -*-
"""test_codegraph_multilang_repo.py · 多语言仓库级分析测试（第五阶段·混合语言仓库）
验证：①混合仓库统一 IR（函数带语言/file 归属）②跨语言依赖树 ③跨语言调用定位
④跨语言影响分析 ⑤纯 Python 仓库回归"""
import sys, os, tempfile, shutil
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from codegraph_white import (analyze_repository, build_dependency_tree,
                             cross_file_calls, impact_analysis_repo)

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# 混合仓库：utils.py + lib.rs + main.js（main.js 导入并调用 utils 的 parse）
tmp = tempfile.mkdtemp(prefix="repo_ml_")
with open(os.path.join(tmp, "utils.py"), "w", encoding="utf-8") as f:
    f.write("def parse(data):\n    return data.split(',')\n")
with open(os.path.join(tmp, "lib.rs"), "w", encoding="utf-8") as f:
    f.write("fn format(x: i32) -> String {\n    x.to_string()\n}\n")
with open(os.path.join(tmp, "main.js"), "w", encoding="utf-8") as f:
    f.write("import { parse } from './utils'\n\n"
            "function process(data) {\n    return parse(data);\n}\n")

repo = analyze_repository(tmp)
fnames = sorted(repo["files"].keys())

# ① 混合仓库统一 IR：3 文件（py/js/rs），函数带语言归属
check('①a 混合仓库 3 文件', repo["file_count"] == 3, f'{repo["file_count"]} 文件: {fnames}')
fns = {f["name"]: (f["file"], f.get("lang", "")) for f in repo["functions"]}
check('①b 函数带 file+lang', fns.get("parse") == ("utils.py", "python")
      and fns.get("process") == ("main.js", "javascript")
      and fns.get("format") == ("lib.rs", "rust"), str(fns))

# ② 跨语言依赖树：main.js → utils.py
tree = build_dependency_tree(repo)
check('② main.js 依赖 utils.py', tree.get("main.js") == ["utils.py"], str(tree.get("main.js")))

# ③ 跨文件调用：main.js process 调 parse → 定位 utils.py（跨语言）
cc = cross_file_calls(repo)
js_calls = [(c[0], c[1], c[2]) for c in cc.get("main.js", [])]
check('③ 跨语言调用定位', any(c[0] == "process" and c[1] == "parse"
      and c[2] == "utils.py" for c in js_calls), str(js_calls))

# ④ 跨语言影响分析：改 utils.py parse → main.js process 在调用面
r = impact_analysis_repo(repo, "parse")
check('④ 跨语言影响分析', any(c["name"] == "process" and c["file"] == "main.js"
      for c in r["callers"]), str([(c["name"], c["file"]) for c in r["callers"]]))

# ⑤ 纯 Python 仓库回归（旧测试场景）
tmp2 = tempfile.mkdtemp(prefix="repo_ml_py_")
with open(os.path.join(tmp2, "a.py"), "w", encoding="utf-8") as f:
    f.write("import b\n\ndef run():\n    return b.helper()\n")
with open(os.path.join(tmp2, "b.py"), "w", encoding="utf-8") as f:
    f.write("def helper():\n    return 1\n")
repo2 = analyze_repository(tmp2)
check('⑤ 纯 Python 仓库回归', repo2["file_count"] == 2
      and build_dependency_tree(repo2).get("a.py") == ["b.py"],
      str(build_dependency_tree(repo2)))

shutil.rmtree(tmp, ignore_errors=True)
shutil.rmtree(tmp2, ignore_errors=True)

print(f'\n=== 多语言仓库级分析测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
