# -*- coding: utf-8 -*-
"""harness.core.agent_pool · Agent 实例池（灵枢引擎接入）
================================================
from aeis.api import Agent——直接调库，MCP 协议层完全丢弃。
构造惰性（0.47s，YOLO/CLIP 首次视觉才加载）。
"""
import os
import sys

_AEIS_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _AEIS_ROOT not in sys.path:
    sys.path.insert(0, _AEIS_ROOT)


class AgentPool:
    """Agent 单例池（当前单实例：灵枢主 Agent，生产库）。"""

    def __init__(self, env: dict = None):
        self._env = env or {}
        self._agent = None

    def get(self):
        """获取主 Agent（惰性构造，首次调用才创建）。"""
        if self._agent is None:
            # 注入运行时环境变量（密钥等）
            for k, v in self._env.items():
                if v and not os.environ.get(k):
                    os.environ[k] = str(v)
            import aeis  # noqa: F401  必须先 import 包（注册 sys.modules 别名）
            from aeis.api import Agent
            db = self._env.get("AEIS_DB") or os.environ.get("AEIS_DB") or ":memory:"
            identity = self._env.get("AEIS_IDENTITY") or "灵枢"
            self._agent = Agent(identity=identity, db_path=db)
        return self._agent

    def close(self):
        if self._agent is not None:
            try:
                self._agent.close()
            except Exception:
                pass
            self._agent = None
