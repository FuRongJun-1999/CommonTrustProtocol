# -*- coding: utf-8 -*-
"""test_ds_compose.py · 数据结构/算法概念测试（第四阶段·代码深学）
验证：①九概念组合生成 ②方向识别 ③单字排除 ④非数据结构问题回落"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from ds_compose import ds_route, identify_ds_direction

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ① 九概念组合生成（答案含核心词≥2 由自校验保证，这里再验关键语义词）
QS = {
    "什么是数组？": ("数组", "O(1)"),
    "链表和数组有什么区别？": ("链表", "节点"),
    "什么是栈？": ("栈", "LIFO"),
    "队列有什么用？": ("队列", "FIFO"),
    "什么是二叉树？": ("树", "O(log n)"),
    "什么是图数据结构？": ("图", "路径"),
    "为什么用哈希表？": ("哈希", "O(1)"),
    "排序为什么是 O(n log n)？": ("排序", "O(n log n)"),
    "什么是时间复杂度？": ("复杂度", "渐进"),
}
for q, (kw1, kw2) in QS.items():
    r = ds_route(q)
    ans = r.get("answer", "")
    ok = r.get("ok") and kw1 in ans and kw2 in ans
    check(f'① 概念生成: {q[:14]}…', ok, ans[:36])

# ② 方向识别（最长关键词）
check('②a 树识别', identify_ds_direction("什么是二叉搜索树") == "树")
check('②b 队列识别', identify_ds_direction("消息队列有什么用") == "队列")
check('②c 排序识别', identify_ds_direction("快排是什么") == "排序")

# ③ 单字排除：图片/图像不命中图域
check('③a 图片排除', identify_ds_direction("图片处理有哪些步骤") is None)
check('③b 图像排除', identify_ds_direction("图像识别怎么做") is None)

# ④ 非数据结构问题回落 + 跨域不串扰
r = ds_route("什么是碳中和？")
check('④a 非数据结构回落', not r.get("ok") and "落回" in r.get("reason", ""))
r = ds_route("为什么要写单元测试？")
check('④b 软件工程问题不串扰', not r.get("ok"))

print(f'\n=== 数据结构/算法概念测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
