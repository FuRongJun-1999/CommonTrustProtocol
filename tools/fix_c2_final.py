# -*- coding: utf-8 -*-
"""c2 收尾：盐水不结冰 长短语赢回 + 牛奶冷藏移除 变质（靠蜂蜜防腐长短语）"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

# 盐水融雪 +盐水不容易结冰/不容易结冰/盐水难结冰
m = re.search(r'"盐水融雪":\s*\[[^\]]*\]', src)
assert m
salt = ['盐融雪', '盐化雪', '撒盐融冰', '融雪剂', '盐水融雪', '撒盐融雪', '冰点降低', '盐水不结冰', '除冰',
        '撒盐雪', '雪就化', '盐为什么', '不结冰', '融雪', '盐水不容易结冰', '不容易结冰', '盐水难结冰', '盐水会冻吗']
src = src[:m.start()] + '"盐水融雪": [%s]' % ", ".join('"%s"' % t for t in salt) + src[m.end():]

# 牛奶冷藏 移除 变质（通用词，蜂蜜变质/牛奶变质 各靠长短语）
m2 = re.search(r'"牛奶冷藏":\s*\[[^\]]*\]', src)
assert m2
milk = ['牛奶', '冷藏', '牛奶放冰箱', '牛奶容易坏', '牛奶怎么保存', '牛奶坏了', '牛奶放久', '鲜奶', '巴氏奶']
src = src[:m2.start()] + '"牛奶冷藏": [%s]' % ", ".join('"%s"' % t for t in milk) + src[m2.end():]

open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK")
