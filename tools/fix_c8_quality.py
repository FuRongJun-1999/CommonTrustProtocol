# -*- coding: utf-8 -*-
"""c8 质量修复：浅色衣服长短语赢回 + 散步chitchat/减肥劫持"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

# 浅色衣服 +防晒穿什么颜色/穿什么颜色暖和（长短语赢过黑色吸热）
m = re.search(r'"浅色衣服":\s*\[[^\]]*\]', src)
assert m
lst = ['穿浅色衣服', '浅色衣服凉快', '浅色吸热', '浅色衣服', '深色衣服', '穿什么颜色', '浅色深色', '夏天穿', '黑色吸热',
       '防晒穿', '穿什么颜色暖和', '什么颜色暖和', '什么颜色凉快', '防晒衣',
       '防晒穿什么颜色', '防晒穿什么', '穿什么颜色防晒', '冬天穿什么颜色']
src = src[:m.start()] + '"浅色衣服": [%s]' % ", ".join('"%s"' % t for t in lst) + src[m.end():]

# 散步 +每天散步好吗/饭后散步好不好/散步能减肥吗（chitchat 散步 子串拦截）
m2 = re.search(r'"散步":\s*\[[^\]]*\]', src)
assert m2
lst2 = ['去散步', '想散步', '散步好', '散步', '饭后走一走', '散步是', '每天散步', '散步好处', '走路散步',
        '散步能减肥', '散步减肥', '每天散步好吗', '散步好吗', '饭后散步', '饭后散步好吗', '散步能', '散步有什么好处']
src = src[:m2.start()] + '"散步": [%s]' % ", ".join('"%s"' % t for t in lst2) + src[m2.end():]

open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK")
