# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

UPD = {
    "降落伞": ['降落伞', '跳伞', '降落', '慢慢落', '缓缓落下', '飘下来', '伞兵',
              '空中掉下来', '为什么跳伞', '安全落地', '空气阻力', '阻力',
              '小鸟摔不死', '摔不死', '从树上掉下来', '落得慢', '掉得比', '玩具伞',
              '从楼顶', '落得很慢', '小鸟从很高', '掉下来没事', '坠落'],
    "反射": ['镜子照人', '倒影', '反射', '镜子里', '照镜子', '平面镜', '镜中', '哈哈镜',
             '凸面镜', '凹面镜', '镜子为什么', '为什么镜子', '镜像是', '虚像', '水面倒影',
             '后视镜', '水中月亮', '镜中月亮', '倒影是', '手伸不进去', '摸不到',
             '看得到摸不到', '挥手'],
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
