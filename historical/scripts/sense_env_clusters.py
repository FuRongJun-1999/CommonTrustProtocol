# -*- coding: utf-8 -*-
"""感知：检查语义文件是否已有 碳中和/碳达峰/温室效应/全球变暖 等环境常识簇"""
import sys, importlib
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.semantic_translate as st
importlib.reload(st)

for k in ['碳中和', '碳达峰', '温室效应', '全球变暖', '碳排放', '温室气体', '气候变化',
          '新能源', '可再生能源', '光伏', '风力发电', '电动汽车', '锂电池', '储能',
          '绿色能源', '双碳']:
    in_rd = k in st.REVERSE_DAILY
    in_dom = k in st.DOMAIN_SYNONYM_CLUSTERS
    in_syn = k in st.SYNONYM_CLUSTERS
    print(f'{k}: RD={in_rd} DOMAIN={in_dom} SYNONYM={in_syn}')
