# -*- coding: utf-8 -*-
"""_t10_selfcheck.py · T10 自验收（手工正确实现 × 全断言，一次性）"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from t10_project_bench import PROJECTS, run_tests

IMPLS = {
    '订单状态机': (
        "LEGAL = {('待支付','支付'):'已支付', ('已支付','发货'):'已发货',\n"
        "         ('已发货','确认'):'已完成', ('待支付','取消'):'已取消'}\n"
        "def advance(state, action):\n"
        "    key = (state, action)\n"
        "    if key not in LEGAL:\n"
        "        raise ValueError('非法流转: ' + state + ' + ' + action)\n"
        "    return LEGAL[key]\n"),
    '日历推算': (
        "def is_leap(year):\n"
        "    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0\n"
        "def next_day(y, m, d):\n"
        "    dim = [31, 29 if is_leap(y) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]\n"
        "    d += 1\n"
        "    if d > dim[m-1]:\n"
        "        d = 1\n"
        "        m += 1\n"
        "        if m > 12:\n"
        "            m = 1\n"
        "            y += 1\n"
        "    return (y, m, d)\n"),
    '账单聚合': (
        "def summarize(records):\n"
        "    if not records:\n"
        "        return {'total': 0.0, 'by_category': {}, 'top': None}\n"
        "    by = {}\n"
        "    for r in records:\n"
        "        if r['amount'] > 0:\n"
        "            by[r['category']] = by.get(r['category'], 0) + r['amount']\n"
        "    total = round(sum(by.values()), 2)\n"
        "    top = None\n"
        "    if by:\n"
        "        mx = max(by.values())\n"
        "        top = sorted(k for k in by if by[k] == mx)[0]\n"
        "    return {'total': total, 'by_category': by, 'top': top}\n"),
    '编译器组合程序': (
        "def program_text():\n"
        "    return ('定义 面积（r）：返回 r 乘 r 乘 3.14；\\n'\n"
        "            '定义 总面积（n）：若 n 等于 0，则 返回 0，否则 返回 面积（n） 加 总面积（n 减 1）；\\n'\n"
        "            '结果 = 总面积（2）；止。')\n"),
}

allok = True
for proj in PROJECTS:
    impl = IMPLS[proj['name']]
    ok, why = run_tests(impl, proj['tests'])
    allok = allok and ok
    print(f"{proj['name']}: {'✓ 断言全过' if ok else '✘ ' + why[:120]}")
print('T10 自验收:', 'PASS' if allok else 'FAIL')
sys.exit(0 if allok else 1)
