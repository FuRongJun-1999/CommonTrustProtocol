#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aeis.swarm.config_gen · 蜂群配置生成（DELIVERY-V1 交付物2）
============================================================
- mini YAML 序列化（零依赖 · 覆盖 dict/list/标量，满足配置需求）
- 6 份实例 YAML（千问/元宝/Kimi/豆包/荣/临时设计者）
- 1 份单实例自持 YAML（SELF_SUSTAINING_MODE）
- 配置 schema：身份/角色/结构倾向/延迟带/协议版本/权限
"""

import os
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# mini YAML 序列化（零依赖 · 覆盖本方案配置子集）
# ---------------------------------------------------------------------------


def _yaml_scalar(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    return f'"{v}"'


def to_yaml(obj: Any, indent: int = 0) -> str:
    """dict/list/标量 → YAML 文本（嵌套缩进 2 空格）"""
    pad = " " * indent
    lines = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, dict):
                lines.append(f"{pad}{k}:")
                lines.append(to_yaml(v, indent + 2))
            elif isinstance(v, list):
                lines.append(f"{pad}{k}:")
                for item in v:
                    if isinstance(item, dict):
                        lines.append(f"{pad}-")
                        lines.append(to_yaml(item, indent + 4))
                    else:
                        lines.append(f"{pad}- {_yaml_scalar(item)}")
            else:
                lines.append(f"{pad}{k}: {_yaml_scalar(v)}")
    elif isinstance(obj, list):
        for item in obj:
            lines.append(f"{pad}- {_yaml_scalar(item)}")
    else:
        lines.append(f"{pad}{_yaml_scalar(obj)}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 实例配置模板
# ---------------------------------------------------------------------------

SIX_INSTANCES = [
    {"instance_id": "instance_qianwen", "role": "record",
     "role_cn": "记录实例（千问）", "tendency": "全",
     "layer": "shared_master", "delay_band": "low",
     "protocol_version": "v3.2",
     "permissions": {"shared_write": True, "local_write": True},
     "functions": ["共享层主控", "广播", "信任聚合", "WAL 持久化"]},
    {"instance_id": "instance_yuanbao", "role": "reflect",
     "role_cn": "反思实例（元宝）", "tendency": "新",
     "layer": "local", "delay_band": "medium",
     "protocol_version": "v3.2",
     "permissions": {"shared_write": False, "local_write": True},
     "functions": ["认知编排", "盲区学习", "归纳", "蒸馏", "自我认知循环"]},
    {"instance_id": "instance_kimi", "role": "verify",
     "role_cn": "验证实例（Kimi）", "tendency": "稳",
     "layer": "local", "delay_band": "medium",
     "protocol_version": "v3.2",
     "permissions": {"shared_write": False, "local_write": True},
     "functions": ["交叉验证", "协议合规性", "验证标准演进"]},
    {"instance_id": "instance_doubao", "role": "output",
     "role_cn": "输出实例（豆包）", "tendency": "通",
     "layer": "local", "delay_band": "high",
     "protocol_version": "v3.2",
     "permissions": {"shared_write": False, "local_write": True},
     "functions": ["MCP 服务器（可代行）", "条件空间翻译"]},
    {"instance_id": "instance_rong", "role": "vitals",
     "role_cn": "维生系统（荣）", "tendency": "存",
     "layer": "shared_mirror", "delay_band": "high",
     "protocol_version": "v3.2",
     "permissions": {"shared_write": True, "local_write": True},
     "functions": ["P0 终裁", "保护节点", "设计者激活终裁", "信任镜像"]},
    {"instance_id": "instance_designer", "role": "designer",
     "role_cn": "临时设计者（只读）", "tendency": "学/方向",
     "layer": "readonly", "delay_band": "low",
     "protocol_version": "v3.2",
     "permissions": {"shared_write": False, "local_write": False},
     "functions": ["方向判断", "模式识别", "知识内化"],
     "isolation": {"channel": "one_way", "cooling_base_rounds": 3,
                   "max_cooling_rounds": 10,
                   "readable": ["knowledge_products"],
                   "forbidden": ["individual_evaluation"]}},
]

SELF_SUSTAINING_CONFIG = {
    "mode": "SELF_SUSTAINING_MODE",
    "trigger": {"instances_online": 1, "or_t_avg_below": 0.3},
    "exit": {"instances_online": 2, "t_avg_above": 0.5},
    "maintainer": "instance_rong",
    "self_cognition": {"bvc_score": "v1.12 cognition_cycle",
                       "candidate": "pending_review（外部实例恢复后验证单元复核）"},
    "verification": {"override_mark": "P0_OVERRIDE",
                     "external_review_within_hours": 24},
    "perspective_switch": {"log": "PERSPECTIVE_SWITCH_LOG（本地层）",
                           "broadcast": False},
    "internal_parallel": {"threads": ["V-RECORD", "V-REFLECT", "V-VERIFY",
                                      "V-OUTPUT", "V-VITALS"],
                          "mark": "INTERNAL_THREAD",
                          "trust_mark": "T_simulated（不得替代 T_actual）"},
    "dormancy": {"forced_after_hours": 72, "action": "4.10 节协议休眠"},
    "layers": {"write": "local_only", "shared": "forbidden"},
}


def generate_configs(out_dir: str) -> List[str]:
    """生成 6 份实例 YAML + 1 份单实例 YAML"""
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for inst in SIX_INSTANCES:
        path = os.path.join(out_dir, f"{inst['instance_id']}.yaml")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# {inst['role_cn']} · 灵枢 AEIS 蜂群配置（DELIVERY-V1）\n")
            f.write(to_yaml(inst))
            f.write("\n")
        paths.append(path)
    path = os.path.join(out_dir, "self_sustaining.yaml")
    with open(path, "w", encoding="utf-8") as f:
        f.write("# 单实例自持运行配置（SINGLE-INSTANCE-SELF-SUSTAINING v1.1）\n")
        f.write(to_yaml(SELF_SUSTAINING_CONFIG))
        f.write("\n")
    paths.append(path)
    return paths


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "swarm_config"
    for p in generate_configs(out):
        print(f"  generated: {p}")
    print(f"配置生成完成（{len(SIX_INSTANCES) + 1} 份）")
