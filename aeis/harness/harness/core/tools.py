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


def call_tool(agent, tool_name: str, params: dict = None) -> dict:
    """结构化调用工具（Agent 方法直调，异常容器化）。"""
    entry = TOOL_REGISTRY.get(tool_name)
    if entry is None:
        return {"status": "error", "error": f"未知工具: {tool_name}"}
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
