# -*- coding: utf-8 -*-
"""c7 触发词补盲：层面/运动后要喝水/走路能减肥"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

UPD = {
    "社会主义核心价值观": ['社会主义核心价值观', '核心价值观', '24字', '富强民主', '爱国敬业', '价值观', '核心价值',
                        '国家层面', '社会层面', '个人层面', '层面是什么', '三个层面'],
    "运动补水": ['运动后喝水', '出汗喝水', '出汗后喝水', '补水', '出汗后要喝水', '运动出汗喝水', '运动补水', '电解质', '运动饮料', '补水时机', '水中毒',
               '运动后要喝水', '运动后为什么喝水', '运动完喝水'],
    "跑步走路": ['跑步和走路', '跑步还是走路', '走路还是跑步', '跑步走路', '跑步消耗', '走路消耗', '哪个消耗大', '跑步伤膝盖', '快走',
               '走路能减肥', '走路减肥', '跑步能减肥', '跑步减肥'],
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
