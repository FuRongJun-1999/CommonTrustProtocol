# -*- coding: utf-8 -*-
"""矛盾关联映射生成：conflict_id → 关联矛盾（含语义说明）。

从 v3 linked 扩展为完整映射 + 人类可读的关联解释，供运行时
「相关矛盾」提示使用。
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

# 矛盾 id → 中文名 + 一句话冲突
CONFLICT_META = {
    "self-lazy": ("自我控制", "想努力 vs 控制不住玩手机"),
    "self-ideal": ("理想现实", "理想 vs 现实差距"),
    "self-procrast": ("拖延", "重要事 vs 拖着不做"),
    "self-compare": ("攀比", "别人过得好 vs 自己的节奏"),
    "fam-couple": ("夫妻协作", "付出 vs 不被看见"),
    "fam-gener": ("代际观念", "年轻人自主 vs 老人观念"),
    "fam-motherinlaw": ("婆媳相处", "小家庭主权 vs 婆婆介入"),
    "fam-eldercare": ("养老规划", "赡养责任 vs 资源有限"),
    "edu-score": ("应试压力", "全面发展 vs 分数筛选"),
    "edu-resource": ("教育公平", "资源集中 vs 公平分配"),
    "edu-doublecut": ("双减焦虑", "减负 vs 竞争不减"),
    "edu-tutor": ("补习班", "补课投入 vs 效果/抵触"),
    "teach-authority": ("师生权威", "老师权威 vs 学生质疑"),
    "teach-fair": ("师生公平", "偏爱优生 vs 放弃差生"),
    "teach-bully": ("校园霸凌", "孩子安全 vs 学校息事宁人"),
    "work-pay": ("薪酬公平", "干活多 vs 工资低"),
    "work-loyalty": ("跳槽", "忠诚 vs 跳槽发展"),
    "work-age35": ("中年危机", "经验价值 vs 年龄折价"),
    "work-layoff": ("裁员", "企业降本 vs 员工生存"),
    "work-burnout": ("工作压力", "任务无限 vs 时间有限"),
    "gov-reg": ("政企监管", "创新速度 vs 监管滞后"),
    "gov-subsidy": ("产业补贴", "扶持 vs 公平竞争"),
    "gov-platform": ("平台用工", "灵活就业 vs 权益保障"),
    "gov-carbon": ("碳中和", "环保成本 vs 企业利润"),
    "intl-tech": ("技术封锁", "领先者封锁 vs 追赶者自主"),
    "intl-trade": ("贸易摩擦", "贸易利益 vs 关税战"),
    "intl-energy": ("能源资源", "能源控制 vs 资源依赖"),
    "intl-climate": ("气候责任", "历史排放 vs 发展权"),
    "self-choice": ("选择决策", "理想 vs 稳定"),
    "social-boundary": ("拒绝边界", "合群 vs 做自己"),
    "relation-attach": ("依恋焦虑", "亲密 vs 独立"),
    "family-expect": ("家庭期望", "父母期望 vs 孩子自主"),
}

# 关联说明（一对矛盾 → 为什么关联）
LINK_NOTES = {
    ("fam-motherinlaw", "fam-couple"): "婆媳矛盾会渗入夫妻关系——丈夫夹中间，夫妻协作被婆婆介入打断",
    ("fam-motherinlaw", "fam-gener"): "婆媳冲突是代际观念冲突在家庭里的具体化",
    ("fam-eldercare", "fam-gener"): "养老分歧本质是代际责任观的冲突",
    ("fam-eldercare", "work-burnout"): "工作压力大时养老责任更难扛——双重负荷",
    ("edu-doublecut", "edu-score"): "双减焦虑源于应试压力没变、补课渠道变了",
    ("edu-tutor", "edu-score"): "补课是应试压力的产物——竞争不变，补课不止",
    ("edu-tutor", "edu-doublecut"): "双减后补习转入地下/私教，焦虑变形",
    ("teach-bully", "teach-fair"): "被霸凌的孩子往往是被忽视的边缘生——公平问题放大",
    ("teach-bully", "fam-couple"): "孩子被欺负的家庭，夫妻常因处理分歧争吵",
    ("work-age35", "work-loyalty"): "跳槽频繁可能加速中年危机（履历碎片化）",
    ("work-age35", "work-burnout"): "中年人的加班压力更高——上有老下有小",
    ("work-layoff", "work-age35"): "裁员优先裁35+——年龄与裁员直接相关",
    ("work-layoff", "work-pay"): "薪酬高的老员工是裁员目标——性价比逻辑",
    ("gov-platform", "gov-reg"): "平台用工乱象正是监管跟不上创新的例子",
    ("gov-platform", "work-pay"): "骑手没社保=劳动报酬权益缺失",
    ("gov-carbon", "gov-subsidy"): "碳中和产业靠补贴起步（新能源补贴）",
    ("gov-carbon", "intl-energy"): "碳中和改变能源格局——影响国际能源争夺",
    ("intl-energy", "intl-tech"): "稀土卡脖子=技术封锁的资源版",
    ("intl-energy", "gov-carbon"): "能源转型（碳中和）重塑国际能源权力",
    ("intl-climate", "gov-carbon"): "国内碳中和与国际减排责任同源",
    ("intl-climate", "intl-energy"): "气候谈判绕不开能源结构（谁排得多）",
    ("self-procrast", "self-lazy"): "拖延是自我控制失败的日常形态",
    ("self-procrast", "work-burnout"): "工作拖延→加班→更累→更拖延，恶性循环",
    ("self-compare", "self-ideal"): "攀比放大理想与现实的落差感",
    ("self-compare", "self-choice"): "看到别人选了稳定/理想，加重自己的纠结",
}

# 序列化为 JSON（供运行时加载）
out = {"conflicts": CONFLICT_META, "links": [
    {"a": k[0], "b": k[1], "note": v} for k, v in LINK_NOTES.items()]}
with open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\conflict_map.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(f"矛盾关联映射: {len(CONFLICT_META)} 矛盾, {len(LINK_NOTES)} 条关联")
for k, v in list(LINK_NOTES.items())[:6]:
    print(f"  {k[0]} <-> {k[1]}: {v[:40]}")
