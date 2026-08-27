# -*- coding: utf-8 -*-
"""round13 LLM 变异 vs 清理后簇——真实迁移率"""
import sys, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
importlib.reload(st)

qs = {
    "感冒": [
        "为什么我换季的时候特别容易犯感冒？",
        "家里老人总是咳咳停不下来，是感冒还是别的？",
        "鼻子一塞就难受，感冒了是不是只能等它自己好？",
        "同事天天打喷嚏，我是不是也快被传染感冒了？",
        "幼儿园里小朋友老感冒，是不是免疫力差？",
    ],
    "光合作用": [
        "为什么天黑之后花草就不长了？",
        "为什么天热的时候草长得快？",
        "家里养的花为什么放客厅就枯了？",
        "晚上没太阳，花还能开吗？",
        "为什么摘下来的花放两天就蔫了？",
        "植物不吃东西靠什么活？",
        "植物吸收二氧化碳干什么用？",
    ],
    "遗传": [
        "爸爸的近视眼会传给孩子吗？",
        "双胞胎孩子性格为什么差这么多？",
        "为什么我头发是黑的，我儿子偏偏是黄的？",
        "两个健康的爸妈怎么会生出有病的孩子？",
        "孩子爱挑食是天生还是后天养成的？",
        "听说基因能决定身高，是真的吗？",
    ],
    "萌发": [
        "种子泡水里放一天，为什么还不冒芽啊",
        "春天种豆子，土干了几天它就不长了怎么办",
        "我的番茄种子埋土里两周了，怎么一点动静没有",
        "种子要不要晒太阳才能发芽，放屋里可以吗",
        "天太冷了种子还能不能发芽，要不要等暖和了",
        "泡水的种子到底泡多久合适，泡久了会烂吗",
    ],
}
total_ok = total = 0
for theme, lst in qs.items():
    ok = sum(1 for q in lst if theme in st.encode(q))
    total_ok += ok; total += len(lst)
    print(f"{theme}: {ok}/{len(lst)}")
print(f"--- total {total_ok}/{total} ---")
