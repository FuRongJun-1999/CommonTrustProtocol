# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
olds = {
    "三角形面积": "三角形的面积等于底乘高除2——底乘高再除以2，就是三角形面积（底乘高除2）",
    "分数定义": "分数由分子分母组成：分母表示把整体分成几份，分子表示取其中几份——这就是分数（分子分母）",
    "奇数": "奇数是不能被2整除的整数——如1、3、5、7，除以2余1；偶数是能被2整除的整数，如2、4、6",
    "偶数": "偶数是能被2整除的整数——如2、4、6、8；奇数不能被2整除，如1、3、5",
}
for key, old in olds.items():
    lines = [l for l in src.splitlines() if l.startswith('    "%s": "' % key)]
    if not lines:
        print(f"{key}: NO LINE"); continue
    line = lines[0]
    print(f"{key}: match={old in line}")
    if old not in line:
        print(f"   actual: {repr(line[:120])}")
