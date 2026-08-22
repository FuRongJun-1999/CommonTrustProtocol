# -*- coding: utf-8 -*-
"""c11 触发词补盲：叶子绿/秋天变黄/价值观会变/提高记忆/记忆睡眠"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

UPD = {
    "叶子绿色": ['叶子绿色', '叶子为什么绿', '叶子是绿的', '叶绿素', '为什么叶子绿', '叶子绿', '秋天变黄', '光合色素', '叶绿体',
               '叶子是绿色', '叶子绿色是', '为什么叶子是绿色', '叶子变黄', '变黄', '秋天叶子'],
    "价值观": ['价值观', '什么是价值观', '价值观是', '价值观有什么用', '价值观怎么形成', '价值观改变', '价值观和道德', '人生价值观',
              '价值观会变', '价值观会变吗', '价值观能变', '价值观形成'],
    "记忆": ['记忆', '什么是记忆', '记忆是', '记忆力', '提高记忆', '记忆方法', '遗忘', '艾宾浩斯', '记忆训练', '记忆力差', '怎么记住',
            '怎么提高记忆', '提高记忆力', '记忆和睡眠', '记忆睡眠', '记忆和遗忘'],
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
