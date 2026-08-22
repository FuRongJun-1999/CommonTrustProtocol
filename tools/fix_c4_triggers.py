# -*- coding: utf-8 -*-
"""c4 触发词补盲：5 个缺口"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

UPD = {
    "板块构造": ['板块构造', '板块运动', '地壳板块', '板块', '大陆漂移', '魏格纳', '地震', '火山', '地壳运动', '板块交界',
               '漂移', '大陆漂移说', '板块移动', '为什么地震', '为什么火山'],
    "四季成因": ['为什么有四季', '四季怎么来的', '四季成因', '春夏秋冬', '四季是', '为什么四季', '地轴倾斜', '直射点', '夏至冬至', '二十四节气',
               '南北半球', '季节相反', '为什么有春夏秋冬', '四季怎么形成'],
    "白天黑夜": ['白天和黑夜', '黑夜和白天', '白天黑夜', '为什么有白天', '昼夜', '为什么天黑', '天亮', '昼夜交替', '地球自转', '时区', '昼夜长短',
               '时间不同', '为什么时间不同', '时差', '世界各地时间', '东边先'],
    "夏天冬天": ['夏天和冬天', '冬天和夏天', '夏天热还是', '夏天冬天', '为什么夏天热', '为什么冬天冷', '夏至', '冬至', '太阳高度', '四季温度',
               '距离有关', '地球距离', '白天长', '黑夜短', '夏天白天', '冬天白天', '日照'],
}
for theme, lst in UPD.items():
    m = re.search(r'"%s":\s*\[[^\]]*\]' % theme, src)
    assert m, theme
    new = '"%s": [%s]' % (theme, ", ".join('"%s"' % t for t in lst))
    src = src[:m.start()] + new + src[m.end():]

open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK:", {k: len(v) for k, v in UPD.items()})
