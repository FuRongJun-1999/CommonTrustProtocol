# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
old = "奇数是不能被2整除的整数——如1、3、5、7，除以2余1；偶数是能被2整除的整数，如2、4、6"
print("old len:", len(old))
print("old in src:", old in src)
pat = r'    "奇数": "'
for m in re.finditer(pat, src):
    ls = m.start(); le = src.index("\n", ls)
    line = src[ls:le]
    print("match:", repr(line[:100]))
