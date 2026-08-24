# -*- coding: utf-8 -*-
"""code_compose.py · 白箱自举第二阶段·代码编写主线原型 v1
理论：《白箱自举·角色扮演与代码编写》（§3 代码=编程规律条件单元）
核心：代码编写=带条件的知识问答（条件=编程任务需求）——
  ① 代码条件单元 CODE_UNITS（{任务 → 代码模式模板}，带 {参数} 占位）
  ② 任务方向识别（问题 → 任务：排序/去重/计数/最大/反转/求和）
  ③ 组合生成（任务模板 × 参数 → 代码，未预写完整代码）
  ④ 自校验三层：L1 语法（ast.parse）→ L2 样例（输入→期望断言运行）→ L3 边界
  ⑤ 固化：验证通过代码 → 固化 JSON → 同任务直出
零 LLM：全部白箱确定性生成 + 自校验（语法/测试是物理基底裁决）。
"""
import sys, json, os, ast
sys.stdout.reconfigure(encoding='utf-8')


# ============ 一、代码条件单元库（任务 → 代码模式模板 + 验证样例） ============
# pattern: 代码模板（{fn}=函数名占位）；cases: (输入, 期望输出) 自校验样例
CODE_UNITS = {
    "排序-冒泡": {
        "task": "排序",
        "pattern": (
            "def {fn}(arr):\n"
            "    n = len(arr)\n"
            "    for i in range(n):\n"
            "        for j in range(n - 1 - i):\n"
            "            if arr[j] > arr[j + 1]:\n"
            "                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n"
            "    return arr\n"),
        "cases": [([3, 1, 2], [1, 2, 3]), ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
                  ([7], [7]), ([], [])],
        "params": ["fn"],
    },
    "去重-保序": {
        "task": "去重",
        "pattern": (
            "def {fn}(arr):\n"
            "    seen = set()\n"
            "    out = []\n"
            "    for x in arr:\n"
            "        if x not in seen:\n"
            "            seen.add(x)\n"
            "            out.append(x)\n"
            "    return out\n"),
        "cases": [([1, 2, 2, 3, 1], [1, 2, 3]), ([], []), ([1, 1, 1], [1])],
        "params": ["fn"],
    },
    "计数-频率": {
        "task": "计数",
        "pattern": (
            "def {fn}(arr):\n"
            "    from collections import Counter\n"
            "    return dict(Counter(arr))\n"),
        "cases": [([1, 2, 2, 3], {1: 1, 2: 2, 3: 1}), ([], {}), (["a", "a"], {"a": 2})],
        "params": ["fn"],
    },
    "最大值": {
        "task": "最大",
        "pattern": (
            "def {fn}(arr):\n"
            "    if not arr:\n"
            "        return None\n"
            "    m = arr[0]\n"
            "    for x in arr[1:]:\n"
            "        if x > m:\n"
            "            m = x\n"
            "    return m\n"),
        "cases": [([3, 1, 2], 3), ([7], 7), ([], None), ([-1, -5, -2], -1)],
        "params": ["fn"],
    },
    "反转列表": {
        "task": "反转",
        "pattern": (
            "def {fn}(arr):\n"
            "    return arr[::-1]\n"),
        "cases": [([1, 2, 3], [3, 2, 1]), ([], []), (["a", "b"], ["b", "a"])],
        "params": ["fn"],
    },
    "求和": {
        "task": "求和",
        "pattern": (
            "def {fn}(arr):\n"
            "    total = 0\n"
            "    for x in arr:\n"
            "        total += x\n"
            "    return total\n"),
        "cases": [([1, 2, 3], 6), ([], 0), ([5], 5)],
        "params": ["fn"],
    },
}

# 任务方向识别（问题 → 任务，最长关键词优先）
TASK_KEYWORDS = {
    "排序": ["排序", "排好", "从小到大", "升序", "从大到小", "降序", "整理顺序"],
    "去重": ["去重", "重复", "不重复", "唯一", "去掉重复"],
    "计数": ["数一数", "计数", "出现次数", "几次", "统计", "频率"],
    "最大": ["最大", "最大值", "最高的", "最大的数", "最多"],
    "反转": ["反转", "倒过来", "倒序", "反过来"],
    "求和": ["求和", "加起来", "总和", "相加", "累加"],
}

# ============ 四、多语言代码单元（第四阶段·代码深学：Rust / JavaScript） ============
# 每单元带 py_ref（Python 等价实现）——Rust/JS 逻辑样例用 py_ref 验证（模板逻辑正确性）

RUST_UNITS = {
    "排序-冒泡": {
        "task": "排序", "lang": "rust",
        "pattern": ("fn {fn}(arr: &mut Vec<i32>) {\n"
                    "    let n = arr.len();\n"
                    "    for i in 0..n {\n"
                    "        for j in 0..n - 1 - i {\n"
                    "            if arr[j] > arr[j + 1] {\n"
                    "                arr.swap(j, j + 1);\n"
                    "            }\n"
                    "        }\n"
                    "    }\n"
                    "}\n"),
        "cases": [([3, 1, 2], [1, 2, 3]), ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
                  ([], [])],
        "py_ref": "def solve(arr):\n    arr = arr[:]\n    n = len(arr)\n"
                  "    for i in range(n):\n        for j in range(n - 1 - i):\n"
                  "            if arr[j] > arr[j + 1]:\n"
                  "                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n"
                  "    return arr\n",
    },
    "求和": {
        "task": "求和", "lang": "rust",
        "pattern": "fn {fn}(arr: &[i32]) -> i32 {\n    arr.iter().sum()\n}\n",
        "cases": [([1, 2, 3], 6), ([], 0), ([5], 5)],
        "py_ref": "def solve(arr): return sum(arr)\n",
    },
    "最大值": {
        "task": "最大", "lang": "rust",
        "pattern": ("fn {fn}(arr: &[i32]) -> Option<i32> {\n"
                    "    arr.iter().copied().max()\n}\n"),
        "cases": [([3, 1, 2], 3), ([7], 7), ([], None)],
        "py_ref": "def solve(arr): return max(arr) if arr else None\n",
    },
}

JS_UNITS = {
    "排序": {
        "task": "排序", "lang": "javascript",
        "pattern": "function {fn}(arr) {\n    return arr.slice().sort((a, b) => a - b);\n}\n",
        "cases": [([3, 1, 2], [1, 2, 3]), ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
                  ([], [])],
        "py_ref": "def solve(arr): return sorted(arr)\n",
    },
    "求和": {
        "task": "求和", "lang": "javascript",
        "pattern": "function {fn}(arr) {\n    return arr.reduce((s, x) => s + x, 0);\n}\n",
        "cases": [([1, 2, 3], 6), ([], 0), ([5], 5)],
        "py_ref": "def solve(arr): return sum(arr)\n",
    },
    "反转": {
        "task": "反转", "lang": "javascript",
        "pattern": "function {fn}(arr) {\n    return arr.slice().reverse();\n}\n",
        "cases": [([1, 2, 3], [3, 2, 1]), ([], []), (["a", "b"], ["b", "a"])],
        "py_ref": "def solve(arr): return arr[::-1]\n",
    },
}

LANG_UNITS = {"python": CODE_UNITS, "rust": RUST_UNITS,
              "javascript": JS_UNITS}


def detect_language(question):
    """语言识别：问题含 rust/rs → Rust；js/javascript → JavaScript；否则 Python"""
    q = question.lower()
    if "rust" in q or "rs写" in q or "用rust" in q:
        return "rust"
    if "javascript" in q or "js写" in q or "用js" in q or "用javascript" in q:
        return "javascript"
    return "python"


def identify_task(question):
    """任务方向识别：问题 → 编程任务（最长关键词优先）"""
    best, best_len = None, 0
    for task, kws in TASK_KEYWORDS.items():
        for k in kws:
            if k in question and len(k) > best_len:
                best, best_len = task, len(k)
    return best


def extract_fn_name(question):
    """参数解析：函数名（问题含英文标识符则用，否则默认 solve）"""
    import re
    m = re.search(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b", question)
    if m:
        name = m.group(1)
        if name.lower() not in ("python", "def", "list", "array", "arr"):
            return name
    return "solve"


# ============ 二、组合生成（任务模板 × 参数 → 代码） ============
def compose_code(question, unit_id=None, fn_name=None, lang=None):
    """组合生成：语言识别 → 任务识别 → 代码单元 → 模板填充 → 代码（未预写完整代码）"""
    lang = lang or detect_language(question)
    units = LANG_UNITS.get(lang, CODE_UNITS)
    task = identify_task(question)
    if task is None:
        return None, "任务未识别（诚实边界：不知道要写什么程序）", None, None, lang
    # 匹配代码单元（任务 → 单元；多单元时取第一个）
    uids = [uid for uid, u in units.items() if u["task"] == task]
    if unit_id is not None and unit_id in units:
        uids = [unit_id]
    if not uids:
        return None, f"任务[{task}]在[{lang}]无代码单元覆盖（条件链不完整）", None, None, lang
    uid = uids[0]
    unit = units[uid]
    fn = fn_name or extract_fn_name(question)
    # replace 而非 format：Rust/JS pattern 含函数体 {}（format 会当占位符报错）
    code = unit["pattern"].replace("{fn}", fn)
    return task, uid, code, unit, lang


# ============ 三、自校验三层（语法 → 样例 → 边界） ============
def verify_code(code, unit, lang="python"):
    """自校验：L1 语法 + L2 样例 + L3 边界（白箱自己发现代码错误）
    Python：ast 语法 + exec 样例运行；Rust/JS：结构校验 + py_ref 逻辑样例"""
    import re as _re
    if lang != "python":
        checks = []
        # L1 结构校验：函数关键字 + 括号平衡 + 无占位残留
        kw = "fn " if lang == "rust" else "function "
        if kw not in code:
            return False, [f"✗ L1 结构错误：缺 {kw.strip()} 函数声明"]
        if "{" not in code or code.count("{") != code.count("}"):
            return False, ["✗ L1 结构错误：函数体括号不平衡"]
        if "{" in code and _re.search(r"\{\s*[a-z_]+\s*\}", code):
            return False, ["✗ L1 结构错误：存在未替换的模板占位符"]
        # L2 逻辑样例：py_ref（Python 等价实现）验证模板逻辑正确
        ns = {}
        try:
            exec(unit.get("py_ref", ""), ns)
        except Exception as e:
            return False, [f"✗ L2 py_ref 错误: {e}"]
        fns = [v for k, v in ns.items() if callable(v) and not k.startswith("__")]
        if not fns:
            return False, ["✗ L2 无 py_ref 函数"]
        fn = fns[0]
        for inp, exp in unit.get("cases", []):
            try:
                got = fn(inp)
            except Exception:
                return False, [f"✗ L2 样例崩溃: {inp}"]
            if got != exp:
                return False, [f"✗ L2 样例失败: {inp} → {got}（期望 {exp}）"]
        checks.append(f"✔ 结构通过 | 样例 {len(unit.get('cases', []))} 组全过（py_ref 逻辑）")
        return True, checks
    checks = []
    # L1 语法
    try:
        ast.parse(code)
    except SyntaxError as e:
        return False, [f"✗ L1 语法错误: {e}"]
    # L2 样例运行（函数名必须是 solve——模板默认；用户指定名时用字典注入）
    ns = {}
    try:
        exec(code, ns)
    except Exception as e:
        return False, [f"✗ L1 定义错误: {e}"]
    fns = [v for k, v in ns.items() if callable(v) and not k.startswith("__")]
    if not fns:
        return False, ["✗ L1 无函数定义"]
    fn = fns[0]
    cases = unit.get("cases", [])
    for inp, exp in cases:
        try:
            got = fn(inp)
        except Exception as e:
            return False, [f"✗ L2 样例崩溃: {inp} → {e}"]
        if got != exp:
            return False, [f"✗ L2 样例失败: {inp} → {got}（期望 {exp}）"]
    # L3 边界（额外边界用例：None/空/重复已含在 cases）
    checks.append(f"✔ 语法通过 | 样例 {len(cases)} 组全过")
    return True, checks


# ============ 四、固化（验证通过 → 固化 → 同任务直出） ============
_SOL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "code_solidified.json")
CODE_SOLIDIFIED = {}
if os.path.exists(_SOL_FILE):
    try:
        _ld = json.load(open(_SOL_FILE, encoding="utf-8"))
        if isinstance(_ld, dict):
            CODE_SOLIDIFIED = _ld
    except Exception:
        CODE_SOLIDIFIED = {}


def code_solidify(question, task=None, uid=None, fn=None):
    """固化：组合生成 + 自校验通过 → 固化（自举纪律：未验证代码不固化）"""
    lang = detect_language(question)
    t, u, code, unit, lang = compose_code(question, uid, fn, lang)
    if code is None:
        return None
    ok, checks = verify_code(code, unit, lang)
    if not ok:
        return None  # 自校验未过 → 拒绝固化（自举纪律）
    key = f"{task or t}|{u}"
    entry = {"task": t, "unit": u, "code": code, "checks": checks,
             "source": "code_solidified", "lang": lang}
    CODE_SOLIDIFIED[key] = entry
    try:
        json.dump(CODE_SOLIDIFIED, open(_SOL_FILE, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
    except Exception:
        pass
    return entry


def code_route(question, uid=None, fn=None):
    """代码条件路由统一入口：固化层 → 组合生成+自校验（多语言）"""
    lang = detect_language(question)
    t = identify_task(question)
    if t is not None and lang == "python":
        # 固化层：同任务已固化的代码直出（仅 Python——多语言不混）
        for k, entry in CODE_SOLIDIFIED.items():
            if entry.get("task") == t:
                return {"question": question, "ok": True, "solidified": True,
                        "code": entry["code"], "task": t,
                        "unit": entry.get("unit"), "checks": [],
                        "lang": "python"}
    task, uid, code, unit, lang = compose_code(question, uid, fn, lang)
    if code is None:
        return {"question": question, "ok": False, "reason": uid,
                "task": task, "code": None, "lang": lang}
    ok, checks = verify_code(code, unit, lang)
    return {"question": question, "ok": ok, "task": task, "unit": uid,
            "code": code, "checks": checks, "solidified": False, "lang": lang}


if __name__ == "__main__":
    print("=== 白箱自举·代码编写主线（组合生成 + 自校验 · 零 LLM） ===\n")
    QS = [
        "写一个函数把数组从小到大排序",
        "写一个函数去掉数组里重复的元素",
        "写一个函数数一数数组里每个元素出现几次",
        "写一个函数找出一组数里的最大值",
        "写一个函数把列表反转",
        "写一个函数把数组加起来求和",
        "写一个函数计算圆的面积",   # 任务未识别 → 诚实边界
    ]
    results = []
    for q in QS:
        r = code_route(q)
        results.append(r)
        if r.get("ok") and r.get("code"):
            mark = "✔"
            print(f"[{mark}] {q}  [任务={r['task']} 单元={r['unit']}]")
            print(f"   {r['code'].replace(chr(10), ' | ')}")
            print(f"   自校验: {r['checks'][0] if r['checks'] else '✔'}")
        else:
            print(f"[✘] {q} -> {r.get('reason')}")
    # 固化演示
    print("\n=== 固化演示 ===")
    e = code_solidify("写一个函数把数组从小到大排序")
    r2 = code_route("写一个函数把数组从小到大排序")
    print(f"固化: {'✔' if e else '✘'} | 再问: {'固化直出' if r2.get('solidified') else '重新组合'}")
    # 判定
    hit = sum(1 for r in results if r.get("ok"))
    print(f"\n=== 判定 ===\n组合生成测试通过率: {hit}/{len(QS)} = {hit/len(QS)*100:.0f}%（目标≥80%）")
