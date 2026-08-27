# -*- coding: utf-8 -*-
"""通道 B 初稿：str.split 基础版（mini_split）。"""


def mini_split(s, sep):
    """str.split(sep) 的基础手写版：按单字符分隔符扫描切分字符串。

    生效条件与行为：
    - s 为非空字符串，sep 为单字符分隔符，返回子串列表。
    - 保留空段：连续分隔符不合并，
      例如 mini_split("a,,b", ",") → ["a", "", "b"]；
      mini_split("a,b,c", ",") → ["a", "b", "c"]。
    - s 为空字符串时返回 [""]；sep 不在 s 中时返回 [s]。
    - 不调用 s.split()，使用手写的线性扫描逻辑实现。
    """
    result = []
    start = 0
    i = 0
    n = len(s)
    while i < n:
        if s[i] == sep:
            result.append(s[start:i])
            start = i + 1
        i += 1
    result.append(s[start:])
    return result
