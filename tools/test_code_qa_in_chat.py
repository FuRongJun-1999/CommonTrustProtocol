# -*- coding: utf-8 -*-
"""test_code_qa_in_chat.py · 代码问答进 chat_engine 主路由（第五阶段）
验证：①代码问题自动走代码理解通道（code_qa=True）②非代码问题不劫持
③泛词（影响/依赖）未命中回落主流程 ④无 code_qa_fn 时正常流程"""
import sys, os, tempfile, shutil
sys.stdout.reconfigure(encoding='utf-8')
CTP = r'D:\Program Files\2_ai\CommonTrustProtocol'
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
sys.path.insert(0, CTP + r'\tools')
sys.path.insert(0, CTP + r'\aeis')
import wisdom.chat_engine as ce
sys.path.insert(0, CTP + r'\tools')
from codegraph_white import analyze_repository
from code_qa import code_qa

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

tmp = tempfile.mkdtemp(prefix="cqa_chat_")
with open(os.path.join(tmp, "lib.py"), "w", encoding="utf-8") as f:
    f.write("def base(x):\n    return x\n\ndef a():\n    return base(1)\n"
            "\ndef b():\n    return base(2)\n")
repo = analyze_repository(tmp)
qa_fn = lambda q: code_qa(q, repo)

# ① 代码问题自动走代码理解通道
r1 = ce.chat(dex=None, message="改 base 会影响哪些函数？", code_qa_fn=qa_fn)
check('①a 影响问答走代码通道', r1.get("code_qa") and "a" in r1.get("reply", "")
      and "b" in r1.get("reply", ""), r1.get("reply", "")[:36])
r2 = ce.chat(dex=None, message="a 和 b 能并行测试吗？", code_qa_fn=qa_fn)
check('①b 并行问答走代码通道', r2.get("code_qa") and "串行" in r2.get("reply", ""),
      r2.get("reply", "")[:36])
r3 = ce.chat(dex=None, message="仓库里有多少函数？", code_qa_fn=qa_fn)
check('①c 统计问答走代码通道', r3.get("code_qa") and "3 个函数" in r3.get("reply", ""),
      r3.get("reply", "")[:36])

# ② 非代码问题不劫持
r4 = ce.chat(dex=None, message="你好呀", code_qa_fn=qa_fn)
check('② 非代码问题不劫持', not r4.get("code_qa"))

# ③ 泛词未命中回落（「雾霾影响健康」→ code_qa 判断非代码问答 → 回落主流程）
r5 = ce.chat(dex=None, message="雾霾对健康有什么影响？", code_qa_fn=qa_fn)
check('③ 泛词未命中回落主流程', not r5.get("code_qa") and r5.get("reply", ""),
      r5.get("reply", "")[:24])

# ④ 无 code_qa_fn 时正常流程（不影响感知/普通对话）
r6 = ce.chat(dex=None, message="改 base 会影响哪些函数？")
check('④ 无 code_qa_fn 正常流程', not r6.get("code_qa") and r6.get("reply", ""),
      r6.get("reply", "")[:24])

shutil.rmtree(tmp, ignore_errors=True)

print(f'\n=== 代码问答进主路由测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
