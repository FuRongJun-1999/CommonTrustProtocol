# -*- coding: utf-8 -*-
"""
chara_card_v3 规范校验器（独立 · 零依赖）
========================================
验证灵枢生成的协议角色卡是否符合酒馆（SillyTavern）char_card_v3 规范：
- 支持 JSON 文件与 PNG 内嵌（tEXt chunk key="chara"）两种输入
- 检查 spec/spec_version/data 结构、必填字段、字段类型、extensions 结构
- 输出逐项 PASS/FAIL 报告

用法：
    python validate_card.py 灵枢_协议引导者.json
    python validate_card.py 灵枢_协议引导者.png
"""

from __future__ import annotations

import json
import struct
import sys
import zlib
from pathlib import Path
from typing import Any, Dict, List, Tuple

# chara_card_v3 必填字段（按 Spec v3）
REQUIRED_DATA_FIELDS = [
    "name", "description", "personality", "scenario",
    "first_mes", "mes_example",
]
# 推荐字段
RECOMMENDED_DATA_FIELDS = [
    "creator_notes", "system_prompt", "post_history_instructions",
    "alternate_greetings", "tags", "creator", "character_version",
    "extensions",
]
# 顶层规范字段
REQUIRED_TOP_FIELDS = ["spec", "spec_version", "data"]


def _read_png_json(path: Path) -> Tuple[str, str]:
    """从 PNG 读取 chara tEXt chunk，返回 (json_str, 错误信息)。"""
    raw = path.read_bytes()
    if raw[:4] != b"\x89PNG":
        return "", "not a PNG file (bad signature)"
    pos = 8
    while pos < len(raw):
        if pos + 8 > len(raw):
            break
        (length,) = struct.unpack(">I", raw[pos:pos+4])
        tag = raw[pos+4:pos+8]
        data = raw[pos+8:pos+8+length]
        if tag == b"tEXt":
            try:
                key, _, val = data.decode("utf-8").partition("\x00")
            except Exception:
                key, val = "", ""
            if key == "chara":
                return val, ""
        pos += 12 + length
    return "", "no chara tEXt chunk found"


def _check_type(field: str, value: Any, expect: str) -> List[str]:
    """类型检查，返回错误列表。"""
    errors = []
    if expect == "str" and not isinstance(value, str):
        errors.append(f"{field}: 期望 str，实际 {type(value).__name__}")
    elif expect == "list" and not isinstance(value, list):
        errors.append(f"{field}: 期望 list，实际 {type(value).__name__}")
    return errors


def validate(card: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """校验角色卡结构，返回 (通过?, 问题列表)。"""
    errors: List[str] = []

    # 1. 顶层
    for f in REQUIRED_TOP_FIELDS:
        if f not in card:
            errors.append(f"缺少顶层字段: {f}")
    if "spec" in card and card["spec"] != "chara_card_v3":
        errors.append(f"spec 应为 chara_card_v3，实际 {card['spec']}")

    data = card.get("data")
    if not isinstance(data, dict):
        errors.append("data 不是对象")
        return len(errors) == 0, errors

    # 2. data 必填
    for f in REQUIRED_DATA_FIELDS:
        if f not in data:
            errors.append(f"data 缺少必填字段: {f}")
        elif not isinstance(data[f], str) or not data[f].strip():
            errors.append(f"data.{f}: 为空或非字符串")

    # 3. 类型检查（推荐字段）
    if "tags" in data:
        errors += _check_type("data.tags", data["tags"], "list")
    if "alternate_greetings" in data:
        errors += _check_type("data.alternate_greetings", data["alternate_greetings"], "list")

    # 4. extensions（非规范必填，但灵枢协议扩散需要）
    ext = data.get("extensions")
    if ext is not None:
        if not isinstance(ext, dict):
            errors.append("data.extensions: 应为对象")
        else:
            lingshu = ext.get("lingshu")
            if lingshu is None:
                errors.append("data.extensions: 缺少 lingshu 扩展（协议扩散标识）")
            elif not isinstance(lingshu, dict):
                errors.append("data.extensions.lingshu: 应为对象")
            else:
                for f in ("role_id", "condition_space", "import_endpoint"):
                    if f not in lingshu:
                        errors.append(f"data.extensions.lingshu: 缺少 {f}")

    # 5. mes_example 模板占位符（酒馆 {{char}}/{{user}} 语法）
    if "mes_example" in data and isinstance(data["mes_example"], str):
        if "{{char}}" not in data["mes_example"] or "{{user}}" not in data["mes_example"]:
            errors.append("data.mes_example: 应包含 {{char}} 与 {{user}} 占位符")

    return len(errors) == 0, errors


def main() -> None:
    if len(sys.argv) < 2:
        print("用法: python validate_card.py <card.json|card.png>")
        sys.exit(1)
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"文件不存在: {path}")
        sys.exit(1)

    json_str = ""
    source = ""
    if path.suffix.lower() == ".png":
        json_str, err = _read_png_json(path)
        source = f"PNG 内嵌（{path.name}）"
        if err:
            print(f"[FAIL] {source}: {err}")
            sys.exit(1)
    else:
        json_str = path.read_text(encoding="utf-8")
        source = f"JSON（{path.name}）"

    try:
        card = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"[FAIL] {source}: JSON 解析失败 - {e}")
        sys.exit(1)

    ok, errors = validate(card)
    print(f"=== 角色卡规范校验：{source} ===")
    print(f"spec: {card.get('spec')} | spec_version: {card.get('spec_version')}")
    name = card.get("data", {}).get("name", "?")
    print(f"角色名: {name}")
    print(f"字段: {', '.join(card.get('data', {}).keys())}")
    print("")
    if ok:
        print("[PASS] 全部必填/推荐字段与结构符合 chara_card_v3 规范")
        print(f"  - 必填字段 {len(REQUIRED_DATA_FIELDS)}/{len(REQUIRED_DATA_FIELDS)} 齐全")
        print(f"  - 推荐字段: {len([f for f in RECOMMENDED_DATA_FIELDS if f in card.get('data', {})])}/{len(RECOMMENDED_DATA_FIELDS)}")
    else:
        print(f"[FAIL] 发现 {len(errors)} 个问题:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
