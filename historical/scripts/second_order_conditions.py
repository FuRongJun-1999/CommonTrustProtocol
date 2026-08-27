# -*- coding: utf-8 -*-
"""second_order_conditions.py · 验证「二阶条件 = 条件交互 = 新条件发现」（GPT 第 7 点）
微积分进阶：
  一阶偏导 ∂f/∂x = 单条件影响（条件单元）
  二阶混合偏导 ∂²f/∂x∂y = 条件之间的关系（条件交互）：
    = 0 → 条件独立（可分离组合——组合引擎并行化）
    ≠ 0 → 条件组合（气压×温度 → 新规律——递归组合的数学基础）
意义：compose_recursive（递归组合）处理的正是 ∂²f/∂x∂y ≠ 0 的交互部分——
  认知结构增长：一阶=单条件，二阶=条件关系，三阶=复杂结构。
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')


# ============ 知识函数（含交互项）：沸点 = f(气压, 增压) ============
# f(P, S) = 100 + a·ΔP + b·S + c·ΔP·S
#   a = 气压效应（高原 ΔP<0 → 沸点降）
#   c = 交互系数（气压 × 增压 的组合效应——高压锅在高原）
def boiling_point(dP, S, a=-12.0, b=20.0, c=0.8):
    """沸点知识函数：dP=气压变化量，S=增压状态(0/1)，c=交互强度"""
    return 100.0 + a * dP + b * S + c * dP * S


# ============ 偏导计算（数值/解析） ============
def partial_f(f, var_idx, vals, h=1e-5):
    """数值偏导 ∂f/∂var"""
    v = list(vals)
    vp = list(vals); vp[var_idx] += h
    vm = list(vals); vm[var_idx] -= h
    return (f(*vp) - f(*vm)) / (2 * h)


def mixed_partial(f, i, j, vals, h=1e-5):
    """数值混合偏导 ∂²f/∂xi∂xj"""
    v = list(vals)
    pp = list(vals); pp[i] += h; pp[j] += h
    pm = list(vals); pm[i] += h; pm[j] -= h
    mp = list(vals); mp[i] -= h; mp[j] += h
    mm = list(vals); mm[i] -= h; mm[j] -= h
    return (f(*pp) - f(*pm) - f(*mp) + f(*mm)) / (4 * h * h)


if __name__ == "__main__":
    print("=== 验证：二阶条件 = 条件交互 = 新条件发现 ===\n")

    # ① 知识函数：沸点 = f(气压ΔP, 增压S) 含交互项 c·ΔP·S
    print("① 知识函数（含交互项）：沸点 = 100 + a·ΔP + b·S + c·ΔP·S")
    print("   a=-12（气压效应） b=+20（增压效应） c=0.8（交互强度）\n")

    # ② 一阶偏导 = 单条件影响（条件单元）
    base = (0.0, 0.0)  # 标准大气压、无增压
    dPd = partial_f(boiling_point, 0, base)
    dS = partial_f(boiling_point, 1, base)
    print("② 一阶偏导（单条件影响 = 条件单元）")
    print(f"   ∂沸点/∂气压 = {dPd:.2f}（气压降低1单位→沸点降12°C）")
    print(f"   ∂沸点/∂增压 = {dS:.2f}（增压→沸点升20°C）")

    # ③ 混合偏导 = 条件交互
    mix = mixed_partial(boiling_point, 0, 1, base)
    print("\n③ 二阶混合偏导 ∂²沸点/∂气压∂增压 = {:.2f}".format(mix))
    print(f"   ≠ 0 → 气压 × 增压 存在交互（高压锅在高原产生新规律）")

    # ④ 条件独立 vs 交互（c=0 时）
    def f_indep(dP, S, a=-12.0, b=20.0):
        return 100.0 + a * dP + b * S  # 无交互项
    mix0 = mixed_partial(f_indep, 0, 1, base)
    print("\n④ 对照：无交互项（c=0）→ 混合偏导 = {:.4f}".format(mix0))
    print(f"   = 0 → 气压与增压独立（可分离组合）")

    # ⑤ 交互的工程意义：高原×高压锅 = 递归组合的数学基础
    print("\n⑤ 交互的工程意义（高原 × 高压锅）")
    dP_plateau = -0.65  # 高原气压低（ΔP≈-0.65atm）
    # 一阶（独立假设，错）：沸点 = 100 + a·ΔP + b·S
    naive = f_indep(dP_plateau, 1.0)
    # 真实（含交互）：c·ΔP·S 修正
    real = boiling_point(dP_plateau, 1.0)
    print(f"   一阶独立近似: 沸点 = {naive:.1f}°C（漏了交互项）")
    print(f"   二阶修正:     沸点 = {real:.1f}°C（含 c·ΔP·S 交互）")
    print(f"   交互贡献 = {real - naive:.2f}°C（∂²f/∂x∂y≠0 的部分）")
    print(f"   → compose_recursive 递归组合处理的就是这部分："
          f"「高原(气压低)×高压锅(增压)→能煮熟」")

    # ⑥ 认知结构增长：一阶→二阶→三阶
    print("\n⑥ 认知结构增长（偏导阶数 = 结构深度）")
    print("   一阶（条件单元）: 单条件影响——气压↓→沸点↓")
    print("   二阶（条件组合）: 条件关系——气压×增压 交互（新条件发现）")
    print("   三阶（复杂结构）: 更高阶交互——预测误差自动条件化逐步补全")
    print("   → 学习 = 在条件空间中逐阶逼近知识函数（泰勒展开的认知版）")

    print("\n=== 结论 ===\n"
          "混合偏导 ∂²f/∂x∂y 判定条件独立/交互：\n"
          "  =0 → 条件可分离（组合引擎并行化）；≠0 → 需要组合条件单元\n"
          "  （递归组合的数学基础——高压锅在高原 = ∂²f/∂x∂y≠0 的部分）\n"
          "认知结构增长 = 偏导阶数：一阶单条件→二阶条件关系→三阶复杂结构\n"
          "误差→条件更新 = 泰勒展开的逐阶修正（寻找缺失项，非调参数）")
