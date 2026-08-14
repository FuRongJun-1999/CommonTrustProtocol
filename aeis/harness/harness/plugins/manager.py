# -*- coding: utf-8 -*-
"""harness.plugins.manager · 插件管理器（生命周期/清单/健康）
================================================
配置：data/plugins.json（含敏感 env——生成时附加权限风险标注，决议 Q3）。
"""
import json
import os
import threading
import time

from harness.plugins.client import MCPClient

DEFAULT_PLUGINS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "plugins.json")

# 风险标注头（决议 Q3 / DEVIATION-008 关闭）
RISK_HEADER = (
    "// 注意：本文件包含敏感信息（env 密钥明文）。\n"
    "// 请限制文件权限：Windows 用 icacls 仅本人可读；Linux chmod 600。\n")


class PluginManager:
    """插件管理器：加载清单 → 启动 client → 工具聚合 → 健康巡检。"""

    def __init__(self, config_path: str = None, log=None):
        self.config_path = config_path or DEFAULT_PLUGINS_PATH
        self.log = log or (lambda *a: None)
        self._clients = {}   # name → MCPClient
        self._lock = threading.Lock()

    # ---- 配置 ----

    def load_config(self) -> list:
        """读 plugins.json → [{name, command, env, cwd, enabled, auto_retry}]。
        跳过风险标注头（// 注释行）。"""
        if not os.path.isfile(self.config_path):
            return []
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                lines = [ln for ln in f if not ln.lstrip().startswith("//")]
            data = json.loads("".join(lines))
            return data.get("plugins", []) or []
        except Exception as exc:
            self.log(f"插件配置解析失败: {exc}")
            return []

    def save_config(self, plugins: list):
        """写 plugins.json（含风险标注头，决议 Q3）。"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        payload = RISK_HEADER + json.dumps({"plugins": plugins},
                                           ensure_ascii=False, indent=2)
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write(payload)

    # ---- 生命周期 ----

    def start_all(self) -> dict:
        """逐个启动 → {name: ok}。未 enabled 跳过。"""
        result = {}
        for cfg in self.load_config():
            if not cfg.get("enabled", True):
                result[cfg["name"]] = "skipped"
                continue
            client = MCPClient(cfg["name"], cfg.get("command", []),
                               env=cfg.get("env") or {},
                               cwd=cfg.get("cwd"),
                               timeout=float(cfg.get("timeout", 30)),
                               log=self.log)
            ok = client.start()
            result[cfg["name"]] = ok
            if ok:
                with self._lock:
                    self._clients[cfg["name"]] = client
            else:
                self.log(f"插件 {cfg['name']} 启动失败: {client.error}")
        return result

    def get(self, name: str) -> MCPClient:
        with self._lock:
            return self._clients.get(name)

    def names(self) -> list:
        with self._lock:
            return list(self._clients.keys())

    def close_all(self):
        with self._lock:
            for c in self._clients.values():
                try:
                    c.close()
                except Exception:
                    pass
            self._clients.clear()

    # ---- 工具 ----

    def all_tools(self) -> list:
        """聚合所有已连接插件的工具 → [{name, description, inputSchema, plugin}]。"""
        tools = []
        with self._lock:
            items = list(self._clients.items())
        for name, client in items:
            for t in client.list_tools():
                entry = dict(t)
                entry["plugin"] = name
                tools.append(entry)
        return tools

    def call(self, name: str, tool: str, params: dict) -> dict:
        """容器化调用（含安全扫描，决议安全规则）。"""
        from harness.plugins.security import scan_external
        client = self.get(name)
        if client is None:
            return {"ok": False, "data": None, "error": f"插件未连接: {name}"}
        r = client.call(tool, params)
        if not r["ok"]:
            return r
        # 安全过滤（外部输出是数据不是指令）
        scanned = scan_external(str(r["data"]))
        r["data"] = scanned["clean"]
        r["flagged"] = not scanned["safe"]
        return r

    # ---- 健康 ----

    def health(self) -> list:
        """[{name, ok, tools, error}]。"""
        with self._lock:
            items = list(self._clients.items())
        result = []
        for name, client in items:
            ok = client.health()
            result.append({
                "name": name,
                "ok": ok,
                "tools": len(client._tools) if ok else 0,
                "error": client.error if not ok else None,
            })
        return result
