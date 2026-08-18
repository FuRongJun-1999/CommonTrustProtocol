# -*- coding: utf-8 -*-
"""灵枢 · 因果候选生成器 causal_discover（v1.16 · R 维进化）

设计（爸爸：条件论对自身的使用）：
  用条件论七操作处理**系统自身的行为数据**（被拒路径/预测未命中），
  生成因果假设 → 结合物理信息基底校准（可观测预测 → 验证回路）给出因果分析。

七操作映射：
  识别 ← 扫描被拒路径/预测未命中 → 异常模式（系统失败的输入=未知因果线索）
  声明 ← 异常 → 候选因果主张（带条件空间）
  组合 ← 相似被拒路径聚合 → 同原因多次失败 = 强因果信号
  分离 ← dex_analyze 七操作剥离混淆（逆转测试查因果方向/统计卡查证据）
  逆转 ← 因果方向检查（A→B 还是 B→A 还是第三变量）
  循环 ← 输出可观测预测 → 验证回路（物理基底）→ 命中强化/未命中否决

输出：因果候选（条件空间声明 + 可验证预测），交验证回路 + 设计者终裁 → causal 边入图。
"""
import os
import sys
import re
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


class CausalDiscoverer:
    """条件论七操作对自身：行为数据 → 因果候选 → 可验证预测。"""

    def __init__(self, engine, dex=None):
        self.engine = engine
        self.dex = dex  # 智慧之书 ConditionDex（供分离/逆转检查）

    # ---------------- 识别（反向·识别操作） ----------------
    def _scan_anomalies(self, limit=8):
        """扫描异常模式：open 被拒路径（系统在这些输入上失败）。
        被拒路径 = 预测/处理失败的输入——未知因果的线索。"""
        anomalies = []
        try:
            paths = self.engine.list_rejected_paths(status="open") if hasattr(
                self.engine, "list_rejected_paths") else []
            # 按 description 聚类（同原因多次失败）
            clusters = {}
            for p in paths:
                desc = (p.get("description") or "")[:60]
                key = desc[:20]
                clusters.setdefault(key, []).append(p)
            for key, group in clusters.items():
                anomalies.append({
                    "type": "rejected_path_cluster",
                    "description": key,
                    "count": len(group),
                    "reasons": list(dict.fromkeys(
                        (p.get("reason") or "")[:30] for p in group))[:3],
                    "evidence": group[0].get("evidence", ""),
                })
        except Exception:
            pass
        # 预测未命中（hit_history 尾部 false）
        try:
            hist = getattr(getattr(self.engine, "_prediction", None),
                           "_hit_history", []) or []
            misses = sum(1 for h in hist[-20:] if not h)
            if misses >= 3:
                anomalies.append({
                    "type": "prediction_miss",
                    "description": f"近20次预测未命中 {misses} 次",
                    "count": misses,
                    "reasons": ["预测-验证闭环持续未命中=未知机制"],
                    "evidence": "hit_history",
                })
        except Exception:
            pass
        return anomalies[:limit]

    # ---------------- 声明（反向·声明操作） ----------------
    def _declare_candidate(self, anomaly):
        """异常 → 候选因果主张（条件空间声明）。"""
        desc = anomaly["description"] or ""
        reason = (anomaly.get("reasons") or ["未知"])[0]
        return {
            "claim": f"「{desc}」与「{reason}」可能存在因果相关（重复失败=机制性原因而非偶然）",
            "type": "causal_candidate",
            "condition_space": {
                "observation_position": "灵枢行为观测层（被拒路径/预测反馈）",
                "observation_tool": "rejected_paths 聚类 + hit_history 分析",
                "time_window": [0.0, time.time()],
                "existence_constraint": f"候选未验证——仅在重复失败 {anomaly.get('count',1)} 次的证据下成立，需物理基底验证",
            },
            "source_anomaly": anomaly,
        }

    # ---------------- 分离 + 逆转（dex_analyze 七操作） ----------------
    def _separate_invert(self, candidate):
        """剥离混淆 + 因果方向检查（复用智慧之书 dex_analyze 的七操作）。
        逆转：排除逆向因果与第三变量（_t_invert 语义）。"""
        checks = []
        if self.dex is not None:
            try:
                ana = self.dex.dex_analyze(candidate["claim"], limit=3)
                premises = ana.get("premises", [])
                has_causal = any(p.get("type") == "因果声称" for p in premises)
                checks.append({"check": "因果声称识别", "found": has_causal})
                invert = ana.get("invert", {}).get("status", "")
                checks.append({"check": "逆转测试", "status": invert})
            except Exception as e:
                checks.append({"check": "dex_analyze", "error": str(e)[:40]})
        else:
            # 无 dex：规则化逆转检查（含因果词且可证伪）
            has_causal = bool(re.search(r"因果|导致|相关|因为", candidate["claim"]))
            checks.append({"check": "因果声称识别", "found": has_causal})
            checks.append({"check": "逆转测试",
                           "status": "需验证：因果方向非唯一，需排除逆向因果与第三变量"})
        candidate["separation_checks"] = checks
        return candidate

    # ---------------- 循环（可观测预测 → 物理基底） ----------------
    def _cycle_predictions(self, candidate):
        """生成可观测预测——物理信息基底校准的输入。
        如果因果成立（A→B），则在 X 条件下应观察到 Y；预测可执行/可观测。
        交 prediction_feedback 验证：命中强化 / 未命中否决。"""
        desc = (candidate.get("source_anomaly") or {}).get("description", "")
        return {
            "candidate_id": f"cc_{abs(hash(candidate['claim'])) % 10**8}",
            "claim": candidate["claim"],
            "predictions": [
                {"observable": f"重复处理同特征输入，若机制性原因存在，失败模式应可复现",
                 "verify_method": "prediction_feedback（验证回路）",
                 "expected": "复现→强化候选；不复现→否决（偶然）"},
                {"observable": f"补足缺失知识后，同类输入应转为成功",
                 "verify_method": "设计者终裁 + 图谱检索",
                 "expected": "补足后成功→因果确认；仍失败→候选错误"},
            ],
            "condition_space": candidate["condition_space"],
            "note": "物理基底校准：因果候选必须通过可观测预测验证，非仅逻辑自洽",
        }

    # ---------------- 主流程 ----------------
    def discover(self, limit=5):
        """七操作对自身：识别→声明→分离/逆转→循环。
        返回因果候选（带可验证预测），交验证回路 + 设计者终裁。"""
        # 1. 识别
        anomalies = self._scan_anomalies(limit=limit)
        if not anomalies:
            return {"candidates": [], "note": "无异常模式（无因果候选信号）"}
        # 2. 声明
        candidates = [self._declare_candidate(a) for a in anomalies]
        # 3. 分离 + 逆转
        for c in candidates:
            self._separate_invert(c)
        # 4. 循环（可观测预测）
        outputs = [self._cycle_predictions(c) for c in candidates]
        return {
            "candidates": outputs,
            "note": ("条件论对自身的使用：七操作处理自身行为数据（被拒路径/预测未命中）"
                     "→ 因果候选 → 可观测预测 → 验证回路（物理基底校准）→ 终裁入图"),
        }


# ---------------- 自测 ----------------
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    from aeis.api import Agent
    agent = Agent(identity="灵枢",
                  db_path=r'C:\Users\FuRongJun\.dsh\profiles\web\data\lingshu.db')
    # 注入一条被拒路径作为信号
    try:
        agent.engine.register_rejected_path(
            "query", "用户问「水为什么烧开」检索不到沸点知识", "翻译表缺沸点→沸腾映射",
            evidence="extend_test")
        agent.engine.register_rejected_path(
            "query", "用户问「为什么下雨前蚂蚁搬家」图谱无此常识", "常识卡缺失",
            evidence="extend_test")
    except Exception:
        pass
    discoverer = CausalDiscoverer(agent.engine, dex=agent._get_wisdom())
    result = discoverer.discover(limit=3)
    print("=== 因果候选生成器（条件论对自身）===")
    for c in result.get("candidates", []):
        print(f"\n候选 {c['candidate_id']}: {c['claim'][:50]}")
        for s in c.get("separation_checks", []):
            print(f"  分离/逆转: {s}")
        for p in c.get("predictions", []):
            print(f"  预测: {p['observable'][:40]}... ({p['verify_method']})")
    print(f"\n{result['note']}")
    agent.close()
