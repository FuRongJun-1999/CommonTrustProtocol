# -*- coding: utf-8 -*-
"""round12 簇清理：发酵/氧化 去掉提取碎片，保留有意义的自然词"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

FER = ['发酵', '发面', '面团发酵', '面团为什么', '馒头为什么', '酵母', '酵母是',
       '蒸馒头', '酒酿', '酸奶', '腐乳', '酱油', '发酵是', '为什么会发酵',
       '面团发', '发起来了', '面发', '发酵粉', '泡打粉', '面团会发酵',
       '馒头', '松软', '发不起来', '不发起', '发酸']
OX = ['生锈速度', '防锈', '除锈', '铁锈', '锈迹', '为什么不生锈', '不锈钢为什么',
      '铁生锈', '生锈了', '生锈', '锈了', '苹果切开发黄', '切开发黄', '发黄',
      '铜绿', '银器变黑', '氧化', '有锈', '长锈', '菜刀生锈', '锈斑', '锈点', '锈断']

for theme, lst in (("发酵", FER), ("氧化", OX)):
    m = re.search(r'"%s":\s*\[[^\]]*\]' % theme, src)
    assert m, theme
    new = '"%s": [%s]' % (theme, ", ".join('"%s"' % t for t in lst))
    src = src[:m.start()] + new + src[m.end():]

open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("发酵(%d)/氧化(%d) 已清理" % (len(FER), len(OX)))
