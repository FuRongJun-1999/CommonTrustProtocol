# -*- coding: utf-8 -*-
"""round15 簇清理：降落伞/秋千/反射/蒸发 去掉提取碎片，保留有意义的自然词"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

PARA = ['降落伞', '跳伞', '降落', '慢慢落', '缓缓落下', '飘下来', '伞兵',
        '空中掉下来', '为什么跳伞', '安全落地', '空气阻力', '阻力',
        '小鸟摔不死', '摔不死', '从树上掉下来', '落得慢', '掉得比', '玩具伞']
SWING = ['秋千', '荡秋千', '荡起来', '越荡越高', '摆起来', '钟摆', '摆动',
         '来回摆', '摆一下', '为什么秋千', '荡高', '单摆', '能一直荡', '一直荡']
MIRROR = ['镜子照人', '倒影', '反射', '镜子里', '照镜子', '平面镜', '镜中', '哈哈镜',
          '凸面镜', '凹面镜', '镜子为什么', '为什么镜子', '镜像是', '虚像', '水面倒影',
          '后视镜', '水中月亮', '镜中月亮', '倒影是']
EVAP = ['晾干了', '晾干', '晾', '水干了', '晒干了', '晒干', '衣服干了', '衣服晾干',
        '干了', '蒸发', '蒸发了', '水蒸气', '干得快', '晾衣服', '蒸发是', '为什么会干',
        '水洒', '不见了', '水不见了', '洒地上', '地里的积水', '积水', '泳池的水',
        '汗干了', '身上干了']

for theme, lst in (("降落伞", PARA), ("秋千", SWING), ("反射", MIRROR), ("蒸发", EVAP)):
    m = re.search(r'"%s":\s*\[[^\]]*\]' % theme, src)
    assert m, theme
    new = '"%s": [%s]' % (theme, ", ".join('"%s"' % t for t in lst))
    src = src[:m.start()] + new + src[m.end():]

open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK:", {k: len(v) for k, v in (("降落伞", PARA), ("秋千", SWING), ("反射", MIRROR), ("蒸发", EVAP))})
