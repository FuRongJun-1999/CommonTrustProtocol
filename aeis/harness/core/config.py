# -*- coding: utf-8 -*-
"""harness.core.config · 配置加载（零依赖）
================================================
优先级：环境变量 > data/config.json。
迁移自 ZCode config.json 的 mcp.servers.aeis env（AEIS_DB/AEIS_IDENTITY/
AEIS_DESIGNER_KEY/BOCHA_API_KEY）+ 运行时自身配置（DEEPSEEK_API_KEY、
模型端点、语音开关、调度开关）。

config.json 结构：
{
  "env": {"AEIS_DB": "...", "AEIS_IDENTITY": "灵枢", ...},
  "model": {"base_url": "https://api.deepseek.com", "name": "deepseek-chat",
            "temperature": 0.7, "max_tokens": 500},
  "voice": {"enabled": true, "max_seconds": 10},
  "scheduler": {"enabled": true, "tick_seconds": 15},
  "terminal": {"enabled": true}
}
"""
import json
import os

DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "config.json")

DEFAULTS = {
    "env": {
        "AEIS_DB": r"D:\Program Files\2_ai\AEIS\data\aeis_memory.db",
        "AEIS_IDENTITY": "灵枢",
        "AEIS_DESIGNER_KEY": "",
        "BOCHA_API_KEY": "",
        "DEEPSEEK_API_KEY": "",
        "AEIS_WORKSPACE": r"D:\Program Files\2_ai\AEIS",
    },
    "model": {
        "base_url": "https://api.deepseek.com",
        "name": "deepseek-chat",
        "temperature": 0.7,
        "max_tokens": 500,
        # v1.27（无 API 自维持 · 本地模型提供方）：providers 模型提供方列表。
        # deepseek = 云端（需 DEEPSEEK_API_KEY）；ollama = 本地（离线可用，
        # API 断开后仍可推理——角色扮演/兜底优先走本地）。
        "providers": [
            {"name": "deepseek", "base_url": "https://api.deepseek.com",
             "model": "deepseek-chat", "key_env": "DEEPSEEK_API_KEY", "local": False},
            {"name": "ollama", "base_url": "http://localhost:11434/v1",
             "model": "ornith-1.5-9b", "key_env": "", "local": True},
        ],
        # 默认本地提供方（角色扮演/降级兜底优先）
        "local": {"base_url": "http://localhost:11434/v1",
                  "name": "ornith-1.5-9b", "prefer": True},
    },
    "voice": {"enabled": True, "max_seconds": 10},
    "scheduler": {"enabled": True, "tick_seconds": 15},
    "terminal": {"enabled": True},
    "agents": {"enabled": True, "pool_size": 3, "default_timeout": 300},
}


def load_config(path: str = None) -> dict:
    """加载配置：env 优先，config.json 补全（迁移自 ZCode 的 4 密钥）。"""
    cfg = json.loads(json.dumps(DEFAULTS))  # deep copy
    path = path or DEFAULT_CONFIG_PATH
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                user = json.load(f)
            for k, v in (user.get("env") or {}).items():
                cfg["env"][k] = v
            for sec in ("model", "voice", "scheduler", "terminal"):
                if isinstance(user.get(sec), dict):
                    cfg[sec].update(user[sec])
        except Exception:
            pass
    # 环境变量覆盖（运行时契约）
    for k in cfg["env"]:
        if os.environ.get(k):
            cfg["env"][k] = os.environ[k]
    return cfg


def save_default_config(path: str = None) -> str:
    """写出默认配置模板（含密钥占位，供迁移粘贴）。"""
    path = path or DEFAULT_CONFIG_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(DEFAULTS, f, ensure_ascii=False, indent=2)
    return path
