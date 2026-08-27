# -*- coding: utf-8 -*-
"""精确清理：只删矛盾类自进化 patch 的噪声（从 added 报告人工核对的精确黑名单）"""
import re, sys
sys.stdout.reconfigure(encoding="utf-8")
TRANSLATE_PY = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(TRANSLATE_PY, encoding="utf-8").read()

# 精确噪声黑名单（本轮矛盾类自进化产生，人工终裁确认）
NOISE = {
    "学习游戏趣味": ["学不", "习室"],
    "学习枯燥": ["习时学不"],
    "拖延启动": ["复习时拖", "复习时拖延", "习时拖延"],
    "学习意义": ["失业时学习", "失业时读书", "失业时学", "年时学习", "年时读书", "用不", "还要", "要学"],
    "知识乐趣": ["么带孩子", "带孩子时", "带孩子时读书", "带孩"],
    "游戏机制": ["周末时游戏", "睡前时游戏", "周末时游", "末时游戏", "停不", "直玩"],
    "游戏责任": ["孩子时游戏", "学生时游戏", "家长时游戏", "不住"],
    "学习娱乐平衡": ["周末时学习", "备考时学习", "备考时游戏", "周末时学", "学一", "玩一"],
    "瓶外水珠": ["么冰箱拿"],
}

lines = src.split("\n")
removed = []
for i, line in enumerate(lines):
    m = re.match(r'^(\s*"([^"]+)"):\s*\[(.*)\],?\s*$', line)
    if not m:
        continue
    key, body = m.group(2), m.group(3)
    ban = NOISE.get(key)
    if not ban:
        continue
    items = [x.strip() for x in body.split(",") if x.strip()]
    clean_items = []
    for it in items:
        t = it.strip('"').strip("'")
        if t in ban:
            removed.append((key, t))
        else:
            clean_items.append(it)
    if len(clean_items) != len(items):
        lines[i] = f'{m.group(1)}: [{", ".join(clean_items)}],'
src = "\n".join(lines)
open(TRANSLATE_PY, "w", encoding="utf-8").write(src)
print("removed:", len(removed))
for k, t in removed:
    print("  ", k, "->", t)
