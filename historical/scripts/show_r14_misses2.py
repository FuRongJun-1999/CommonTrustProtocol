# -*- coding: utf-8 -*-
import sys, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
importlib.reload(st)

qs = {
    "燃烧": ["为什么木头点燃后要烧很久才能烧完？", "为什么用锅盖盖住火就能灭？", "为什么火堆一吹反而烧得更旺？", "为什么蜡烛能一直烧？"],
    "溶解": ["为什么热水里糖化得更快？", "为什么盐像那样化掉？", "冰块掉进水里，到底是化了还是溶进去了？", "为什么泡枸杞要用热水？"],
}
for theme, lst in qs.items():
    print(f"--- {theme} ---")
    for q in lst:
        fp = st.encode(q)
        hit = theme in fp
        keys = [k for k in fp if k in st.REVERSE_DAILY]
        print(f"  {'HIT' if hit else 'MISS'} {q[:24]}")
        print(f"    fp={keys}")
