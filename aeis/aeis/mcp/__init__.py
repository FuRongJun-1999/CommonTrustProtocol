# -*- coding: utf-8 -*-
"""
aeis.mcp · 灵枢 MCP 服务包
==========================
零依赖 MCP server（stdio · JSON-RPC 2.0）。

启动：python -m aeis.mcp.server    （或安装后：aeis-mcp）
环境变量：AEIS_DB（持久化路径，默认 :memory:）· AEIS_IDENTITY（身份，默认 灵枢）

注意：本包不主动导入 server（保持 python -m 启动干净）；
需要编程式使用时：from aeis.mcp.server import AEISServer
"""
