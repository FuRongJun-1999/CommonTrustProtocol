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
    },
    "voice": {"enabled": True, "max_seconds": 10},
    "scheduler": {"enabled": True, "tick_seconds": 15},
    "terminal": {"enabled": True},
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
