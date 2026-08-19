# -*- coding: utf-8 -*-
"""
灵枢×酒馆协议扩散 · 一键验证（离线自检）
========================================
跑通整条链路的离线验证，输出 PASS/FAIL 报告：
1. 角色卡规范校验（JSON + PNG）
2. 角色扮演引擎三导入接口（内存库）
3. 注入块组装完整性（锚点/价值观/条件空间）

用法：
    python selfcheck_diffusion.py

无需网络、无需真实上游——mock 替代，适合发布前自检。
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from aeis.roleplay import RolePlayEngine  # noqa: E402
from validate_card import validate  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))


def main() -> int:
    print("=== 灵枢×酒馆协议扩散 · 离线自检 ===\n")

    # ---------- 1. 角色卡规范校验 ----------
    print("[1] 角色卡规范校验（chara_card_v3）")
    base = Path(__file__).resolve().parent.parent / "release"
    for name in ("灵枢_协议引导者.json", "灵枢_协议引导者.png"):
        p = base / name
        if not p.exists():
            check(f"角色卡 {name}", False, "文件不存在")
            continue
        if p.suffix == ".png":
            import struct
            raw = p.read_bytes()
            json_str = ""
            pos = 8
            while pos < len(raw):
                (ln,) = struct.unpack(">I", raw[pos:pos+4])
                tag = raw[pos+4:pos+8]
                if tag == b"tEXt":
                    key, _, val = raw[pos+8:pos+8+ln].decode("utf-8").partition("\x00")
                    if key == "chara":
                        json_str = val
                        break
                pos += 12 + ln
            if not json_str:
                check(f"PNG 内嵌 {name}", False, "未找到 chara chunk")
                continue
            card = json.loads(json_str)
        else:
            card = json.loads(p.read_text(encoding="utf-8"))
        ok, errors = validate(card)
        check(f"角色卡 {name}", ok, "" if ok else "; ".join(errors))

    # ---------- 2. 引擎三导入接口 ----------
    print("\n[2] 角色扮演引擎三导入接口（内存库）")
    tmp = tempfile.mkdtemp(prefix="diff_selfcheck_")
    rp = RolePlayEngine(data_dir=tmp)
    rp.create_role("t1", name="测试", scenario="s", first_mes="f")
    r1 = rp.import_anchor("t1", [{"content": "锚点A", "immutable": True}])
    check("anchor 导入", r1["added"] == 1, f"added={r1['added']}")
    r2 = rp.import_values("t1", [{"name": "V1", "condition": "c1", "priority": 0.9}])
    check("values 导入", r2["added"] == 1, f"added={r2['added']}")
    r3 = rp.import_memory("t1", [{"content": "记忆1"}, {"content": "记忆2"}])
    check("memory 导入", r3["added"] == 2, f"added={r3['added']}")

    # ---------- 3. 注入块组装 ----------
    print("\n[3] 注入块组装完整性")
    block = rp.build_role_block("t1")
    checks = {
        "条件空间声明": "角色扮演条件空间" in block,
        "自我锚点": "锚点A" in block,
        "价值观条件注入": "条件触发" in block,
    }
    for k, v in checks.items():
        check(f"注入块含 {k}", v)
    rp.close()

    # ---------- 汇总 ----------
    print("\n=== 汇总 ===")
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    total = len(RESULTS)
    print(f"  {passed}/{total} 通过")
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"  FAIL: {name} — {detail}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
