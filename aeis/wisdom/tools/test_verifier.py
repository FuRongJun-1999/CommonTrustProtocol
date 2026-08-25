# -*- coding: utf-8 -*-
"""test_verifier.py · 白箱本地校验器（Zero-LLM Verifier）测试
验证：六层校验链 + 本地缓存 + 深拷贝防污染 + 真实 CODE_UNITS 通过。
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from verifier import Verifier, VerifyRequest, VerifyCache  # noqa: E402

# 用临时缓存文件，避免污染 data/verify_cache.json
TEST_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "data", "test_verify_cache.json")


def reset_cache():
    if os.path.exists(TEST_CACHE):
        os.remove(TEST_CACHE)


def make_verifier():
    return Verifier(VerifyCache(TEST_CACHE))


GOOD_SORT = (
    "def solve(arr):\n"
    "    # 排序：冒泡法（相邻比较交换，最小元素浮到头部）\n"
    "    n = len(arr)\n"
    "    for i in range(n):\n"
    "        for j in range(n-1-i):\n"
    "            if arr[j] > arr[j+1]:\n"
    "                arr[j], arr[j+1] = arr[j+1], arr[j]\n"
    "    return arr\n"
)


def test_l1_syntax():
    reset_cache()
    v = make_verifier()
    r = v.verify(VerifyRequest(task="排序", code="def solve(arr):\n  return ", cases=[([1], [1])]))
    assert not r.ok, "语法错误应被拒绝"
    assert any(c["level"] == "L1语法" for c in r.checks)
    print("✓ L1 语法检测")


def test_l2_samples():
    reset_cache()
    v = make_verifier()
    # 正确排序
    r_ok = v.verify(VerifyRequest(
        task="排序", code=GOOD_SORT, cases=[([3, 1, 2], [1, 2, 3]), ([], [])]))
    assert r_ok.ok, "正确代码应通过 L2"
    # 错误排序（比较方向反了）
    bad = GOOD_SORT.replace(">", "<")
    r_bad = v.verify(VerifyRequest(
        task="排序", code=bad, cases=[([3, 1, 2], [1, 2, 3])]))
    assert not r_bad.ok, "错误代码应被 L2 拒绝"
    print("✓ L2 样例物理裁决")


def test_cache_hit():
    reset_cache()
    v = make_verifier()
    req = VerifyRequest(task="排序", code=GOOD_SORT, unit_id="t1",
                        cases=[([3, 1, 2], [1, 2, 3])])
    r1 = v.verify(req)
    assert not r1.cached
    r2 = v.verify(req)
    assert r2.cached, "相同请求第二次应命中缓存"
    assert r1.ok == r2.ok
    print("✓ 本地缓存命中（零计算零token）")


def test_no_pollution():
    """深拷贝：被校验代码原地修改输入，不得污染外部共享 cases。"""
    reset_cache()
    v = make_verifier()
    # 外部共享 cases（模拟 CODE_UNITS 引用）
    shared_cases = [([3, 1, 2], [1, 2, 3]), ([], [])]
    req = VerifyRequest(task="排序", code=GOOD_SORT, unit_id="t2",
                        cases=shared_cases)
    v.verify(req)
    assert shared_cases[0][0] == [3, 1, 2], "外部 cases 被污染！"
    print("✓ 深拷贝防污染")


def test_spec_compliance():
    reset_cache()
    v = make_verifier()
    # 任务=排序 但代码无比较结构 → 规范不符合
    r = v.verify(VerifyRequest(task="排序", code="def solve(arr):\n    return arr",
                               cases=[([3, 1, 2], [3, 1, 2])]))
    assert not r.ok, "无排序结构应被规范检查拒绝"
    assert any(c["level"] == "规范符合性" and not c["ok"] for c in r.checks)
    print("✓ 规范符合性（结构规则）")


def test_real_code_units():
    """真实 CODE_UNITS 全部通过（核心验收）。"""
    reset_cache()
    v = make_verifier()
    try:
        from code_compose import CODE_UNITS
    except ImportError:
        print("  (code_compose 不可用，跳过)")
        return
    passed, failed = 0, 0
    for unit_id, unit in CODE_UNITS.items():
        code = unit.get("pattern", "").replace("{fn}", "solve")
        if not code:
            continue
        r = v.verify(VerifyRequest(
            task=unit.get("task", unit_id), code=code, unit_id=unit_id,
            cases=unit.get("cases", [])))
        if r.ok:
            passed += 1
        else:
            failed += 1
    assert failed == 0, f"真实 CODE_UNITS 有 {failed} 个失败"
    assert passed >= 6
    print(f"✓ 真实 CODE_UNITS: {passed} 全部通过")


if __name__ == "__main__":
    print("=" * 60)
    print("白箱本地校验器测试（Zero-LLM Verifier）")
    print("=" * 60)
    test_l1_syntax()
    test_l2_samples()
    test_cache_hit()
    test_no_pollution()
    test_spec_compliance()
    test_real_code_units()
    reset_cache()
    print("\n" + "=" * 60)
    print("全部测试通过 ✅（零 LLM）")
    print("=" * 60)
