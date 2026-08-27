# -*- coding: utf-8 -*-
"""通道 B 初稿：复合赋值执行器（mini_aug_apply）。"""


def mini_aug_apply(cur, op, rhs):
    """复合赋值执行器：按 op 对 cur 施加复合赋值运算，返回运算后的新值。

    生效条件与行为：
    - op 只能是 '+='、'-='、'*='、'/=' 四种字符串之一；
      传入其他 op 时抛 ValueError("unknown op")。
    - '+='：加法；当 cur 与 rhs 均为字符串时为拼接。
    - '-='：减法；'*='：乘法（数字参与；操作数类型不兼容时
      由 Python 原生运算抛出 TypeError，本函数不做额外包装）。
    - '/='：真除法，始终返回 float（例如 10 /= 4 得到 2.5）；
      rhs 为 0（含 0.0）时抛 ValueError("division by zero")。
    - 本函数不修改 cur，只返回新值。
    """
    if op == '+=':
        return cur + rhs
    if op == '-=':
        return cur - rhs
    if op == '*=':
        return cur * rhs
    if op == '/=':
        if rhs == 0:
            raise ValueError("division by zero")
        return cur / rhs
    raise ValueError("unknown op")
