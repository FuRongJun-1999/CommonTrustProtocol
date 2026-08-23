# -*- coding: utf-8 -*-
"""c13 修复：①恢复 DOMAIN_ROUTE（短路/应力/混凝土钢筋→工程学）②RD['应力'] 升级 ③补触发词"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

SRC = r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py'
src = open(SRC, encoding='utf-8').read()
lines = src.splitlines(keepends=True)

# ---- 1. 恢复 DOMAIN_ROUTE ----
fixed1 = False
for i, ln in enumerate(lines):
    if '"应力": "什么是应力、应力有什么作用' in ln:
        indent = ln[:len(ln) - len(ln.lstrip())]
        lines[i] = indent + '"短路": "工程学", "应力": "工程学", "混凝土钢筋": "工程学",\n'
        fixed1 = True
        print(f'[1] DOMAIN_ROUTE 恢复 (line {i+1})')
        break
if not fixed1:
    print('[1] !! DOMAIN_ROUTE 污染行未找到')

# ---- 2. RD['应力'] 升级 ----
STRESS_NEW = "什么是应力、应力有什么作用，是『应力』vs『内力分布』的矛盾——应力（是单位面积上（承受的内力）、应力=力÷面积（F/A）、单位（帕斯卡Pa）、应力（分（拉应力/压应力/剪应力）、材料（承受应力（有极限（强度）、应力（超过强度（材料破坏）——应力的真相：应力=单位面积上的内力（F/A）、单位Pa、分拉压剪三种、材料强度=能承受的最大应力、设计要（应力<许用应力（才安全）、应力集中（孔洞尖角处应力大（要避免）。真相：①什么是应力——定义：物体（受力（内部（产生内力）、内力（分布（在截面上）、应力（=内力÷截面面积）、公式（σ=F/A）、单位（帕斯卡Pa（N/m²）、应力（描述（材料受力程度）——应力=力/面积（单位面积承受的内力（σ=F/A；②应力分几种——应力类型：拉应力（拉伸（材料被拉长）、压应力（压缩（材料被压短）、剪应力（剪切（材料被错开）、弯曲（梁内（上压下拉）、扭转（轴内（剪切应力）、不同类型（材料表现不同）——拉压剪三种基本应力（弯曲扭转是组合；③应力大了会怎样——强度极限：每种材料（能承受的（应力有限）、强度（=材料能承受的（最大应力）、应力（超过强度（材料破坏（断裂/压溃）、安全设计（应力（远小于（材料强度）、安全系数（留余量（防意外）——应力超强度（材料破坏（设计留安全系数；④什么是应力集中——应力集中：构件（有孔洞/尖角/台阶（局部应力（变大）、应力集中（局部应力（几倍于平均应力）、裂纹（从应力集中处（开始）、设计（避免（尖角（用圆角过渡）、应力集中（是（破坏的起点）——孔洞尖角应力集中（局部应力大（裂纹起点（圆角过渡；⑤应力在哪用到——工程应用：桥梁（承重（梁内应力）、楼房（柱子（压应力）、飞机（机翼（弯曲应力）、机械零件（转轴（应力）、设计（计算应力（选材料（定尺寸）、应力分析（是（工程基础）——桥梁楼房机械（处处有应力（设计要算应力。误区提醒：以为应力是力（应力是单位面积上的力）；以为应力越大越好（超过强度就破坏）；以为应力只在大结构里有（小零件也有）。总结：应力是材料受力的度量——单位面积上的内力，分拉压剪三种，材料能承受的最大应力是强度，设计必须让工作应力小于许用应力并留安全系数，应力集中是破坏起点要避免。"
fixed2 = False
for i, ln in enumerate(lines):
    if re.search(r'"应力"\s*:\s*"物体单位面积上承受的内力叫应力"', ln):
        indent = ln[:len(ln) - len(ln.lstrip())]
        lines[i] = indent + '"应力": "' + STRESS_NEW + '",\n'
        fixed2 = True
        print(f'[2] RD[应力] 升级 (line {i+1})')
        break
if not fixed2:
    print('[2] !! RD[应力] 旧行未找到')

src = ''.join(lines)

# ---- 3. 补触发词 ----
NEW_TRIGGERS = {
    '一年月数': ['一年有12个月', '为什么一年有12个月', '一年十二个月', '一年几个月'],
    '一天小时': ['一天有多少个小时', '一天有多少个钟头', '一天24小时', '一天多少个小时'],
    '混凝土钢筋': ['混凝土要加钢筋', '为什么混凝土要加钢筋', '加钢筋', '钢筋混凝土'],
    '介质': ['声音需要介质', '需要介质', '为什么声音需要介质', '传声介质', '声音靠什么传播'],
}
lines = src.splitlines(keepends=True)
out = []
changed = []
i = 0
while i < len(lines):
    ln = lines[i]
    m = re.match(r'^(\s*)"([^"]+)"\s*:\s*\[', ln)
    if m and m.group(2) in NEW_TRIGGERS:
        key = m.group(2)
        buf = ln
        j = i + 1
        while ']' not in buf and j < len(lines):
            buf += lines[j]
            j += 1
        elems = re.findall(r'"([^"]+)"', buf)
        add = [t for t in NEW_TRIGGERS[key] if t not in elems]
        if add:
            indent = m.group(1)
            newbuf = indent + '"' + key + '": ['
            all_elems = elems + add
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
src = ''.join(out)
for k, old_n, new_n in changed:
    print(f'[3] OK {k}: 触发词 {old_n} -> {new_n}')

open(SRC, 'w', encoding='utf-8').write(src)
print('已写回')
