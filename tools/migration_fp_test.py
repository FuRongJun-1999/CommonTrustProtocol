# -*- coding: utf-8 -*-
"""fp 级迁移测试：20 变体 → encode → fp 是否含'彩虹'term（路由表确定性覆盖）"""
import sys, os, json
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
import semantic_translate as _st

VARIANTS = [
    "为什么下雨过后天上会挂彩色的桥？",
    "雨停了为什么能看到七色的光带？",
    "天空那道七彩的弧是什么？",
    "为什么有时候下完雨看不到那道彩带？",
    "天上那道七彩桥是实体吗？",
    "喷泉边那道彩色光圈是什么？",
    "那道七色的光弧为什么是弯的？",
    "下完雨天空的彩色光带是什么原理？",
    "为什么雨后的天空会出现七彩的光环？",
    "谁在天上画了那道七色彩带？",
    "阳光穿过水雾为什么会有彩色？",
    "雨后的光弧怎么才能看到？",
    "那道彩色弧线能走到下面去吗？",
    "为什么七彩的光带只在太阳在背后时出现？",
    "天空的彩色圆弧是怎么来的？",
    "为什么水汽能变出彩色的桥？",
    "那道七彩的带子是实物吗？",
    "雨后什么时候最容易见到那道彩弧？",
    "光穿过水滴为什么会变出颜色？",
    "彩色的光弧为什么是圆的不是直的？",
]

hits = 0
print("=== fp 路由表覆盖（彩虹簇）===")
for i, q in enumerate(VARIANTS, 1):
    fp = _st.encode(q)
    rainbow = "彩虹" in fp
    if rainbow:
        hits += 1
    trigs = [t for t in _st.DOMAIN_SYNONYM_CLUSTERS.get("彩虹", []) if t in q]
    print(f"[{'✓' if rainbow else '✗'}] {q[:22]} | fp含彩虹={rainbow} | 命中触发词={trigs}")
print(f"\n=== fp 路由命中: {hits}/{len(VARIANTS)} ({hits/len(VARIANTS)*100:.0f}%) ===")
print("彩虹簇触发词:", _st.DOMAIN_SYNONYM_CLUSTERS.get("彩虹"))
