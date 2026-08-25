# -*- coding: utf-8 -*-
"""verifier.py · 白箱本地校验器（Zero-LLM Verifier）v1

目标：把「白箱写代码 → 外部校验（是否符合规范/能否执行）」全部本地化，
彻底抛开大模型依赖。重复校验走本地缓存（替代 99.9% 的 LLM 缓存命中）。

设计：docs/白箱本地校验器_ZeroLLM_Verifier.md

校验链（六层，全部确定性）：
  ① 校验指纹 → 本地缓存（已校验过 → 直接返回）
  ② L1 语法：ast.parse + 结构规则
  ③ L2 样例：输入→期望断言运行（物理基底裁决）
  ④ L3 边界：额外边界用例
  ⑤ 规范符合性：condition_kb 语义对齐 + 结构规范（白箱规则）
  ⑥ 集成测试：依赖单元组装 + 回归

用法：
  python verifier.py --verify "os_112|工作窃取|<code文件路径>"   # 校验单个
  python verifier.py --cache-stats                                # 缓存统计
  python verifier.py --self-test                                   # 自测
"""
from __future__ import annotations

import ast
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import traceback
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

CACHE_FILE = os.path.join(HERE, "..", "data", "verify_cache.json")
DATA_DIR = os.path.join(HERE, "..", "data")


# ============ 一、数据结构 ============

@dataclass
class VerifyRequest:
    """校验请求：白箱生成的代码 + 单元定义。

    cases/deps 做深拷贝（不可变快照）——被校验代码可能原地修改输入
    （如排序 arr[j], arr[j+1] = ...），若引用外部共享 list 会污染原始数据，
    导致相同请求产生不同指纹（缓存失效）。
    """
    task: str                       # 任务描述（排序/循环编译/图遍历…）
    code: str                       # 白箱生成的代码
    unit_id: str = ""               # 单元标识（域+序号，如 os_112）
    lang: str = "python"            # 语言
    cases: List[Tuple[Any, Any]] = field(default_factory=list)  # (输入, 期望)
    deps: List[str] = field(default_factory=list)               # 依赖单元
    expected_structure: Dict[str, Any] = field(default_factory=dict)  # 规范约束

    def __post_init__(self) -> None:
        # 深拷贝可变字段——防止被校验代码原地修改污染外部共享对象
        self.cases = copy.deepcopy(self.cases)
        self.deps = list(self.deps)
        self.expected_structure = dict(self.expected_structure)

    def fingerprint(self) -> str:
        """确定性指纹：相同请求 → 相同指纹（缓存键）。"""
        payload = json.dumps({
            "task": self.task, "code": self.code, "unit_id": self.unit_id,
            "lang": self.lang, "cases": self.cases, "deps": self.deps,
            "structure": self.expected_structure,
        }, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


@dataclass
class VerifyResult:
    """校验结果。"""
    ok: bool
    checks: List[Dict[str, Any]] = field(default_factory=list)  # [{level, ok, evidence}]
    fingerprint: str = ""
    cached: bool = False
    reason: str = ""

    def summary(self) -> str:
        parts = [f"✅ 通过" if self.ok else f"❌ 失败"]
        for c in self.checks:
            mark = "✓" if c["ok"] else "✗"
            parts.append(f"{mark} {c['level']}")
        if self.reason:
            parts.append(f"原因: {self.reason}")
        return " | ".join(parts)


# ============ 二、本地缓存（替代 LLM 缓存命中） ============

class VerifyCache:
    """校验结果本地缓存。相同指纹 → 零计算返回。"""

    def __init__(self, path: str = CACHE_FILE):
        self.path = path
        self._data: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        try:
            if os.path.exists(self.path):
                with open(self.path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
        except Exception:
            self._data = {}

    def get(self, fingerprint: str) -> Optional[VerifyResult]:
        entry = self._data.get(fingerprint)
        if entry is None:
            return None
        r = VerifyResult(ok=entry["ok"], fingerprint=fingerprint, cached=True)
        r.checks = entry.get("checks", [])
        r.reason = entry.get("reason", "")
        return r

    def put(self, result: VerifyResult) -> None:
        self._data[result.fingerprint] = {
            "ok": result.ok,
            "checks": result.checks,
            "reason": result.reason,
        }
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=1)
        except Exception:
            pass

    def stats(self) -> Dict[str, Any]:
        n = len(self._data)
        n_pass = sum(1 for v in self._data.values() if v.get("ok"))
        return {"total": n, "passed": n_pass, "failed": n - n_pass}


# ============ 三、校验器 ============

class Verifier:
    """本地校验器：六层校验链，零 LLM。"""

    def __init__(self, cache: Optional[VerifyCache] = None):
        self.cache = cache or VerifyCache()

    # ---------- 主入口 ----------
    def verify(self, req: VerifyRequest) -> VerifyResult:
        # 不可变快照：verify 内部运行样例可能原地修改输入（如排序
        # arr[j], arr[j+1] = ...），必须深拷贝防止污染原始 req 对象
        # （否则同一 req 第二次校验指纹变化，缓存失效）
        req = copy.deepcopy(req)
        fp = req.fingerprint()

        # ① 缓存命中 → 直接返回
        cached = self.cache.get(fp)
        if cached is not None:
            return cached

        checks: List[Dict[str, Any]] = []

        # ② L1 语法
        checks.append(self._check_l1_syntax(req))

        # ③ L2 样例（语法通过才运行）
        if checks[-1]["ok"]:
            checks.append(self._check_l2_samples(req))

        # ④ L3 边界
        if checks[-1]["ok"]:
            checks.append(self._check_l3_boundary(req))

        # ⑤ 规范符合性
        checks.append(self._check_spec_compliance(req))

        # ⑥ 集成测试（有 deps 才做）
        if req.deps:
            checks.append(self._check_integration(req))

        ok = all(c["ok"] for c in checks)
        reason = ""
        if not ok:
            failed = [c for c in checks if not c["ok"]]
            reason = failed[0]["evidence"] if failed else "未知失败"

        result = VerifyResult(ok=ok, checks=checks, fingerprint=fp, reason=reason)
        # 写缓存
        self.cache.put(result)
        return result

    # ---------- L1 语法 ----------
    def _check_l1_syntax(self, req: VerifyRequest) -> Dict[str, Any]:
        """ast.parse + 结构规则（函数定义/占位残留/括号平衡）。"""
        code = req.code
        # 语法解析
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {"level": "L1语法", "ok": False,
                    "evidence": f"语法错误: {e}"}

        # 结构规则
        errors = []
        funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        if not funcs:
            errors.append("无函数定义")
        # 占位残留（{fn} 等模板占位符未替换）
        if "{fn}" in code or "{param" in code:
            errors.append("存在未替换的模板占位符")
        # 括号平衡（ast 通过即平衡，冗余检查）
        if code.count("(") != code.count(")"):
            errors.append("括号不平衡")
        # 禁止裸 import（白箱代码应自包含）——但允许标准库
        imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
        STDLIB_OK = {"collections", "typing", "functools", "itertools", "math",
                     "random", "json", "re", "string", "dataclasses", "abc"}
        if imports and not req.expected_structure.get("allow_import"):
            bad = []
            for n in imports:
                if isinstance(n, ast.ImportFrom):
                    top = (n.module or "").split(".")[0]
                    if top and top not in STDLIB_OK:
                        bad.append(n.module)
                else:
                    for alias in n.names:
                        top = alias.name.split(".")[0]
                        if top not in STDLIB_OK:
                            bad.append(alias.name)
            if bad:
                return {"level": "L1语法", "ok": False,
                        "evidence": f"存在非标准库导入: {bad}"}

        if errors:
            return {"level": "L1语法", "ok": False, "evidence": "; ".join(errors)}
        return {"level": "L1语法", "ok": True,
                "evidence": f"语法通过（{len(funcs)} 个函数定义）"}

    # ---------- L2 样例 ----------
    def _check_l2_samples(self, req: VerifyRequest) -> Dict[str, Any]:
        """每个 (输入, 期望) 运行断言。"""
        if not req.cases:
            return {"level": "L2样例", "ok": True, "evidence": "无样例（跳过）"}

        ns: Dict[str, Any] = {}
        try:
            exec(compile(req.code, "<verify>", "exec"), ns)
        except Exception as e:
            return {"level": "L2样例", "ok": False,
                    "evidence": f"代码编译/执行失败: {e}"}

        # 找被测函数（第一个函数定义）
        func_name = None
        try:
            tree = ast.parse(req.code)
            funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            func_name = funcs[0].name if funcs else None
        except Exception:
            pass

        if not func_name or func_name not in ns:
            return {"level": "L2样例", "ok": False,
                    "evidence": f"找不到被测函数（期望 {func_name}）"}

        fn = ns[func_name]
        for case_idx, (inp, exp) in enumerate(req.cases, 1):
            try:
                got = fn(inp) if not isinstance(inp, tuple) else fn(*inp)
            except Exception as e:
                return {"level": "L2样例", "ok": False,
                        "evidence": f"样例{case_idx} 崩溃: {inp} → {e}"}
            if got != exp:
                return {"level": "L2样例", "ok": False,
                        "evidence": f"样例{case_idx} 失败: {inp} → {got}（期望 {exp}）"}
        return {"level": "L2样例", "ok": True,
                "evidence": f"{len(req.cases)} 组样例全部通过"}

    # ---------- L3 边界 ----------
    def _check_l3_boundary(self, req: VerifyRequest) -> Dict[str, Any]:
        """额外边界用例：None/空/极端值。"""
        extra_cases = self._gen_boundary_cases(req.task)
        if not extra_cases:
            return {"level": "L3边界", "ok": True, "evidence": "无额外边界用例"}

        ns: Dict[str, Any] = {}
        try:
            exec(compile(req.code, "<verify>", "exec"), ns)
        except Exception as e:
            return {"level": "L3边界", "ok": False, "evidence": f"执行失败: {e}"}

        func_name = None
        try:
            tree = ast.parse(req.code)
            funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            func_name = funcs[0].name if funcs else None
        except Exception:
            pass

        if not func_name or func_name not in ns:
            return {"level": "L3边界", "ok": True, "evidence": "跳过（无函数）"}

        fn = ns[func_name]
        for case_idx, (inp, exp) in enumerate(extra_cases, 1):
            try:
                got = fn(inp) if not isinstance(inp, tuple) else fn(*inp)
            except Exception as e:
                # 边界用例允许异常返回（如空列表→None/报错均可接受）
                if exp == "any":
                    continue
                return {"level": "L3边界", "ok": False,
                        "evidence": f"边界用例{case_idx} 崩溃: {inp} → {e}"}
            if exp != "any" and got != exp:
                return {"level": "L3边界", "ok": False,
                        "evidence": f"边界用例{case_idx} 失败: {inp} → {got}（期望 {exp}）"}
        return {"level": "L3边界", "ok": True,
                "evidence": f"{len(extra_cases)} 组边界用例通过"}

    def _gen_boundary_cases(self, task: str) -> List[Tuple[Any, Any]]:
        """根据任务类型生成边界用例（白箱规则，非 LLM）。"""
        t = task.lower()
        if any(w in t for w in ("排序", "sort", "去重", "dedup", "反转", "reverse")):
            return [([], []), ([1], [1]), (None, "any")]
        if any(w in t for w in ("最大", "max", "最小", "min")):
            return [([], None), ([5], 5), (None, "any")]  # 空列表→None（与单元语义一致）
        if any(w in t for w in ("求和", "sum")):
            return [([], 0), (None, "any")]
        if any(w in t for w in ("计数", "count", "频率", "freq")):
            return [([], {}), (None, "any")]  # Counter 语义：空列表 → {}
        return []

    # ---------- ⑤ 规范符合性（白箱规则 + condition_kb） ----------
    def _check_spec_compliance(self, req: VerifyRequest) -> Dict[str, Any]:
        """结构规范 + 语义对齐（condition_kb 查条件路由表）。"""
        errors = []

        # 结构规范：任务关键词 → 应包含的结构（白箱规则）
        structure_rules = {
            "排序": ["<", ">"], "sort": ["<", ">"],
            "去重": ["set", "seen"], "dedup": ["set", "seen"],
            "循环": ["while", "for"], "loop": ["while", "for"],
            "递归": ["def", "recurs"], "递归函数": ["return"],
            "反转": ["::-1", "reverse"],
        }
        for kw, patterns in structure_rules.items():
            if kw in req.task and req.expected_structure.get("skip_structure"):
                continue
            if kw in req.task:
                hit = any(p in req.code for p in patterns)
                if not hit and not req.expected_structure.get("structure_optional"):
                    errors.append(f"任务含「{kw}」但代码未见对应结构 {patterns}")

        # 语义对齐：condition_kb 查该任务的条件规律，代码应有对应处理
        try:
            from condition_kb import ConditionKB
            kb = ConditionKB()
            sem = kb.lookup(req.task)
            if sem and sem.get("match"):
                # 查到的规律描述包含条件词 → 代码应体现条件分支
                cond_words = ["如果", "若", "when", "if", "条件", "情况"]
                has_cond = any(w in req.code for w in cond_words)
                if any(w in sem.get("match", "") for w in ["条件", "如果", "当"]) \
                        and not has_cond \
                        and not req.expected_structure.get("no_cond_needed"):
                    errors.append(f"condition_kb 提示「{sem.get('match', '')[:30]}」需条件处理但代码无分支")
        except Exception:
            pass  # condition_kb 不可用时跳过（不影响主校验）

        if errors:
            return {"level": "规范符合性", "ok": False, "evidence": "; ".join(errors)}
        return {"level": "规范符合性", "ok": True,
                "evidence": "结构规范 + 语义对齐通过"}

    # ---------- ⑥ 集成测试 ----------
    def _check_integration(self, req: VerifyRequest) -> Dict[str, Any]:
        """依赖单元组装 + 端到端运行（简化：deps 代码拼接后执行）。"""
        if not req.deps:
            return {"level": "集成", "ok": True, "evidence": "无依赖（跳过）"}
        try:
            # 组装依赖 + 被测代码
            combined = "\n\n".join(req.deps) + "\n\n" + req.code
            ns: Dict[str, Any] = {}
            exec(compile(combined, "<integrate>", "exec"), ns)

            # 端到端：跑第一个样例
            if req.cases:
                func_name = None
                tree = ast.parse(req.code)
                funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
                func_name = funcs[0].name if funcs else None
                if func_name and func_name in ns:
                    inp, exp = req.cases[0]
                    got = ns[func_name](inp) if not isinstance(inp, tuple) else ns[func_name](*inp)
                    if got != exp:
                        return {"level": "集成", "ok": False,
                                "evidence": f"组装后首样例失败: {inp} → {got}（期望 {exp}）"}
            return {"level": "集成", "ok": True,
                    "evidence": f"{len(req.deps)} 个依赖组装 + 端到端通过"}
        except Exception as e:
            return {"level": "集成", "ok": False,
                    "evidence": f"组装失败: {e}"}


# ============ 四、CLI ============

def _build_request_from_file(path: str) -> VerifyRequest:
    """从 JSON 文件构建校验请求。"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return VerifyRequest(
        task=data.get("task", ""),
        code=data.get("code", ""),
        unit_id=data.get("unit_id", ""),
        lang=data.get("lang", "python"),
        cases=[tuple(c) for c in data.get("cases", [])],
        deps=data.get("deps", []),
        expected_structure=data.get("structure", {}),
    )


def _self_test() -> bool:
    """自测：排序单元应通过，错误代码应失败。"""
    v = Verifier()
    passed = 0

    # 正确代码
    good_code = (
        "def solve(arr):\n"
        "    n = len(arr)\n"
        "    for i in range(n):\n"
        "        for j in range(n-1-i):\n"
        "            if arr[j] > arr[j+1]:\n"
        "                arr[j], arr[j+1] = arr[j+1], arr[j]\n"
        "    return arr\n"
    )
    r1 = v.verify(VerifyRequest(
        task="排序", code=good_code, unit_id="test_sort",
        cases=[([3, 1, 2], [1, 2, 3]), ([], []), ([1], [1])],
    ))
    print(f"[1] 排序正确代码: {r1.summary()}")
    passed += 1 if r1.ok else 0

    # 错误代码（冒泡逻辑反了）
    bad_code = good_code.replace("if arr[j] > arr[j+1]", "if arr[j] < arr[j+1]")
    r2 = v.verify(VerifyRequest(
        task="排序", code=bad_code, unit_id="test_sort_bad",
        cases=[([3, 1, 2], [1, 2, 3]), ([], []), ([1], [1])],
    ))
    print(f"[2] 排序错误代码: {r2.summary()}")
    passed += 1 if not r2.ok else 0

    # 缓存命中
    r3 = v.verify(VerifyRequest(
        task="排序", code=good_code, unit_id="test_sort",
        cases=[([3, 1, 2], [1, 2, 3]), ([], []), ([1], [1])],
    ))
    print(f"[3] 缓存命中: cached={r3.cached} {r3.summary()}")
    passed += 1 if r3.cached else 0

    # 语法错误
    r4 = v.verify(VerifyRequest(
        task="排序", code="def solve(arr):\n  return ", unit_id="test_syntax",
        cases=[([1], [1])],
    ))
    print(f"[4] 语法错误: {r4.summary()}")
    passed += 1 if not r4.ok else 0

    # 规范符合性（排序但无比较结构）
    r5 = v.verify(VerifyRequest(
        task="排序", code="def solve(arr):\n    return arr", unit_id="test_nosort",
        cases=[([3, 1, 2], [3, 1, 2])],
    ))
    print(f"[5] 规范不符（排序无比较）: {r5.summary()}")
    passed += 1 if not r5.ok else 0

    print(f"\n自测: {passed}/5 通过")
    return passed == 5


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description="白箱本地校验器（零 LLM）")
    ap.add_argument("--verify", type=str, help="校验请求 JSON 文件路径")
    ap.add_argument("--cache-stats", action="store_true", help="缓存统计")
    ap.add_argument("--self-test", action="store_true", help="自测")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(0 if _self_test() else 1)

    if args.cache_stats:
        stats = VerifyCache().stats()
        print(f"缓存统计: 共 {stats['total']} 条（通过 {stats['passed']} / 失败 {stats['failed']}）")
        return

    if args.verify:
        req = _build_request_from_file(args.verify)
        result = Verifier().verify(req)
        print(json.dumps(asdict(result), ensure_ascii=False, indent=1))
        return

    ap.print_help()


if __name__ == "__main__":
    main()
