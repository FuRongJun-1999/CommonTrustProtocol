# -*- coding: utf-8 -*-
"""draft_flash_split.py · T5 通道 B 初稿（GLM-5.3-Flash 生成，待白箱校验器裁决）
生效条件：MiniPy str 方法白名单 split 的可测实现单元。
执行：单字符分隔符线性扫描，保留空段，不合并连续分隔符。
不适用条件：多字符分隔符、正则语义、maxsplit 参数。
"""


def mini_split(s, sep):
    """str.split 基础版：按单字符 sep 切分 s，返回子串列表。

    生效条件：s 为字符串，sep 为单字符。
    行为：保留空段（"a,,b" → ["a", "", "b"]）；s 为空返回 [""]；
    sep 不在 s 中返回 [s]；不调用内建 split，手写扫描。
    """
    if sep not in s:
        return [s]
    parts = []
    buf = []
    for ch in s:
        if ch == sep:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    parts.append("".join(buf))
    return parts
