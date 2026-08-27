# -*- coding: utf-8 -*-
"""查当前自进化后表状态 + 剩余未收敛变体"""
import sys, json
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
import semantic_translate as _st

themes = ["彩虹", "黑色吸热", "雷声闪电", "瓶外水珠", "饺子浮起", "切洋葱",
          "吸管吸饮料", "泡泡彩色", "热水瓶保温", "煮鸡蛋"]
for t in themes:
    trigs = _st.DOMAIN_SYNONYM_CLUSTERS.get(t, [])
    noise = [x for x in trigs if "的时候" in x or "候" in x or "时" in x]
    print(f"{t} ({len(trigs)}): {'NOISE: ' + str(noise) if noise else 'clean'}")
