# -*- coding: utf-8 -*-
"""test_codegraph_impact_repo.py · 仓库级影响分析测试（第五阶段·跨文件调用面）
验证：①改 utils.parse → main 受影响（跨文件）②files_affected ③深度 ④无关函数不在面"""
import sys, os, tempfile, shutil
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from codegraph_white import analyze_repository, impact_analysis_repo

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# 样例仓库：utils.parse ← main.process ← main.run；models 独立
tmp = tempfile.mkdtemp(prefix="repo_impact_")
with open(os.path.join(tmp, "utils.py"), "w", encoding="utf-8") as f:
    f.write("def parse(data):\n    return data.split(',')\n\n"
            "def format(x):\n    return str(x)\n")
with open(os.path.join(tmp, "models.py"), "w", encoding="utf-8") as f:
    f.write("class Item:\n    def __init__(self, name):\n        self.name = name\n")
with open(os.path.join(tmp, "main.py"), "w", encoding="utf-8") as f:
    f.write("import utils\nimport models\n\n"
            "def process(data):\n    return utils.parse(data)\n\n"
            "def run():\n    return process('a,b')\n")
repo = analyze_repository(tmp)

# ① 改 utils.parse → 调用面含 main.process（跨文件）
r = impact_analysis_repo(repo, "parse")
names = {c["name"] for c in r["callers"]}
check('①a 跨文件调用面含 process', "process" in names, f'callers={names}')
check('①b 调用者带文件定位', any(c["name"] == "process" and c["file"] == "main.py"
      for c in r["callers"]), str(r["callers"]))

# ② files_affected
check('② 受影响文件', "main.py" in r["files_affected"]
      and "utils.py" in r["files_affected"], str(r["files_affected"]))

# ③ 深度：run→process→parse（run depth=2）
check('③ 深度正确', r["depth"].get("process") == 1 and r["depth"].get("run") == 2,
      str(r["depth"]))

# ④ 无关函数不在调用面（models.Item 不调 parse；parse 不调 format）
r2 = impact_analysis_repo(repo, "parse")
check('④ 无关函数不在面', all("Item" not in c["name"] for c in r2["callers"]), '')

# ⑤ 目标函数不存在 → 诚实边界
r3 = impact_analysis_repo(repo, "nope")
check('⑤ 不存在目标诚实边界', r3["target_file"] is None and r3["callers"] == [], '')

shutil.rmtree(tmp, ignore_errors=True)

print(f'\n=== 仓库级影响分析测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
