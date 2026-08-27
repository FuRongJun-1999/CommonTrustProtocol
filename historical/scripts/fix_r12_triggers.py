# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

# 发酵 +面团会发酵/面团发起来（决胜更长的触发词）
m = re.search(r'"发酵":\s*\[([^\]]*)\]', src)
assert m
fer = ['发酵', '发面', '面团发酵', '面团为什么', '馒头为什么', '酵母', '酵母是',
       '蒸馒头', '酒酿', '酸奶', '腐乳', '酱油', '发酵是', '为什么会发酵',
       '面团发', '发起来了', '面发', '发酵粉', '泡打粉', '面团会发酵']
src = src[:m.start()] + '"发酵": [%s]' % ", ".join('"%s"' % t for t in fer) + src[m.end():]

# 氧化 +有锈/长锈/菜刀生锈
m2 = re.search(r'"氧化":\s*\[([^\]]*)\]', src)
assert m2
ox = ['生锈速度', '防锈', '除锈', '铁锈', '锈迹', '为什么不生锈', '不锈钢为什么',
      '铁生锈', '生锈了', '生锈', '锈了', '苹果切开发黄', '切开发黄', '发黄',
      '铜绿', '银器变黑', '氧化', '有锈', '长锈', '菜刀生锈']
src = src[:m2.start()] + '"氧化": [%s]' % ", ".join('"%s"' % t for t in ox) + src[m2.end():]

open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK 发酵(%d)/氧化(%d)" % (len(fer), len(ox)))
