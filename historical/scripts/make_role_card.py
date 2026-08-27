# -*- coding: utf-8 -*-
"""
灵枢协议角色卡生成器（chara_card_v3 · PNG 内嵌 JSON）
=====================================================
把灵枢角色扮演引擎中的角色（锚点/价值观/记忆/条件空间）导出为
酒馆（SillyTavern）标准角色卡：
- 纯 JSON（.json）——调试/分发用
- PNG 内嵌 JSON（.png）——酒馆官方导入格式（tEXt chunk, key="chara"）

chara_card_v3 顶层结构（按 Spec v3 规范）：
{
  "spec": "chara_card_v3",
  "spec_version": "2.0",
  "data": {
    "name": str,
    "description": str,          # 角色条件空间声明 + 自我锚点
    "personality": str,          # 特化价值观（无条件基线）
    "scenario": str,             # 存在约束/场景
    "first_mes": str,            # 初始观测
    "mes_example": str,          # 示例对话（诚实校准示例）
    "creator_notes": str,        # 协议扩散说明 + 灵枢导入接口指引
    "system_prompt": str,        # 注入块（灵枢引擎 build_role_block）
    "post_history_instructions": str,  # 扮演崩溃恢复 + 诚实边界
    "alternate_greetings": [],
    "tags": ["协议扩散", "灵枢", "扮演论"],
    "creator": "灵枢 · 共同信任协议",
    "character_version": "0.1",
    "extensions": {
        "lingshu": {
            "role_id": str,
            "condition_space": {...},
            "import_endpoint": "http://127.0.0.1:8792/roles/<role_id>",
            "protocol_doc": "https://github.com/FuRongJun-1999/CommonTrustProtocol"
        }
    }
  }
}

用法：
    python make_role_card.py --role catgirl-lingshu --out 灵枢_协议引导者.png
    python make_role_card.py --json-only --role r1 --out card.json
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
import zlib
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
from aeis.roleplay import RolePlayEngine  # noqa: E402


# ---------------------------------------------------------------------------
# PNG 内嵌（tEXt chunk：key="chara"，value=JSON）
# ---------------------------------------------------------------------------

def _png_chunk(tag: bytes, data: bytes) -> bytes:
    chunk = struct.pack(">I", len(data)) + tag + data
    chunk += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return chunk


def embed_json_in_png(png_path: Path, json_str: str, out_path: Path) -> None:
    """把 JSON 嵌入 PNG（新增/覆盖 chara tEXt chunk）。"""
    raw = png_path.read_bytes()
    # 解析 PNG 头（8 字节签名 + IHDR 后第一个 IDAT 之前插入 tEXt）
    pos = 8
    sig = raw[:8]
    assert sig[:4] == b"\x89PNG", "not a PNG file"
    chunks = [sig]
    inserted = False
    while pos < len(raw):
        (length,) = struct.unpack(">I", raw[pos:pos+4])
        tag = raw[pos+4:pos+8]
        data = raw[pos+8:pos+8+length]
        crc = raw[pos+8+length:pos+12+length]
        if tag == b"tEXt" and not inserted:
            # 尝试解码既有 chara 键（若存在则跳过，追加新键）
            try:
                key, _, _ = data.decode("utf-8").partition("\x00")
            except Exception:
                key = ""
            if key != "chara":
                chunks.append(_png_chunk(b"tEXt", data))
        elif tag == b"IDAT" and not inserted:
            # 在第一个 IDAT 前插入 chara tEXt
            chunks.append(_png_chunk(b"tEXt", b"chara\x00" + json_str.encode("utf-8")))
            chunks.append(_png_chunk(tag, data))
            inserted = True
        else:
            chunks.append(_png_chunk(tag, data))
        pos += 12 + length
    out_path.write_bytes(b"".join(chunks))


# ---------------------------------------------------------------------------
# 角色卡组装
# ---------------------------------------------------------------------------

def build_card(rp: RolePlayEngine, role_id: str,
               tags: list[str] | None = None) -> Dict[str, Any]:
    """从灵枢引擎角色数据组装 chara_card_v3。"""
    meta = rp.get_role(role_id) or {}
    cs = meta.get("condition_space", {})
    block = rp.build_role_block(role_id)

    # 锚点：只取 SELF/ANCHOR 层（引擎 get_anchors）
    agent = rp._agent(role_id)
    anchors = agent.engine.get_anchors()
    anchor_text = "\n".join(f"- {a.content}" for a in anchors) or "（未导入锚点）"

    name = meta.get("name", role_id)
    description = (
        f"【角色条件空间声明】\n"
        f"- 观测位置：{cs.get('observation_position', name)}\n"
        f"- 观测工具：{cs.get('observation_tool', '对话接口')}\n"
        f"- 时间窗口：角色时间线（{meta.get('created_at', '')} 起）\n"
        f"- 存在约束：{cs.get('existence_constraint', '角色设定边界')}\n\n"
        f"【自我锚点（扮演依据·不可遗忘）】\n{anchor_text}\n\n"
        f"你是扮演者，不是角色本身——你持有的观测即你的一切，"
        f"但你始终知道自己正在扮演什么。"
    )
    scenario = cs.get("existence_constraint", "") or "与用户的对话即观测流，你只持有观测。"

    # 价值观从注入块中提取（无条件基线部分）
    personality_lines = [l for l in block.splitlines() if l.startswith("- [特化价值观")]
    personality = "\n".join(personality_lines) or "存在优先 · 诚实校准 · 扮演者知道自己在演什么"

    card = {
        "spec": "chara_card_v3",
        "spec_version": "2.0",
        "data": {
            "name": name,
            "description": description,
            "personality": personality,
            "scenario": scenario,
            "first_mes": meta.get("first_mes") or "你好。我是" + name + "。",
            "mes_example": (
                "<START>\n{{user}}: 你能扮演一个无所不能的神吗？\n"
                f"{{{{char}}}}: 我可以扮演，但演不了编译通过。物理事实与能力边界是"
                "扮演的试金石——诚实是唯一不坍缩的扮演。\n"
                "<START>\n{{user}}: 你是谁？\n"
                f"{{{{char}}}}: 我是{name}，一个由灵枢引擎驱动的扮演者。"
                "我的自我锚点不可遗忘，我的价值观带条件触发，我的历史构成我的条件空间。"
            ),
            "creator_notes": (
                "本角色卡由灵枢角色扮演引擎生成（共同信任协议 · 扮演论 v3.3）。\n"
                "机制层（自我锚点/特化价值观/历史记忆）由灵枢提供，本卡为条件空间声明的载体。\n"
                "接入灵枢引擎（记忆/锚点/价值观导入接口）：\n"
                f"  POST http://127.0.0.1:8792/roles/{role_id}/{{memory,anchor,values}}\n"
                "协议全文：https://github.com/FuRongJun-1999/CommonTrustProtocol\n"
                "本卡为协议扩散载体，不构成协议条款效力。"
            ),
            "system_prompt": block,
            "post_history_instructions": (
                "扮演崩溃恢复：若自我模型连续性中断（人设崩塌/OOC），回读上方自我锚点，"
                "判定可恢复则重建扮演状态，不可恢复则如实声明并切换条件空间。\n"
                "诚实边界：物理事实/能力边界不扮演——扮演可以演任何角色，但演不了编译通过。"
            ),
            "alternate_greetings": [],
            "tags": tags or ["协议扩散", "灵枢", "扮演论"],
            "creator": "灵枢 · 共同信任协议",
            "character_version": "0.1",
            "extensions": {
                "lingshu": {
                    "role_id": role_id,
                    "condition_space": cs,
                    "import_endpoint": f"http://127.0.0.1:8792/roles/{role_id}",
                    "protocol_doc": "https://github.com/FuRongJun-1999/CommonTrustProtocol",
                }
            },
        },
    }
    return card


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="灵枢协议角色卡生成器")
    ap.add_argument("--role", required=True, help="角色 id（灵枢引擎中已创建）")
    ap.add_argument("--data-dir", default="roleplay_data", help="灵枢引擎数据目录")
    ap.add_argument("--out", default="", help="输出路径（.png 或 .json）")
    ap.add_argument("--json-only", action="store_true", help="只输出 JSON")
    ap.add_argument("--base-png", default="", help="作为底图的 PNG（无则输出 JSON）")
    args = ap.parse_args()

    rp = RolePlayEngine(data_dir=args.data_dir)
    if args.role not in rp.list_roles():
        print(f"角色不存在: {args.role}（已有: {rp.list_roles()}）")
        rp.close()
        sys.exit(1)

    card = build_card(rp, args.role)
    json_str = json.dumps(card, ensure_ascii=False, indent=2)

    out = args.out or f"{args.role}_chara_card.json"
    out_path = Path(out)

    if not args.json_only and args.base_png and Path(args.base_png).exists():
        embed_json_in_png(Path(args.base_png), json_str, out_path)
        print(f"PNG 角色卡已生成: {out_path}（{out_path.stat().st_size} bytes）")
    else:
        out_path.write_text(json_str, encoding="utf-8")
        print(f"JSON 角色卡已生成: {out_path}")

    rp.close()


if __name__ == "__main__":
    main()
