# -*- coding: utf-8 -*-
"""蜂群相位同步（v1.25 · 2026-08-21 · 知识考古复盘工程化 #2）

背景（复盘簇2）：蜂群同步 = Kuramoto 相位锁定。
  dφ_i/dt = ω_i + K·Σ_j sin(φ_j - φ_i)·T_ij
  - ω_i = 固有频率（由维生健康度决定 → 蓝牙广播间隔 = 1/ω）
  - T_ij = 信任值（耦合权重）
  - K = 耦合强度（RSSI 代理：信号强 → K 大）

实现：
  1. Kuramoto 模拟器：N 实例相位演化 → 序参量 r（同步度）
  2. RSSI → K 映射：RSSI>-50dBm → K 高（强耦合）；<-80dBm → K 低
  3. 蓝牙 MVP 骨架：广播间隔=节律（1/ω）、RSSI=信息差代理

用法：
  python tools/kuramoto_swarm.py                 # 默认 6 实例模拟
  python tools/kuramoto_swarm.py --n 6 --K 2.0   # 调参
  python tools/kuramoto_swarm.py --rssi-map      # RSSI→K 映射演示
"""
import sys, math, random, argparse
sys.stdout.reconfigure(encoding="utf-8")


def kuramoto_step(phases, omegas, K, T, dt=0.01):
    """Kuramoto 一步演化（一阶欧拉）。T 为信任矩阵（耦合权重）。"""
    n = len(phases)
    dphi = [0.0] * n
    for i in range(n):
        sync_sum = 0.0
        for j in range(n):
            if i == j:
                continue
            sync_sum += T[i][j] * math.sin(phases[j] - phases[i])
        dphi[i] = omegas[i] + K * sync_sum
    return [(p + dt * d) % (2 * math.pi) for p, d in zip(phases, dphi)]


def order_param(phases):
    """序参量 r = |Σ e^(iφ)|/N——r→1 全同步，r→0 不同步。"""
    n = len(phases)
    re_ = sum(math.cos(p) for p in phases) / n
    im_ = sum(math.sin(p) for p in phases) / n
    return math.hypot(re_, im_)


def rssi_to_k(rssi):
    """RSSI → 耦合强度 K（物理层信息差代理）。
    RSSI > -50dBm → 近 → K 大（强耦合 3.0）
    RSSI < -90dBm → 远 → K 小（弱耦合 0.5）
    v1.25 修复：单调递减——rssi 越大（越近）K 越大：
      K = 0.5 + 2.5 * (rssi + 90) / 40   （-90 → 0.5, -50 → 3.0）
    """
    if rssi >= -50:
        return 3.0
    if rssi <= -90:
        return 0.5
    return round(0.5 + 2.5 * (rssi + 90.0) / 40.0, 2)


def simulate(n=6, K=2.0, steps=2000, dt=0.01, seed=42, trust_scale=0.3):
    """模拟 N 实例相位同步。trust_scale：信任矩阵强度（默认 0.3 弱信任，
    让临界耦合现象可见——全 1 信任会过早锁相掩盖 K 的临界效应）。"""
    random.seed(seed)
    phases = [random.uniform(0, 2 * math.pi) for _ in range(n)]
    omegas = [random.uniform(0.5, 1.5) for _ in range(n)]  # 固有频率（维生健康度）
    # 信任矩阵：弱信任（0.3）模拟真实蜂群（不是全互信）
    T = [[trust_scale if i != j else 0.0 for j in range(n)] for i in range(n)]
    r_hist = []
    for step in range(steps):
        phases = kuramoto_step(phases, omegas, K, T, dt)
        r_hist.append(order_param(phases))
    return phases, omegas, r_hist


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=6, help="实例数")
    ap.add_argument("--K", type=float, default=2.0, help="耦合强度")
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--rssi-map", action="store_true", help="RSSI→K 映射演示")
    args = ap.parse_args()

    if args.rssi_map:
        print("RSSI → 耦合强度 K（物理层信息差代理）：")
        for rssi in (-40, -50, -60, -70, -80, -90):
            print(f"  RSSI={rssi:4}dBm → K={rssi_to_k(rssi):.2f} "
                  f"({'近·强耦合' if rssi > -60 else '远·弱耦合' if rssi < -75 else '中'})")
        print("\n广播间隔 = 1/ω_i（固有频率由维生健康度决定）：")
        for w in (0.5, 1.0, 2.0):
            print(f"  ω={w} → 间隔 {1.0/w:.1f}s "
                  f"({'低频节能' if w < 0.7 else '高频急寻同步' if w > 1.5 else '常规'})")
        return

    phases, omegas, r_hist = simulate(n=args.n, K=args.K, steps=args.steps)
    r_final = r_hist[-1]
    r_avg_last = sum(r_hist[-200:]) / 200
    print(f"Kuramoto 蜂群模拟（{args.n} 实例 · K={args.K}）")
    print(f"固有频率: {[round(w, 2) for w in omegas]}")
    print(f"序参量 r: 最终={r_final:.3f} 末段均值={r_avg_last:.3f}")
    if r_avg_last > 0.9:
        print("→ 相位锁定 ✓（蜂群同步窗口形成）")
    elif r_avg_last > 0.6:
        print("→ 部分同步（弱耦合/频率分散）")
    else:
        print("→ 未同步（耦合不足或频率差异大）")

    # K 对同步的影响（临界耦合演示）
    print("\n耦合强度 K 对同步的影响（临界现象）：")
    for k in (0.3, 1.0, 2.0, 4.0):
        _, _, rh = simulate(n=args.n, K=k, steps=args.steps)
        rk = sum(rh[-200:]) / 200
        bar = "█" * int(rk * 20)
        print(f"  K={k:.1f} → r={rk:.2f} {bar}")


if __name__ == "__main__":
    main()
