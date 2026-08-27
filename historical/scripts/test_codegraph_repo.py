# -*- coding: utf-8 -*-
"""test_codegraph_repo.py · codegraph 仓库级分析测试（第五阶段·代码理解深化）
验证：①仓库 IR（文件/函数/类带归属）②文件依赖树 ③跨文件调用 ④仓库统计"""
import sys, os, tempfile
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from codegraph_white import (analyze_repository, build_dependency_tree,
                             cross_file_calls, repo_stats)

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# 构造样例仓库（3 文件：main 导入 utils/models，utils 被 main 调用）
tmp = tempfile.mkdtemp(prefix="repo_sample_")
with open(os.path.join(tmp, "utils.py"), "w", encoding="utf-8") as f:
    f.write("import math\n\ndef parse(data):\n    return data.split(',')\n")
with open(os.path.join(tmp, "models.py"), "w", encoding="utf-8") as f:
    f.write("class Item:\n    def __init__(self, name):\n        self.name = name\n")
with open(os.path.join(tmp, "main.py"), "w", encoding="utf-8") as f:
    f.write("import utils\nimport models\n\ndef process(data):\n    tokens = utils.parse(data)\n    items = models.Item(tokens[0])\n    return items\n\ndef run():\n    return process('a,b')\n")

repo = analyze_repository(tmp)
fnames = sorted(repo["files"].keys())

# ① 仓库 IR：3 文件，函数带 file 归属
check('①a 仓库 3 文件', repo["file_count"] == 3, f'{repo["file_count"]} 文件: {fnames}')
fns = {f["name"]: f["file"] for f in repo["functions"]}
check('①b 函数带文件归属', fns.get("parse") == "utils.py"
      and fns.get("process") == "main.py" and fns.get("Item.__init__") == "models.py",
      str(fns))

# ② 文件依赖树：main → utils/models
tree = build_dependency_tree(repo)
check('②a main 依赖 utils+models', sorted(tree.get("main.py", [])) == ["models.py", "utils.py"],
      str(tree.get("main.py")))
check('②b utils 不依赖本地文件', tree.get("utils.py") == [], str(tree.get("utils.py")))

# ③ 跨文件调用：main.process 调 utils.parse → 定位 utils.py
cc = cross_file_calls(repo)
main_calls = [(c[0], c[1], c[2]) for c in cc.get("main.py", [])]
check('③a 跨文件调用定位', any(c[0] == "process" and c[1] == "parse"
      and c[2] == "utils.py" for c in main_calls), str(main_calls))

# ④ 仓库统计
st = repo_stats(repo)
check('④ 仓库统计', st["files"] == 3 and st["functions"] >= 4
      and st["classes"] == 1 and st["cross_calls"] >= 1, str(st))

# ⑤ 空目录诚实边界
empty = tempfile.mkdtemp(prefix="repo_empty_")
r0 = analyze_repository(empty)
check('⑤ 空目录诚实边界', r0["file_count"] == 0 and r0["function_count"] == 0, '')

import shutil
shutil.rmtree(tmp, ignore_errors=True)
shutil.rmtree(empty, ignore_errors=True)

print(f'\n=== codegraph 仓库级分析测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
