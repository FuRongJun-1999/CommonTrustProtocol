# -*- coding: utf-8 -*-
"""distill_condition_units.py · 知识库条件化（第四阶段·①）
REVERSE_DAILY（649 条完整答案）→ 蒸馏为「{条件链→规律片段}」条件单元骨架。
方法（白箱确定性）：从完整答案提取 条件词（气压/温度/密度/光照…）× 方向词
（降低/升高/变快/…）→ 生成 {条件→规律} 单元。转化率 = 可条件化的已升级簇比例。
"""
import sys, ast, json, os
sys.stdout.reconfigure(encoding='utf-8')

SITE = r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages'
ST = os.path.join(SITE, 'wisdom', 'semantic_translate.py')


def load_reverse_daily(path=ST):
    """ast 解析 semantic_translate.py 的 REVERSE_DAILY 字面量（不 import 免加载模型）"""
    tree = ast.parse(open(path, encoding='utf-8').read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == 'REVERSE_DAILY':
                    return ast.literal_eval(node.value)
    return {}


# 条件词表（知识适用的条件维度——从 compose_engine 条件维度扩展）
CONDITION_WORDS = [
    "气压", "温度", "湿度", "密度", "光照", "阳光", "重力", "摩擦", "压力",
    "面积", "速度", "浓度", "酸碱", "酸性", "碱性", "水分", "氧气", "二氧化碳",
    "热量", "能量", "电流", "电压", "电阻", "波长", "频率", "距离", "时间",
    "风", "海拔", "深度", "体积", "质量", "盐度", "糖分", "季节", "时间",
    "电解质", "催化剂", "酶", "磁力", "电场", "引力", "张力", "惯性", "杠杆",
    # 领域条件词（第四阶段扩充）
    "光", "声", "音", "电", "磁", "金属", "塑料", "木材", "水", "油", "糖",
    "盐", "维生素", "蛋白质", "细菌", "病毒", "细胞", "基因", "植物", "动物",
    "人类", "城市", "人口", "经济", "市场", "价格", "货币", "星球", "太阳",
    "月亮", "空气", "土壤", "海洋", "森林", "气候", "雨", "雪", "冰", "火山",
    "地震", "季节", "昼夜", "星球", "宇宙", "恒星", "行星", "轨道", "速度",
]

# 方向词表（规律方向——答案中体现的变化）
DIRECTION_WORDS = [
    "降低", "升高", "上升", "下降", "增大", "减小", "变大", "变小", "变快",
    "变慢", "加快", "减慢", "加速", "减速", "变硬", "变软", "变稠", "变稀",
    "融化", "凝固", "蒸发", "液化", "升华", "凝华", "沸腾", "结冰", "熔化",
    "浮", "沉", "亮", "暗", "更热", "更冷", "更快", "更慢", "更多", "更少",
    "膨胀", "收缩", "弯曲", "折射", "反射", "溶解", "沉淀", "氧化", "燃烧",
    "发光", "发热", "吸收", "释放", "增加", "减少", "加速反应", "减慢反应",
]

# 可解释性动词（答案中体现因果）
CAUSE_WORDS = ["因为", "所以", "导致", "由于", "原因", "因此", "→", "是"]

# 条件化结构词（「越…越…」「取决于」「随…而」是条件化的黄金信号）
CONDITIONAL_STRUCTURE = ["越", "取决于", "随", "而", "不同", "变化", "影响",
                         "决定", "与…有关", "跟…有关", "取决于"]


def distill_answer(answer):
    """从完整答案蒸馏 {条件→规律} 骨架：返回 (条件词, 方向词, 条件化结构)"""
    conds = [w for w in CONDITION_WORDS if w in answer]
    dirs = [w for w in DIRECTION_WORDS if w in answer]
    has_cause = any(w in answer for w in CAUSE_WORDS)
    has_structure = any(w in answer for w in CONDITIONAL_STRUCTURE)
    return conds, dirs, has_cause or has_structure


def distill_report(limit_keys=None):
    rd = load_reverse_daily()
    keys = list(rd.keys())
    if limit_keys:
        keys = keys[:limit_keys]
    results = []
    conditionable = 0
    for k in keys:
        ans = rd.get(k, "")
        conds, dirs, cause = distill_answer(ans)
        # 可条件化：≥1 条件词 +（≥1 方向词 OR 条件化结构词「越/取决于/随…而」）
        ok = len(conds) >= 1 and (len(dirs) >= 1 or cause)
        if ok:
            conditionable += 1
            results.append({"key": k, "conds": conds, "dirs": dirs,
                            "len": len(ans)})
    rate = conditionable / len(keys) if keys else 0
    return {"total": len(keys), "conditionable": conditionable,
            "rate": round(rate * 100, 1), "samples": results}


if __name__ == "__main__":
    print("=== 知识库条件化：REVERSE_DAILY 蒸馏分析 ===\n")
    r = distill_report()
    print(f"总簇: {r['total']} | 可条件化（含条件词+方向词）: {r['conditionable']}"
          f" = {r['rate']}%")
    print(f"判定⑤ 转化率 ≥80%: {'✔' if r['rate'] >= 80 else '✘'}")

    print("\n=== 条件化样本（前 8 条蒸馏骨架） ===")
    for s in r["samples"][:8]:
        print(f"  [{s['key']}] 条件={s['conds'][:4]} 方向={s['dirs'][:4]}"
              f"（{s['len']}ch）")

    # 输出 JSON 供后续生成条件单元
    out = {s["key"]: {"conds": s["conds"], "dirs": s["dirs"]}
           for s in r["samples"]}
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'distilled_condition_units.json'), 'w',
              encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"\n蒸馏骨架已存: tools/distilled_condition_units.json"
          f"（{len(out)} 条可条件化）")
