# -*- coding: utf-8 -*-
"""c12 触发词补丁：7 个 MISS 簇 + 4 个非精准命中簇补 DOMAIN 触发词
（encode 是连续子串匹配——触发词必须是问法里连续出现的短语）
规则：只做并集，不删已有触发词；先扫描确认每 key 仅 1 处定义"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

SRC = r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py'
src = open(SRC, encoding='utf-8').read()

# 重复 key 扫描（防覆盖 bug）
for k in ['下雨打伞','洗澡降温','晚上睡觉','吃早饭','垃圾入桶','烧水去氯','冬天穿衣',
          '开水晾凉','窗户起雾','夏天出汗','节约用水']:
    n = len(re.findall('"' + re.escape(k) + r'"\s*:', src))
    print(f'扫描 {k}: {n} 处定义')
    assert n == 2, f'{k} 定义数异常: {n}'  # DOMAIN + REVERSE_DAILY

# 新增触发词（问法变体 + 关键名词，必须能在常见问法里连续出现）
NEW_TRIGGERS = {
    '下雨打伞': ['下雨天要打伞','下雨天为什么要打伞','为什么下雨要打伞','下雨要打伞吗',
                '打伞','雨伞','淋雨','淋湿','伞能挡雨','打伞挡雨'],
    '洗澡降温': ['冲凉','冲凉降温','洗澡降温','夏天冲凉','洗澡能降温','冲凉能降温',
                '洗澡降温吗','冲凉舒服'],
    '晚上睡觉': ['为什么要晚上睡觉','为什么晚上要睡觉','晚上为什么要睡觉','晚上要睡觉吗',
                '早睡','睡觉的好处'],
    '吃早饭': ['为什么吃早饭','早饭重要','吃早餐','早餐重要吗','为什么吃早餐','早饭要吃饱'],
    '垃圾入桶': ['为什么要垃圾分类','垃圾要入桶','乱扔垃圾','垃圾分类入桶','垃圾为什么要分类',
                '乱丢垃圾'],
    '烧水去氯': ['水要烧开','烧开了喝','要烧开喝','水烧开喝','烧开喝','水要烧开喝',
                '为什么要烧开水'],
    '冬天穿衣': ['穿厚衣服','穿厚点','多穿衣服','穿衣服保暖','为什么天冷要穿衣','天冷多穿'],
    '开水晾凉': ['要晾凉','晾凉再喝','开水为什么要晾凉','晾凉喝','开水晾凉吗','水要晾凉'],
    '窗户起雾': ['窗户起雾','玻璃起雾','为什么起雾','起雾怎么办','怎么除雾','车窗起雾'],
    '夏天出汗': ['夏天出汗','天热出汗','为什么夏天出汗','出汗多','为什么天热出汗','夏天为什么出汗'],
    '节约用水': ['节约用水','为什么要节水','怎么节水','省水','为什么要节约用水','节约用水吗'],
}

# 定位 DOMAIN_SYNONYM_CLUSTERS 中的 key 定义并追加触发词
lines = src.splitlines(keepends=True)
out = []
changed = []
i = 0
while i < len(lines):
    ln = lines[i]
    m = re.match(r'^(\s*)"([^"]+)"\s*:\s*\[', ln)
    if m and m.group(2) in NEW_TRIGGERS:
        key = m.group(2)
        # 收集该 key 的列表元素（多行或单行）
        # 合并后续行直到 ] 结束
        buf = ln
        j = i + 1
        while ']' not in buf and j < len(lines):
            buf += lines[j]
            j += 1
        # 提取现有元素
        elems = re.findall(r'"([^"]+)"', buf)
        add = [t for t in NEW_TRIGGERS[key] if t not in elems]
        if add:
            # 重建列表行
            indent = m.group(1)
            newbuf = indent + '"' + key + '": ['
            all_elems = elems + add
            # 保持每行 5 个元素风格
            rows = [all_elems[k:k+5] for k in range(0, len(all_elems), 5)]
            for r_i, row in enumerate(rows):
                if r_i == 0:
                    newbuf += ', '.join('"' + e + '"' for e in row)
                else:
                    newbuf = newbuf.rstrip() + ',\n' + indent + '    ' + ', '.join('"' + e + '"' for e in row)
            newbuf += '],\n'
            out.append(newbuf)
            i = j
            changed.append((key, len(elems), len(all_elems)))
            continue
    out.append(ln)
    i += 1

open(SRC, 'w', encoding='utf-8').write(''.join(out))
for k, old_n, new_n in changed:
    print(f'OK {k}: 触发词 {old_n} -> {new_n}')
if not changed:
    print('无变更')
