# -*- coding: utf-8 -*-
"""draft_flash_aug.py · T5 通道 B 初稿（GLM-5.3-Flash 生成，待白箱校验器裁决）
生效条件：MiniPy 复合赋值语句的求值内核需要独立可测单元。
执行：op 四值分派；'/=' 真除且零除报错；字符串 '+=' 为拼接。
不适用条件：非四值 op、下标/属性目标（本单元只管标量绑定）。
"""


def mini_aug_apply(cur, op, rhs):
    """复合赋值执行器：对当前值 cur 施加 op rhs，返回新值。

    生效条件：op ∈ {'+=', '-=', '*=', '/='}。
    行为：'/=' 为真除（恒返回 float），rhs 为 0 抛 ValueError("division by zero")；
    未知 op 抛 ValueError("unknown op")；'+=' 对字符串为拼接。
    """
    if op == "+=":
        return cur + rhs
    if op == "-=":
        return cur - rhs
    if op == "*=":
        return cur * rhs
    if op == "/=":
        if rhs == 0:
            raise ValueError("division by zero")
        return cur / rhs
    raise ValueError("unknown op")
