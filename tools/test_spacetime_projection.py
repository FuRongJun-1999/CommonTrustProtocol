# -*- coding: utf-8 -*-
"""test_spacetime_projection.py · 2D↔3D 投影互校验测试（第五阶段·闭环时间维）
验证：①右移两视图一致 ②左移一致 ③静止一致 ④冲突检测（自校验抓错）"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from spacetime_projection import cross_validate, direction_map
from spacetime_3d import synth_moving_stereo_frames

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ① 右移：2D 向右 ↔ 3D x+，速度互验
r = cross_validate(synth_moving_stereo_frames(frames=10, speed_px=2, direction="right"))
check('①a 右移方向一致', r["ok"] and r["d2"] == "向右" and r["d3"] == "x+",
      f'2D={r["d2"]} 3D={r["d3"]}')
check('①b 右移速度互验', r["speed_err"] <= 0.30,
      f'3D×10={r["speed3"]*10:.2f} vs 2D={r["speed2"]} 误差={r["speed_err"]:.2%}')

# ② 左移：2D 向左 ↔ 3D x-
r = cross_validate(synth_moving_stereo_frames(frames=8, speed_px=2, direction="left"))
check('② 左移方向一致', r["ok"] and r["d2"] == "向左" and r["d3"] == "x-",
      f'2D={r["d2"]} 3D={r["d3"]}')

# ③ 静止：两侧静止
r = cross_validate(synth_moving_stereo_frames(frames=6, speed_px=0, direction="right"))
check('③ 静止两视图一致', r["ok"] and r["d2"] == "静止" and r["d3"] == "静止",
      f'2D={r["d2"]} 3D={r["d3"]}')

# ④ 冲突检测：方向映射表能识别错误（自校验抓错）
check('④a 映射抓错(向右↔x-)', not direction_map("向右", "x-"), '')
check('④b 映射抓错(向右↔z+)', not direction_map("向右", "z+"), '')
check('④c 映射正确(向左↔x-)', direction_map("向左", "x-"), '')

# ⑤ 映射全覆盖：2D 三态 × 3D 五态 无遗漏
all_pairs = {(d2, d3) for d2 in ("向右", "向左", "静止")
             for d3 in ("x+", "x-", "z+", "z-", "静止")}
covered = set(DIRECTION_MAP.keys()) if 'DIRECTION_MAP' in dir() else set()
from spacetime_projection import DIRECTION_MAP
covered = set(DIRECTION_MAP.keys())
check('⑤ 映射表覆盖全部组合', all_pairs == covered,
      f'缺: {all_pairs - covered} 多: {covered - all_pairs}')

print(f'\n=== 2D↔3D 投影互校验测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
