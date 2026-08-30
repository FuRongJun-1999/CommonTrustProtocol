# -*- coding: utf-8 -*-
"""template_catalog.py · 分层模板目录 + 条件采样器（模板生成引擎 V-TBE.1 前置）

荣洞察（2026-08-30 v0.2）：一张图由细节组合而成——骨架→姿态→外表→细节。
图像 = 四个子条件空间的逐层叠加；分层后组合爆炸化为组合乘法：
n₁+n₂+n₃+n₄ 个模板覆盖 n₁×n₂×n₃×n₄ 种组合图像。

设计文档：docs/模板生成引擎设计_v0.2.md（分层模板模型）
验收：V-TBE.7 分层采样（组合描述无歧义）/ V-TBE.10 组合覆盖可查询。
纯标准库（D-005），无生图 API 依赖（扩散仅在 L4 细节层接入，v0.3）。
"""
from __future__ import annotations

from itertools import product
from typing import Dict, List, Optional

# 四层定义（v0.2 分层模板模型）
LAYERS = ("L1_skeleton", "L2_pose", "L3_appearance", "L4_detail")
LAYER_NAMES = {"L1_skeleton": "骨架", "L2_pose": "姿态",
               "L3_appearance": "外表", "L4_detail": "细节"}


class TemplateCatalog:
    """分层模板目录：每层是独立子条件空间，模板=该层的条件原型。"""

    def __init__(self, name: str = "default"):
        self.name = name
        self._templates: Dict[str, List[dict]] = {k: [] for k in LAYERS}

    def register(self, layer: str, template_id: str, desc: dict,
                 conditions: Optional[dict] = None) -> dict:
        """登记分层模板。desc=该层条件描述（如骨架关节/姿态角度/颜色纹理）。
        conditions=适用条件（层间耦合用，如某细节仅适用特定骨架——诚实边界：
        不强行解耦，条件关联显式记录）。"""
        if layer not in LAYERS:
            raise ValueError(f"未知层 {layer}（可用: {LAYERS}）")
        t = {"id": template_id, "desc": desc,
             "conditions": conditions or {}, "layer": layer}
        self._templates[layer].append(t)
        return t

    def list(self, layer: str) -> List[dict]:
        if layer not in LAYERS:
            raise ValueError(f"未知层 {layer}")
        return list(self._templates[layer])

    def counts(self) -> Dict[str, int]:
        return {k: len(v) for k, v in self._templates.items()}

    def combo_space(self) -> int:
        """组合覆盖空间 = n₁×n₂×n₃×n₄（组合爆炸→组合乘法的度量）。"""
        c = self.counts()
        n = 1
        for k in LAYERS:
            n *= max(1, c[k])
        return n

    # ---- 持久化（目录可保存/加载——模板库增量增长的基础）----
    def to_dict(self) -> dict:
        return {"name": self.name,
                "templates": {k: list(v) for k, v in self._templates.items()}}

    @classmethod
    def from_dict(cls, d: dict) -> "TemplateCatalog":
        cat = cls(d.get("name", "default"))
        for layer, ts in (d.get("templates") or {}).items():
            if layer in LAYERS:
                cat._templates[layer] = list(ts)
        return cat

    def save(self, path: str) -> None:
        import json
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False)

    @classmethod
    def load(cls, path: str) -> "TemplateCatalog":
        import json
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    # ---- 验证闸（V-TBE.8 主仓库侧·识别方向逻辑半边）----
    # 观测签名逐层比对模板 → 匹配度 + 四态判定。
    # 图像→签名的提取半边在 AEIS 身体库（stage4 管线），此处为纯逻辑比对。
    @staticmethod
    def _desc_match(observed: dict, template_desc: dict) -> float:
        """desc 匹配度：键值交集 / 模板键数（0~1）。空模板视为通配=1。"""
        if not template_desc:
            return 1.0
        if not isinstance(observed, dict):
            return 0.0
        hit = sum(1 for k, v in template_desc.items() if observed.get(k) == v)
        return hit / len(template_desc)

    def verify(self, observed: Dict[str, dict], threshold: float = 0.5) -> dict:
        """观测签名 → 逐层匹配模板 → 四态判定（语义识别=分层模板匹配）。
        observed={layer: {desc 键值}}（来自提取管线；缺层记 BLINDSPOT）。
        判定：全层达标=ACCEPT；过半达标=DEFER；其余=REJECT；
        缺层=BLINDSPOT（诚实边界：没看到的不假装看到）。"""
        layers_report = {}
        matched = 0
        blindspot = False
        for layer in LAYERS:
            obs = observed.get(layer)
            if obs is None:
                layers_report[layer] = {"status": "BLINDSPOT", "best": None,
                                        "score": None}
                blindspot = True
                continue
            best_id, best_score = None, 0.0
            for t in self._templates[layer]:
                sc = self._desc_match(obs, t["desc"])
                if sc > best_score:
                    best_id, best_score = t["id"], sc
            ok = best_score >= threshold
            matched += 1 if ok else 0
            layers_report[layer] = {"status": "ACCEPT" if ok else "REJECT",
                                    "best": best_id,
                                    "score": round(best_score, 3)}
        if blindspot:
            verdict = "BLINDSPOT"
        elif matched == len(LAYERS):
            verdict = "ACCEPT"
        elif matched >= len(LAYERS) / 2:
            verdict = "DEFER"
        else:
            verdict = "REJECT"
        return {"verdict": verdict, "matched": matched,
                "layers": layers_report}

    def sample(self, picks: Optional[Dict[str, str]] = None,
               rng=None) -> dict:
        """条件采样：四层各取一模板 → 组合描述（V-TBE.7）。
        picks=指定各层模板 id（缺省每层取第一个；rng 提供时随机取）。"""
        picks = picks or {}
        combo = {}
        for layer in LAYERS:
            ts = self._templates[layer]
            if not ts:
                raise ValueError(f"{LAYER_NAMES[layer]}层无模板（条件链不完整）")
            pid = picks.get(layer)
            t = next((x for x in ts if x["id"] == pid), None) if pid else (
                rng.choice(ts) if rng else ts[0])
            if t is None:
                raise ValueError(f"{layer} 无模板 {pid}")
            combo[layer] = {"id": t["id"], "desc": t["desc"]}
        return {"layers": combo,
                "summary": " + ".join(f"{LAYER_NAMES[l]}[{combo[l]['id']}]"
                                      for l in LAYERS)}

    def sample_all(self, limit: int = 100) -> List[dict]:
        """全组合枚举（上限 limit 防爆——组合空间大时用采样）。"""
        pools = [self._templates[l] for l in LAYERS]
        out = []
        for pick in product(*pools):
            if len(out) >= limit:
                break
            out.append({"layers": {l: {"id": p["id"], "desc": p["desc"]}
                                   for l, p in zip(LAYERS, pick)},
                        "summary": " + ".join(f"{LAYER_NAMES[l]}[{p['id']}]"
                                              for l, p in zip(LAYERS, pick))})
        return out


# ---- 冒烟（V-TBE.7 前置：目录/采样/组合覆盖） ----
if __name__ == "__main__":
    import random
    cat = TemplateCatalog("smoke")
    # 10 骨架 × 20 姿态 × 30 外表 × 15 细节 = 90000 组合，75 模板（v0.2 论证）
    for i in range(10):
        cat.register("L1_skeleton", f"skel_{i}", {"joints": i})
    for i in range(20):
        cat.register("L2_pose", f"pose_{i}", {"angles": i})
    for i in range(30):
        cat.register("L3_appearance", f"app_{i}", {"color": i})
    for i in range(15):
        cat.register("L4_detail", f"det_{i}", {"pattern": i})
    assert cat.combo_space() == 10 * 20 * 30 * 15 == 90000
    s = cat.sample()
    assert len(s["layers"]) == 4 and "骨架" in s["summary"]
    rng = random.Random(42)
    for _ in range(100):
        s2 = cat.sample(rng=rng)          # V-TBE.7：100 组采样无歧义
        assert len(s2["layers"]) == 4
    combos = cat.sample_all(limit=100)
    assert len(combos) == 100
    # 条件关联（层间耦合不强行解耦）
    cat.register("L4_detail", "det_bone", {"pattern": "bone"},
                 conditions={"L1_skeleton": "skel_0"})
    assert cat.list("L4_detail")[-1]["conditions"]["L1_skeleton"] == "skel_0"
    print(f"template_catalog 冒烟: 目录 4 层 75 模板，组合空间 "
          f"{cat.combo_space()}，采样 100 组全过 ✓")
