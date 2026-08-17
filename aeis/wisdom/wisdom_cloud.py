# -*- coding: utf-8 -*-
"""
智慧之书 · mock 云服务（零依赖 http.server）
==========================================
端点：
  POST /dex/query   {op, params}          七操作查询（读公开 · 任何灵枢智能体）
  POST /dex/upload  {entry, contributor}  上传已验证条目（verified 闸门 + 贡献记账）
  GET  /dex/ledger?contributor=X          贡献账本
  GET  /dex/status                        图谱元信息

运行：python wisdom_cloud.py [port]
"""
import json
import os
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from wisdom_book import ConditionDex, _default_cs  # noqa: E402

CLOUD_DB = os.path.join(HERE, "wisdom-book-cloud.db")


def _cs_from_dict(d):
    from aeis.core import ConditionSpace
    if not d:
        return _default_cs()
    try:
        tw = tuple(d.get("time_window") or (0.0, 9999999999.0))
    except Exception:
        tw = (0.0, 9999999999.0)
    return ConditionSpace(
        observation_position=d.get("observation_position", ""),
        observation_tool=d.get("observation_tool", ""),
        time_window=tw,
        existence_constraint=d.get("existence_constraint", ""))


class DexHandler(BaseHTTPRequestHandler):
    cloud = None  # ConditionDex 实例（由 run_server 注入）

    def log_message(self, *args):
        pass

    def _send(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n).decode("utf-8"))

    # ---------------- GET ----------------

    def do_GET(self):
        path = self.path.split("?")[0]
        qs = {}
        if "?" in self.path:
            qs = urllib.parse.parse_qs(self.path.split("?", 1)[1])
        if path in ("/", "/ui", "/index.html", "/ui/index.html", "/wisdom_ui.html"):
            self._send_html()
        elif path == "/dex/status":
            self._send(self._status())
        elif path == "/dex/ledger":
            c = qs.get("contributor", [None])[0]
            self._send(self._ledger(c))
        else:
            self._send({"error": "not_found"}, 404)

    def _send_html(self):
        """人类学习/搜索界面（零依赖单页）"""
        html_path = os.path.join(HERE, "wisdom_ui.html")
        try:
            with open(html_path, "r", encoding="utf-8") as f:
                body = f.read().encode("utf-8")
        except OSError:
            self._send({"error": "ui_not_found"}, 404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ---------------- POST ----------------

    def do_POST(self):
        try:
            body = self._read()
        except Exception:
            self._send({"error": "bad_json"}, 400)
            return
        path = self.path.split("?")[0]
        if path == "/dex/query":
            self._send(self._query(body))
        elif path == "/dex/upload":
            self._send(self._upload(body))
        else:
            self._send({"error": "not_found"}, 404)

    # ---------------- 实现 ----------------

    def _query(self, body):
        op = body.get("op", "")
        params = body.get("params") or {}
        d = self.cloud
        try:
            if op == "filter":
                return {"op": op, "results": d.dex_filter(**params)}
            if op == "respond":
                return {"op": op, "results": d.dex_respond(params.get("condition", ""))}
            if op == "status_node":
                return {"op": op, "results": d.dex_status(params.get("node_id", ""))}
            if op == "cs":
                return {"op": op, "results": d.dex_cs(params.get("code", ""))}
            if op == "combine":
                return {"op": op, "results": d.dex_combine(params.get("a", ""), params.get("b", ""))}
            if op == "separate":
                return {"op": op, "results": d.dex_separate(params.get("node_id", ""))}
            if op == "invert":
                return {"op": op, "results": d.dex_invert(params.get("node_id", ""))}
            if op == "cycle":
                return {"op": op, "results": d.dex_cycle(params.get("node_id", ""))}
            if op == "analyze":
                return {"op": op, "results": d.dex_analyze(params.get("knowledge", ""))}
            if op == "predict":
                return {"op": op, "results": d.dex_predict(
                    params.get("knowledge", ""),
                    horizon=int(params.get("horizon", 2)),
                    limit=int(params.get("limit", 4)))}
            if op == "predict_compare":
                return {"op": op, "results": d.dex_predict_compare(
                    params.get("knowledge", ""),
                    params.get("theory", ""),
                    horizon=int(params.get("horizon", 2)),
                    limit=int(params.get("limit", 4)))}
            if op == "auto_verify":
                return {"op": op, "results": d.dex_auto_verify(
                    params.get("knowledge", ""),
                    limit=int(params.get("limit", 5)),
                    threshold=float(params.get("threshold", 0.50)))}
            if op == "compose":
                return {"op": op, "results": d.dex_compose(
                    params.get("knowledge", ""),
                    limit=int(params.get("limit", 5)),
                    max_anchors=int(params.get("max_anchors", 3)))}
            if op == "test":
                return {"op": op, "results": d.dex_test(params.get("knowledge", ""))}
            if op == "battle":
                return {"op": op, "results": d.dex_battle(params.get("a", ""), params.get("b", ""))}
            if op == "layer_trace":
                return {"op": op, "results": d.dex_layer_trace()}
            if op == "sandbox":
                return {"op": op, "results": d.dex_sandbox(
                    params.get("a", ""), params.get("b", ""),
                    params.get("disturbance", ""))}
            if op == "auto_test":
                return {"op": op, "results": d.dex_auto_test(
                    params.get("a", ""), params.get("b", ""))}
            if op == "usage":
                return {"op": op, "results": d.dex_usage()}
            if op == "homology":
                return {"op": op, "results": d.dex_homology(
                    params.get("entry", ""), params.get("strip_concepts"))}
            if op == "standard_battle":
                return {"op": op, "results": d.dex_standard_battle(
                    params.get("a", ""), params.get("b", ""))}
            return {"op": op, "error": "unknown_op"}
        except Exception as e:
            return {"op": op, "error": str(e)}

    def _upload(self, body):
        entry = body.get("entry") or {}
        contributor = body.get("contributor", "anonymous")
        # ---- 上传闸门：verified 且验证轨迹完整 ----
        if entry.get("status") != "verified":
            return {"ok": False, "reason": "upload_gate: status 必须为 verified",
                    "name": entry.get("name", "")}
        trail = entry.get("verification_trail") or {}
        if not trail.get("verified_by"):
            return {"ok": False, "reason": "upload_gate: verification_trail.verified_by 必填",
                    "name": entry.get("name", "")}
        if not entry.get("condition_space"):
            return {"ok": False, "reason": "upload_gate: 无明确条件空间不配加入图鉴（P17 收录判据）",
                    "name": entry.get("name", "")}
        d = self.cloud
        nid = d.add_entry(
            name=entry.get("name", "未命名"),
            domain=entry.get("domain", "未分类"),
            claim=entry.get("claim", ""),
            cs=_cs_from_dict(entry.get("condition_space")),
            level=int(entry.get("level", 2)),
            status="verified",
            response=entry.get("response"))
        now = time.time()
        d.store.conn.execute(
            "INSERT OR REPLACE INTO contributions (entry_id, contributor, verified_by, verified_at, weight) "
            "VALUES (?,?,?,?,?)",
            (nid, contributor, trail.get("verified_by"), now,
             float(entry.get("weight", 1.0))))
        d.store.conn.commit()
        cnt = d.store.conn.execute(
            "SELECT COUNT(*) FROM contributions WHERE contributor=?", (contributor,)).fetchone()[0]
        return {"ok": True, "entry_id": nid, "contributor": contributor,
                "contribution_count": cnt}

    def _ledger(self, contributor=None):
        conn = self.cloud.store.conn
        if contributor:
            rows = conn.execute(
                "SELECT entry_id, contributor, verified_by, verified_at, weight "
                "FROM contributions WHERE contributor=?", (contributor,)).fetchall()
        else:
            rows = conn.execute(
                "SELECT entry_id, contributor, verified_by, verified_at, weight "
                "FROM contributions ORDER BY verified_at").fetchall()
        return {"contributions": [
            {"entry_id": r[0], "contributor": r[1], "verified_by": r[2],
             "verified_at": r[3], "weight": r[4]} for r in rows]}

    def _status(self):
        from aeis.core import MemoryLayer
        d = self.cloud
        nodes = d.store.query_nodes(layer=MemoryLayer.KNOWLEDGE, limit=1000)
        total = len(nodes)
        verified = sum(1 for n in nodes
                       if n.state_attributes.get("status") == "verified")
        domains = {}
        for n in nodes:
            dom = n.state_attributes.get("domain", "未知")
            domains[dom] = domains.get(dom, 0) + 1
        contrib = d.store.conn.execute(
            "SELECT COUNT(*) FROM contributions").fetchone()[0]
        return {"total_entries": total, "verified": verified,
                "domains": domains, "contributions": contrib}


def run_server(port=0, db_path=None):
    """启动 mock 云（daemon 线程）。port=0 → 自动分配空闲端口。返回 (server, dex)。"""
    db = db_path or CLOUD_DB
    if os.path.exists(db):
        os.remove(db)  # v0 mock：每次全新
    dex = ConditionDex(db_path=db, fresh=True)
    dex.seed_base()
    dex.store.conn.execute(
        "CREATE TABLE IF NOT EXISTS contributions ("
        "entry_id TEXT PRIMARY KEY, contributor TEXT, verified_by TEXT, "
        "verified_at REAL, weight REAL)")
    dex.store.conn.commit()

    DexHandler.cloud = dex
    srv = ThreadingHTTPServer(("127.0.0.1", port), DexHandler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv, dex


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 18766
    srv, _dex = run_server(port=port)
    print(f"智慧之书 mock 云运行于 http://127.0.0.1:{srv.server_address[1]}")
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        srv.shutdown()
