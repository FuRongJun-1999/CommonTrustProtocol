# -*- coding: utf-8 -*-
"""环境常识域建簇 v2：16 个缺失主题建 DOMAIN 触发词 + DOMAIN_ROUTE 域映射
（锚点修正：括号深度匹配 DOMAIN_SYNONYM_CLUSTERS 字典闭合位置，在其内插入）"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

SRC = r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py'
src = open(SRC, encoding='utf-8').read()

NEW_CLUSTERS = {
    '碳中和': ['碳中和', '什么是碳中和', '碳中和是什么', '净零排放', '碳中和怎么实现', '碳中和目标'],
    '碳达峰': ['碳达峰', '什么是碳达峰', '碳达峰是什么', '碳达峰目标', '碳达峰碳中和'],
    '温室效应': ['温室效应', '什么是温室效应', '温室效应是什么', '温室效应原因', '温室效应危害', '地球变暖原因'],
    '全球变暖': ['全球变暖', '什么是全球变暖', '全球变暖是什么', '气候变暖', '地球在变暖', '全球变暖危害'],
    '碳排放': ['碳排放', '什么是碳排放', '碳排放是什么', '碳排放量', '碳排放减少', '碳足迹'],
    '温室气体': ['温室气体', '什么是温室气体', '温室气体有哪些', '二氧化碳排放', '甲烷排放', '二氧化碳'],
    '气候变化': ['气候变化', '什么是气候变化', '气候变暖', '气候异常', '气候在变化'],
    '新能源': ['新能源', '什么是新能源', '新能源有哪些', '新能源车', '清洁能源'],
    '可再生能源': ['可再生能源', '什么是可再生能源', '可再生资源', '清洁能源', '绿色能源', '可再生能源有哪些'],
    '光伏': ['光伏', '光伏发电', '太阳能发电', '太阳能板', '光伏是什么', '光伏电池'],
    '风力发电': ['风力发电', '风能发电', '风力发电机', '风电', '风车发电', '风力发电原理'],
    '电动汽车': ['电动汽车', '电动车', '新能源车', '电动汽车原理', '电动汽车充电', '电动车电池'],
    '锂电池': ['锂电池', '锂离子电池', '电池原理', '锂电池充电', '锂电池寿命', '电池容量'],
    '储能': ['储能', '储能技术', '储能电池', '能量存储', '储能电站', '储能是什么'],
    '绿色能源': ['绿色能源', '什么是绿色能源', '清洁能源', '可再生能源', '绿色电力'],
    '双碳': ['双碳', '双碳目标', '碳达峰碳中和', '双碳政策', '3060目标'],
}


def find_dict_end(src, dict_name):
    """找 dict_name = { 的字典闭合 '}' 位置（括号深度匹配）"""
    i = src.find(dict_name + ' = {')
    assert i >= 0, f'{dict_name} 未找到'
    depth = 0
    j = src.find('{', i)
    for k in range(j, len(src)):
        c = src[k]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return k
    raise RuntimeError(f'{dict_name} 闭合未找到')


# 1. DOMAIN_SYNONYM_CLUSTERS 内插入新簇
end = find_dict_end(src, 'DOMAIN_SYNONYM_CLUSTERS')
block = ''
for k, triggers in NEW_CLUSTERS.items():
    rows = [triggers[i:i+5] for i in range(0, len(triggers), 5)]
    lines_inner = [', '.join('"' + t + '"' for t in row) for row in rows]
    body = ',\n    '.join(lines_inner)
    block += f'    "{k}": [\n    {body}\n    ],\n'
src = src[:end] + '\n' + block + src[end:]

# 2. DOMAIN_ROUTE 域映射（先找 DOMAIN_ROUTE 字典闭合）
try:
    end_dr = find_dict_end(src, 'DOMAIN_ROUTE')
    dr_block = ''.join(f'    "{k}": "环境科学",\n' for k in NEW_CLUSTERS)
    src = src[:end_dr] + '\n' + dr_block + src[end_dr:]
except RuntimeError as e:
    print(f'DOMAIN_ROUTE 跳过: {e}')

open(SRC, 'w', encoding='utf-8').write(src)
print(f'已建簇: {len(NEW_CLUSTERS)} 个环境主题')

# 验证语法
import py_compile
py_compile.compile(SRC, doraise=True)
print('语法 OK')
