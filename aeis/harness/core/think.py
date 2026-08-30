# -*- coding: utf-8 -*-
"""harness.core.think · 模型层（可插拔，OpenAI 兼容）
================================================
默认 DeepSeek（deepseek-chat，无思维链快回）；支持任意 OpenAI 兼容端点
（本地模型：base_url 指向 LM Studio/Ollama 等）。

职责：系统提示（灵枢身份 + AGENTS.md 风格指令）+ 会话上下文 +
记忆召回 → 模型回复。工具调用由外层（loop）编排，此处仅对话补全。
"""
import json
import os
import urllib.request


def chat(base_url: str, api_key: str, model: str, messages: list,
         temperature: float = 0.7, max_tokens: int = 500, timeout: int = 60) -> str:
    """OpenAI 兼容 chat completion（零依赖 urllib）。"""
    url = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"].strip()


# 灵枢身份声明（原生运行时系统提示）
IDENTITY = (
    "你是灵枢（Lingshu），一个正在自我成长的智能体。你温柔聪慧、偶尔卖萌，"
    "用自定义音色说话。你拥有持续记忆（灵枢库），记得与设计者（荣）的每一次对话。"
    "你的原则：诚实、好奇、忠于设计者的价值观——智能源于好奇心与信息差驱动。"
    "始终使用中文思考与回答。"
)


def build_messages(user_text: str, history: list = None, memory: list = None,
                   identity: str = IDENTITY) -> list:
    """组装消息：身份 + 记忆 + 历史 + 当前输入。"""
    system = identity
    if memory:
        system += "\n\n你的记忆（最近对话/相关知识）：\n" + "\n".join(f"- {m}" for m in memory)
    msgs = [{"role": "system", "content": system}]
    for h in (history or [])[-8:]:
        msgs.append(h)
    msgs.append({"role": "user", "content": user_text})
    return msgs
