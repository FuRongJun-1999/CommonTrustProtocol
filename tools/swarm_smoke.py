# -*- coding: utf-8 -*-
"""swarm_smoke.py · 蜂群协议栈+语言栈一键冒烟（2026-08-29 心跳）

联调前一键回归：汇总运行协议栈（M1/M2/M3）、语言栈（V-P/T4/编译器）、
浏览器栈全部测试，输出统一判定。
用法：python tools/swarm_smoke.py
"""
import subprocess, sys, os

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

SUITE = [
    ("M1 批次1 协议/总线/四态协商", "test_swarm_m1.py"),
    ("M1 批次2 互验证闭环", "test_swarm_m1_v2.py"),
    ("M2 桥接 固化进灵枢记忆", "test_swarm_m2_bridge.py"),
    ("M2 增量同步 gap 驱动", "test_swarm_m2_sync.py"),
    ("M3 信任分 三性质", "test_swarm_m3_trust.py"),
    ("M3×M1 集成 信任决定分工", "test_swarm_trust_integration.py"),
    ("dsh 接入指南合规性", "test_swarm_dsh_guide.py"),
    ("M1 真实接入联调彩排（跨进程）", "test_swarm_rehearsal.py"),
    ("编排层批1 能力目录+职责协商", "test_swarm_orchestrator.py"),
    ("语言栈 V-P1~P4", "test_mini_python_vp.py"),
    ("语言栈 T4 增强族", "test_mini_python_t4.py"),
    ("语言栈 P 线自举单元库", os.path.join("..", "aeis", "wisdom", "test_python_self_bootstrap.py")),
    ("编译器管线", "test_mini_compiler.py"),
    ("浏览器 F1/F2", "test_mini_browser_v1.py"),
    ("浏览器 F3/F4", "test_mini_browser_v2.py"),
    ("浏览器 F5/F6", "test_mini_browser_v3.py"),
]

total_p = total_f = 0
failed = []
for name, script in SUITE:
    p = os.path.join(HERE, script)
    r = subprocess.run([sys.executable, p], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    out = (r.stdout or "") + (r.stderr or "")
    line = next((l for l in out.splitlines()
                 if ("验证用例:" in l or "增强族:" in l or "管线测试:" in l
                     or "机制）:" in l)), "")
    ok = r.returncode == 0
    mark = "✔" if ok else "✘"
    print(f"[{mark}] {name:。<30} {line.strip() or ('exit=' + str(r.returncode))}")
    total_p += 1 if ok else 0
    total_f += 0 if ok else 1
    if not ok:
        failed.append((name, out[-300:]))

print("\n=== 蜂群全栈冒烟判定 ===")
if not failed:
    print(f"ALL PASS（{total_p}/{total_p + total_f} 套件）——联调就绪")
sys.exit(0 if not failed else 1)
