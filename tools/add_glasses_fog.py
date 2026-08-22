# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
m = re.search(r'"液化":\s*\[[^\]]*\]', src)
assert m
new = '"液化": ["液化", "水蒸气凝结", "凝结成水", "露水", "露珠", "哈气成水", "小水珠", "起雾", "镜片起雾", "玻璃上有水珠", "冰饮料外壁水珠", "眼镜起雾"]'
src = src[:m.start()] + new + src[m.end():]
open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("液化 +眼镜起雾 OK")
