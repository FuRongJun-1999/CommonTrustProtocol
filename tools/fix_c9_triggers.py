# -*- coding: utf-8 -*-
"""c9 触发词补盲：7 个缺口"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

UPD = {
    "电流方向": ['电流方向', '电流的方向', '电流怎么走', '电流方向是', '正电荷', '电子方向', '正极到负极', '从正极', '电流流向', '交流电直流电',
               '交流电', '直流电', '交流直流', 'AC DC', '方向交替'],
    "惯性": ['什么是惯性', '惯性是什么', '惯性定律', '惯性', '急刹车', '刹车前冲', '保持运动', '惯性是', '质量惯性',
            '急刹车人前冲', '人前冲', '惯性是力', '惯性不是力', '惯性大小'],
    "分子热运动": ['热水洗油污', '热水去油', '分子运动', '热运动', '分子热运动', '扩散', '温度高分子', '分子在动', '为什么热水去油',
                 '热水洗', '洗掉油污', '热水为什么', '去油污'],
    "水油密度": ['水和油', '油和水', '水油密度', '油浮在水', '油为什么浮', '密度', '水油不溶', '不相溶', '乳化', '油水',
                '判断沉浮', '怎么判断', '沉浮', '浮沉', '物体沉浮', '密度判断'],
    "声音传播": ['回声', '隔墙有耳', '声音传播', '声音在真空中', '声音能在真空中', '真空中能听到', '声音怎么传播', '声音靠介质', '真空传声', '声音速度', '声音快慢',
                '怎么传播', '声音是', '声音怎么', '介质传得', '传得快', '什么介质', '声音介质', '传声'],
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
