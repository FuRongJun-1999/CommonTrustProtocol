# -*- coding: utf-8 -*-
"""GLM-5.3-Flash 白箱编码测试 · 三个新增算法单元

以白箱自举管线的工作方式生成：pattern 模板格式 + 物理用例 + 中文注释规范
（条件论 R1），每单元立即过 verifier（L1 语法 / L2 样例 / L3 边界 / 规范）。
"""

# ── 单元 1：二分查找 ──────────────────────────────────────────
BINARY_SEARCH_CODE = '''
def bin_search(arr, target):
    """有序数组二分查找：命中返回索引，未命中返回 -1（要求 arr 升序）。"""
    lo, hi = 0, len(arr) - 1          # 双指针闭区间 [lo, hi]
    while lo <= hi:
        mid = (lo + hi) // 2          # 中点防溢出用整除
        if arr[mid] == target:
            return mid                # 命中：返回当前索引
        elif arr[mid] < target:
            lo = mid + 1              # 目标在右半区
        else:
            hi = mid - 1              # 目标在左半区
    return -1                         # 区间收空：未命中
'''.strip()

BINARY_SEARCH_CASES = [
    (([1, 3, 5, 7, 9], 7), 3),
    (([1, 3, 5, 7, 9], 4), -1),
    (([], 5), -1),
    (([42], 42), 0),
    (([1, 2, 3], 1), 0),
    (([1, 2, 3], 3), 2),
]

# ── 单元 2：快速排序（纯函数版，返回新列表）────────────────────
QUICKSORT_CODE = '''
def quick_sort(arr):
    """快速排序（纯函数）：返回升序新列表，不修改原输入。"""
    if len(arr) <= 1:
        return list(arr)              # 基线：空/单元素直接拷贝返回
    pivot = arr[len(arr) // 2]        # 取中位元素为基准
    left = [x for x in arr if x < pivot]
    mid = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + mid + quick_sort(right)
'''.strip()

QUICKSORT_CASES = [
    ([3, 1, 2], [1, 2, 3]),
    ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
    ([], []),
    ([7], [7]),
    ([2, 2, 1, 1], [1, 1, 2, 2]),
    ([-3, 0, -1, 5], [-3, -1, 0, 5]),
]

# ── 单元 3：字符串逆置 ────────────────────────────────────────
STR_REVERSE_CODE = '''
def str_reverse(s):
    """字符串逆置：双指针原地交换字符序列，返回新字符串（Unicode 安全）。"""
    chars = list(s)                   # 字符串不可变，先转字符列表
    left, right = 0, len(chars) - 1   # 双指针从两端向中间收拢
    while left < right:
        chars[left], chars[right] = chars[right], chars[left]
        left += 1                     # 左指针右移
        right -= 1                    # 右指针左移
    return "".join(chars)             # 重组为字符串
'''.strip()

STR_REVERSE_CASES = [
    ("abc", "cba"),
    ("", ""),
    ("a", "a"),
    ("ab", "ba"),
    ("灵枢白箱", "箱白枢灵"),
]

UNITS = [
    ("二分查找", BINARY_SEARCH_CODE, BINARY_SEARCH_CASES),
    ("快速排序", QUICKSORT_CODE, QUICKSORT_CASES),
    ("字符串逆置", STR_REVERSE_CODE, STR_REVERSE_CASES),
]
