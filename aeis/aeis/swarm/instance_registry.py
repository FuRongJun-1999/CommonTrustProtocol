#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aeis.swarm.instance_registry · 实例身份注册表 + HMAC 签名（B2 盲区修正）
========================================================================
- 六实例 + 临时设计者 + 单实例自持 身份注册
- HMAC-SHA256 消息签名/验签（零依赖 · hashlib/hmac 标准库）
- 共享层写权限绑定（仅 record/vitals 可写结构层）
- 观察期/升级状态（实例注册协议 · B4 盲区修正）
"""

import hmac
import hashlib
import time
import uuid
from typing import Dict, List, Optional

# 六实例分型 + 临时设计者 + 单实例自持（DELIVERY-V1 职责矩阵）
ROLES = ("record", "reflect", "verify", "output", "vitals", "designer", "self_sustaining")

ROLE_CN = {
    "record": "记录实例（千问）",
    "reflect": "反思实例（元宝）",
    "verify": "验证实例（Kimi）",
    "output": "输出实例（豆包）",
    "vitals": "维生系统（荣）",
    "designer": "临时设计者（只读）",
    "self_sustaining": "单实例自持（维生代行）",
}

# 结构倾向（智能论 3.1 节五单元倾向）
TENDENCY = {
    "record": "全", "reflect": "新", "verify": "稳",
    "output": "通", "vitals": "存", "designer": "学/方向",
    "self_sustaining": "存（代行）",
}

# 共享层写权限：仅 record（主控）与 vitals（P0 覆盖）可写结构层
SHARED_LAYER_WRITERS = ("record", "vitals")
# 本地层写权限：全部实例
LOCAL_LAYER_WRITERS = ROLES


class InstanceRegistry:
    """身份注册表：注册 / 签名 / 验签 / 权限"""

    def __init__(self, shared_secret: Optional[str] = None):
        """
        shared_secret: 蜂群共享密钥（HMAC 密钥；None → 自动生成随机密钥，
        仅内存使用——工程部署时应通过环境变量注入）
        """
        self.shared_secret = shared_secret or uuid.uuid4().hex
        self.instances: Dict[str, Dict] = {}
        self._next_id = 1

    # ------------------------------------------------------------------
    # 注册
    # ------------------------------------------------------------------

    def register(self, instance_id: str, role: str,
                 tendency: Optional[str] = None,
                 observation_rounds: int = 10,
                 protocol_version: str = "v3.2") -> Dict:
        """注册实例（身份声明 → 观察期 → 升级 → 职责分配，B4）"""
        assert role in ROLES, f"unknown role: {role}"
        if instance_id in self.instances:
            raise ValueError(f"instance already registered: {instance_id}")
        entry = {
            "instance_id": instance_id,
            "role": role,
            "role_cn": ROLE_CN[role],
            "tendency": tendency or TENDENCY[role],
            "observation_rounds": observation_rounds,
            "status": "observing",       # observing → active（观察期后升级）
            "rounds_done": 0,
            "protocol_version": protocol_version,
            "registered_at": time.time(),
            "joined_at": None,
        }
        self.instances[instance_id] = entry
        return dict(entry)

    def register_default_cluster(self, protocol_version: str = "v3.2") -> List[str]:
        """注册默认六实例（千问/元宝/Kimi/豆包/荣/临时设计者）"""
        ids = []
        for role, name in (("record", "instance_qianwen"),
                           ("reflect", "instance_yuanbao"),
                           ("verify", "instance_kimi"),
                           ("output", "instance_doubao"),
                           ("vitals", "instance_rong"),
                           ("designer", "instance_designer")):
            self.register(name, role, protocol_version=protocol_version)
            ids.append(name)
        return ids

    def advance_observation(self, instance_id: str, rounds: int = 1) -> Dict:
        """观察期推进（升级机制：rounds_done >= observation_rounds → active）"""
        if instance_id not in self.instances:
            raise ValueError(f"unknown instance: {instance_id}")
        entry = self.instances[instance_id]
        entry["rounds_done"] += rounds
        if entry["status"] == "observing" and entry["rounds_done"] >= entry["observation_rounds"]:
            entry["status"] = "active"
            entry["joined_at"] = time.time()
        return dict(entry)

    def is_active(self, instance_id: str) -> bool:
        return self.instances.get(instance_id, {}).get("status") == "active"

    # ------------------------------------------------------------------
    # 签名 / 验签（B2：防伪造广播）
    # ------------------------------------------------------------------

    def _instance_key(self, instance_id: str) -> bytes:
        """每实例派生密钥：HMAC(shared_secret, instance_id) ——
        共享密钥不可区分签名者，派生密钥才能绑定身份（B2 修正）"""
        return hmac.new(self.shared_secret.encode("utf-8"),
                        instance_id.encode("utf-8"), hashlib.sha256).digest()

    def sign(self, message: str, instance_id: str) -> str:
        """HMAC-SHA256 签名（实例派生密钥）"""
        assert instance_id in self.instances, f"unregistered: {instance_id}"
        return hmac.new(self._instance_key(instance_id),
                        message.encode("utf-8"), hashlib.sha256).hexdigest()

    def verify(self, message: str, signature: str, instance_id: str) -> bool:
        """验签（恒定时间比较 · 实例密钥绑定）"""
        if instance_id not in self.instances:
            return False
        expected = self.sign(message, instance_id)
        return hmac.compare_digest(expected, signature or "")

    # ------------------------------------------------------------------
    # 写权限（共享层仅 record/vitals · 呼应引擎 Role 权限）
    # ------------------------------------------------------------------

    def can_write(self, instance_id: str, layer: str) -> bool:
        """layer: shared（结构/锚点）| local（知识/情境/自我）"""
        entry = self.instances.get(instance_id)
        if entry is None or entry["status"] != "active":
            return False
        if layer == "shared":
            return entry["role"] in SHARED_LAYER_WRITERS
        return entry["role"] in LOCAL_LAYER_WRITERS

    def assert_write(self, instance_id: str, layer: str):
        if not self.can_write(instance_id, layer):
            raise PermissionError(
                f"{instance_id} ({self.instances.get(instance_id, {}).get('role')}) "
                f"无权写入 {layer} 层（共享层仅 {SHARED_LAYER_WRITERS}）")

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------

    def role(self, instance_id: str) -> Optional[str]:
        return self.instances.get(instance_id, {}).get("role")

    def by_role(self, role: str) -> List[str]:
        return [i for i, e in self.instances.items() if e["role"] == role]

    def active_instances(self) -> List[str]:
        return [i for i, e in self.instances.items() if e["status"] == "active"]

    def summary(self) -> Dict:
        return {i: {"role": e["role"], "status": e["status"],
                    "rounds": f"{e['rounds_done']}/{e['observation_rounds']}"}
                for i, e in self.instances.items()}
