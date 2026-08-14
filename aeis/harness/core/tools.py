# -*- coding: utf-8 -*-
"""harness.core.tools · 工具注册表（工具 = Agent 方法直调）
================================================
MCP 协议层丢弃后的原生工具面：44 工具映射为 Agent 方法名。
运行时主循环（loop）按需调用；任务（心跳/睡眠）直接调 Agent。
"""
# 工具白名单：名称 → (Agent 方法名, 说明)
TOOL_REGISTRY = {
    # 记忆
    "remember": ("remember", "写入感知记忆"),
    "recall": ("recall", "组合联想召回"),
    "search": ("search", "内容检索"),
    "timeline": ("timeline", "记忆时间线"),
    "session_note": ("session_note", "会话要点写入"),
    "session_recall": ("session_recall", "会话要点恢复"),
    "compact_context": ("compact_context", "上下文压缩"),
    # 关系与推理
    "relate": ("relate", "建立关系边"),
    "reason": ("reason", "因果路径推理"),
    "predict_routes": ("predict_routes", "生成式预测"),
    # 认知与学习
    "blindspots": ("blindspots", "盲区注册表"),
    "learn": ("learn", "盲区学习"),
    "induce": ("induce", "概念归纳"),
    # 知识飞轮
    "distill": ("distill", "经验蒸馏"),
    "flywheel_report": ("flywheel_report", "飞轮度量"),
    "transfer_test": ("transfer_test", "迁移测试"),
    "calibrate": ("calibrate", "宇宙校准"),
    # 生命周期
    "step": ("step", "生命周期一步"),
    "lifecycle_state": ("lifecycle_state", "生命周期状态"),
    # 自我认知
    "action_log": ("action_log", "行为日志"),
    "cognition_cycle": ("cognition_cycle", "自我认知循环"),
    "cognition_report": ("cognition_report", "认知报告"),
    "emotional_bias": ("emotional_bias", "情绪方向性"),
    "self_reliability": ("self_reliability", "元认知校准"),
    "preflight": ("preflight", "输出前反思"),
    "think": ("think", "推理记忆注入"),
    # 反思
    "recursive_reflect": ("recursive_reflect", "递归验证反思"),
    # 视觉
    "see": ("see", "视觉感知"),
    "visual_check": ("visual_check", "视觉信息差"),
    "vprim_query": ("vprim_query", "视觉原语"),
    "world3d": ("world3d", "3D 时空重建"),
    # 身体
    "body": ("body", "身体能力声明"),
    "body_devices": ("body_devices", "设备清单"),
    "device_call": ("device_call", "设备调用"),
    # 知识摄取
    "ingest_text": ("ingest_text", "文本摄取"),
    "ingest_file": ("ingest_file", "文件摄取"),
    "ingest_url": ("ingest_url", "URL 摄取"),
    "web_search": ("web_search", "网络搜索"),
    # 服务
    "self_check": ("self_check", "完整性自检"),
    "gap_trend": ("gap_trend", "信息差趋势"),
    "service_info": ("service_info", "服务信息"),
    "export": ("export", "全库导出"),
}

# ---- 动作分级（ADVERSARIAL-GUARDRAIL 规则2 · DEVIATION-011 关闭） ----
# 显式声明表；未声明工具默认 execute（保守策略）
ACTION_TIERS = {
    # read（只读）
    "recall": "read", "search": "read", "timeline": "read",
    "reason": "read", "predict_routes": "read", "blindspots": "read",
    "flywheel_report": "read", "transfer_test": "read", "calibrate": "read",
    "self_check": "read", "gap_trend": "read", "service_info": "read",
    "lifecycle_state": "read", "cognition_report": "read",
    "action_log": "read", "emotional_bias": "read", "self_reliability": "read",
    "session_recall": "read", "body": "read", "body_devices": "read",
    # write（写入）
    "remember": "write", "session_note": "write", "compact_context": "write",
    "relate": "write", "induce": "write", "learn": "write",
    "distill": "write", "step": "write", "cognition_cycle": "write",
    "preflight": "write", "think": "write", "recursive_reflect": "write",
    "see": "write", "visual_check": "write", "vprim_query": "write",
    "world3d": "write", "ingest_text": "write", "ingest_file": "write",
    "ingest_url": "write", "web_search": "write", "session_note": "write",
    # execute（执行）
    "device_call": "execute", "web_ingest_search": "execute",
    # destructive（破坏级：需 授权|高信任|显式上下文）
    "export": "destructive",
}


def get_tier(tool_name: str) -> str:
    """工具动作分级（显式声明优先，未声明默认 execute——保守策略）。"""
    return ACTION_TIERS.get(tool_name, "execute")


def call_tool(agent, tool_name: str, params: dict = None,
              gate=None, source_kind: str = "instance",
              authorized: bool = False,
              explicit_context: bool = False) -> dict:
    """结构化调用工具（Agent 方法直调，异常容器化）。
    gate：SecurityGate（None=不启用分级闸门，向后兼容）；
    source_kind：来源信任层级（designer/instance/swarm/child/external）。"""
    entry = TOOL_REGISTRY.get(tool_name)
    if entry is None:
        return {"status": "error", "error": f"未知工具: {tool_name}"}
    # 对抗护栏：动作分级闸门（规则2）
    if gate is not None:
        tier = get_tier(tool_name)
        p = params or {}
        target = str(p.get("target", str(p)[:60]))
        check = gate.check_action(
            source=source_kind, source_trust=gate.trust_for(source_kind),
            tier=tier, target=target, authorized=authorized,
            explicit_context=explicit_context)
        if not check["allow"]:
            ev = check["event"] or {}
            return {"status": "blocked", "tool": tool_name,
                    "reason": check["reason"],
                    "event": ev.get("event_type", "ACTION_BLOCKED")}
    method = getattr(agent, entry[0], None)
    if method is None:
        return {"status": "error", "error": f"Agent 无方法: {entry[0]}"}
    try:
        result = method(**(params or {}))
        return {"status": "ok", "tool": tool_name, "result": result}
    except TypeError:
        # 参数不匹配时尝试 kwargs 转发（Agent 方法签名各异）
        try:
            result = method(*(list((params or {}).values())))
            return {"status": "ok", "tool": tool_name, "result": result}
        except Exception as exc:
            return {"status": "error", "error": f"{entry[0]} 调用失败: {exc}"}
    except Exception as exc:
        return {"status": "error", "error": f"{entry[0]} 调用失败: {exc}"}
