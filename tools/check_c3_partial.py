# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
for c in ("加法", "函数定义", "勾股定理", "等差数列", "负数正数", "零自然数", "正方形长方形", "乘法口诀", "三角形面积", "分数定义", "奇数", "偶数"):
    ans = st.REVERSE_DAILY.get(c, "")
    print(f"{c}: len={len(ans)} head={ans[:20]}")
