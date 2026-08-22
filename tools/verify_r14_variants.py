# -*- coding: utf-8 -*-
"""round14 LLM 变异 vs 清理后簇——真实迁移率"""
import sys, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
importlib.reload(st)

qs = {
    "燃烧": [
        "为什么木头点燃后要烧很久才能烧完？",
        "为什么用锅盖盖住火就能灭？",
        "为什么火堆一吹反而烧得更旺？",
        "为什么蜡烛能一直烧？",
    ],
    "溶解": [
        "为什么热水里糖化得更快？",
        "为什么盐像那样化掉？",
        "冰块掉进水里，到底是化了还是溶进去了？",
        "为什么泡枸杞要用热水？",
    ],
    "汽水气泡": [
        "为什么我打开汽水时会有很多气泡冒出来？",
        "为什么放了一天的汽水就不冒泡了？",
        "为什么摇晃一下汽水就会喷出来？",
        "为什么刚买的汽水很爽，放久了就没气了？",
        "为什么冰镇后汽水的气泡更丰富？",
        "为什么碳酸饮料放久了没味道？",
        "为什么我喝完可乐肚子会咕噜响？",
    ],
    "血液循环": [
        "熬夜后第二天总觉得头晕乏力，是怎么回事？",
        "每次跑完步心跳好半天才恢复正常，正常吗？",
        "老年人手脚总是冰凉，是不是身体有问题？",
        "压力大时总觉得胸闷气短，心脏是不是累了？",
        "久坐不动的人更容易犯困，为什么？",
        "中年人体检说血压偏高，平时该怎么注意？",
        "经常加班熬夜的人，心脏能扛得住吗？",
        "运动员心跳慢，是不是比普通人更健康？",
    ],
}
total_ok = total = 0
for theme, lst in qs.items():
    ok = sum(1 for q in lst if theme in st.encode(q))
    total_ok += ok; total += len(lst)
    print(f"{theme}: {ok}/{len(lst)}")
print(f"--- total {total_ok}/{total} ---")
