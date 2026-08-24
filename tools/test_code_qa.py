# -*- coding: utf-8 -*-
"""test_code_qa.py · 代码问答测试（第五阶段·代码条件单元库进对话）
验证：①影响问答 ②依赖问答 ③并行问答 ④统计问答 ⑤诚实回落"""
import sys, os, tempfile, shutil
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from codegraph_white import analyze_repository
from code_qa import code_qa, _classify, _extract_funcs

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

tmp = tempfile.mkdtemp(prefix="cqa_")
with open(os.path.join(tmp, "lib.py"), "w", encoding="utf-8") as f:
    f.write("def base(x):\n    return x\n\ndef a():\n    return base(1)\n"
            "\ndef b():\n    return base(2)\n\ndef c():\n    return a()\n"
            "\ndef d():\n    return 42\n")
repo = analyze_repository(tmp)

# ① 影响问答：改 base → a/b 受影响（含深度）
r = code_qa("改 base 会影响哪些函数？", repo)
check('①a 影响问答命中', r.get("ok") and "a" in r.get("reply", "")
      and "b" in r.get("reply", ""), r.get("reply", "")[:40])
check('①b 影响含文件定位', "lib.py" in r.get("reply", ""), r.get("reply", "")[:40])

# ② 依赖问答
r = code_qa("base 依赖什么？", repo)
check('②a 依赖问答命中', r.get("ok") and "不依赖" in r.get("reply", ""), r.get("reply", "")[:30])
r = code_qa("a 依赖什么？", repo)
check('②b 依赖列表', r.get("ok") and "base" in r.get("reply", ""), r.get("reply", "")[:30])

# ③ 并行问答：a×d 独立可并行；a×b 共享 base 串行
r = code_qa("a 和 d 能并行测试吗？", repo)
check('③a 独立可并行', r.get("ok") and "可以并行" in r.get("reply", ""), r.get("reply", "")[:30])
r = code_qa("a 和 b 能并行测试吗？", repo)
check('③b 共享依赖串行', r.get("ok") and "串行" in r.get("reply", ""), r.get("reply", "")[:36])

# ④ 统计问答
r = code_qa("仓库里有多少函数？", repo)
check('④ 统计问答', r.get("ok") and "5 个函数" in r.get("reply", ""), r.get("reply", "")[:36])

# ⑤ 诚实回落：非代码问题 / 函数不存在
r = code_qa("什么是碳中和？", repo)
check('⑤a 非代码问题回落', not r.get("ok") and r.get("type") is None, r.get("reply", "")[:24])
r = code_qa("改 nonexist 会影响什么？", repo)
check('⑤b 未知函数回落', not r.get("ok") and "未识别" in r.get("reply", ""), r.get("reply", "")[:30])

# ⑥ 类型识别 + 函数提取
check('⑥a 类型识别', _classify("改 base 影响谁") == "影响"
      and _classify("能并行测试吗") == "并行", '')
from code_route_bridge import build_code_route_units
units = build_code_route_units(repo)
check('⑥b 函数提取', _extract_funcs("改 base 影响谁", units) == ["base"]
      and len(_extract_funcs("a 和 d 能并行吗", units)) >= 2, '')

shutil.rmtree(tmp, ignore_errors=True)

print(f'\n=== 代码问答测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
