# -*- coding: utf-8 -*-
"""历史错题回溯集：v61/v62/v64 触发词缺口错题（补丁前曾 MISS，应已修复）"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
ITEMS = [
    # v61 的 6 个错题
    {"q": "伞为什么能挡住雨？", "domain": "下雨打伞"},
    {"q": "睡多久合适？", "domain": "晚上睡觉"},
    {"q": "喝太烫的水有什么危害？", "domain": "开水晾凉"},
    {"q": "烧水能去掉什么？", "domain": "烧水去氯"},
    {"q": "果汁能代替水果吗？", "domain": "蔬果营养"},
    {"q": "待机也耗电吗？", "domain": "节水节电"},
    # v62 的 3 个错题
    {"q": "2月为什么只有28天？", "domain": "一年月数"},
    {"q": "星期是怎么来的？", "domain": "一周天数"},
    {"q": "为什么傍晚天空变红？", "domain": "天空蓝色"},
    # v64 的 2 个错题
    {"q": "生活里有哪些负反馈？", "domain": "负反馈"},
    {"q": "检测阳性就一定有病吗？", "domain": "贝叶斯推断"},
]
with open(r'D:\Program Files\2_ai\CommonTrustProtocol\tools\replay_hist_errors.json', 'w', encoding='utf-8') as f:
    json.dump(ITEMS, f, ensure_ascii=False, indent=1)
print('历史错题回溯集:', len(ITEMS), '题')
