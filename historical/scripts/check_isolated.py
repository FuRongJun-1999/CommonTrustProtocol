# -*- coding: utf-8 -*-
"""检查生活常识孤立直答的簇归属"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
for k in ("刷牙护牙", "早睡早起", "煮饭原理", "开水烫", "晒太阳补钙", "开窗通风",
          "运动热身", "运动拉伸", "走路锻炼", "久坐活动", "用眼休息", "吹干头发",
          "热水解冻", "烧水去氯", "节约用水", "节水节电", "地球公转", "一年月数",
          "一天小时", "一周天数", "垃圾入桶", "喝水规律", "保暖防感冒", "睡前不玩",
          "饿了吃饭", "喝水止渴", "夏天出汗", "冬天穿衣"):
    in_dom = k in st.DOMAIN_SYNONYM_CLUSTERS
    in_syn = k in st.SYNONYM_CLUSTERS
    print(f"{k}: DOMAIN={in_dom} SYNONYM={in_syn}")
