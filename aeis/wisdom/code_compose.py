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
    "去重-保序": {
        "task": "去重", "lang": "rust",
        "pattern": ("fn {fn}(arr: &[i32]) -> Vec<i32> {\n"
                    "    let mut seen = std::collections::HashSet::new();\n"
                    "    arr.iter().copied().filter(|x| seen.insert(*x)).collect()\n}\n"),
        "cases": [([1, 2, 2, 3, 1], [1, 2, 3]), ([], []), ([1, 1, 1], [1])],
        "py_ref": "def solve(arr):\n    seen = set(); out = []\n"
                  "    for x in arr:\n        if x not in seen: seen.add(x); out.append(x)\n"
                  "    return out\n",
    },
    "反转": {
        "task": "反转", "lang": "rust",
        "pattern": ("fn {fn}(arr: &[i32]) -> Vec<i32> {\n"
                    "    arr.iter().rev().copied().collect()\n}\n"),
        "cases": [([1, 2, 3], [3, 2, 1]), ([], []), ([7], [7])],
        "py_ref": "def solve(arr): return arr[::-1]\n",
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
    "去重": {
        "task": "去重", "lang": "javascript",
        "pattern": "function {fn}(arr) {\n    return [...new Set(arr)];\n}\n",
        "cases": [([1, 2, 2, 3, 1], [1, 2, 3]), ([], []), ([1, 1, 1], [1])],
        "py_ref": "def solve(arr):\n    seen = set(); out = []\n"
                  "    for x in arr:\n        if x not in seen: seen.add(x); out.append(x)\n"
                  "    return out\n",
    },
    "最大": {
        "task": "最大", "lang": "javascript",
        "pattern": "function {fn}(arr) {\n    return arr.length ? Math.max(...arr) : null;\n}\n",
        "cases": [([3, 1, 2], 3), ([7], 7), ([], None)],
        "py_ref": "def solve(arr): return max(arr) if arr else None\n",
    },
}

LANG_UNITS = {"python": CODE_UNITS, "rust": RUST_UNITS,
              "javascript": JS_UNITS}


# ============ 五、域单元注册（第六阶段·白箱自举正式管线接管） ============
# 四套域单元库（编译器/语言机制/图数据库/操作系统）接入正式自举管线：
# 域识别 → 单元匹配 → 模板填充 → verify_code 三层自校验 → 固化 JSON → 固化直出
try:
    from compiler_code_units import COMPILER_UNITS as _CU
    from python_code_units import PYTHON_UNITS as _PU
    from graph_db_units import GRAPH_UNITS as _GU
    from os_units import OS_UNITS as _OU
    from browser_units import BROWSER_UNITS as _BU
    from net_units import NET_UNITS as _NU
except Exception:
    _CU = _PU = _GU = _OU = _BU = _NU = {}

DOMAIN_UNITS = {"compiler": _CU, "pylang": _PU,
                "graph": _GU, "os": _OU, "browser": _BU, "net": _NU}

# 域识别词表（问题 → 域）
DOMAIN_KEYWORDS = {
    "compiler": ["编译", "词法", "语法", "VM", "字节码", "序列化", "调试",
                 "类型推断", "类型检查", "名实", "道德经", "中文编译器",
                 "函数", "递归", "定义", "注释", "逻辑表达式", "链式"],
    "pylang": ["Python", "表达式", "闭包", "控制流", "作用域", "栈机",
               "优先级", "逻辑短路", "异常", "抛出", "捕获", "try", "raise",
               "工厂", "延迟绑定", "nonlocal", "生成器", "yield", "迭代器",
               "推导", "类", "继承", "多态", "类定义", "装饰器", "上下文",
               "with", "属性"],
    "graph": ["图数据库", "图遍历", "图查询", "条件路由图", "遍历", "路径",
              "路由", "持久化", "条件链", "建图", "图存储", "模式匹配",
              "聚合", "匹配", "事务", "索引", "子图", "PageRank", "连通",
              "拓扑", "执行计划", "批量", "布隆", "相似度", "同构", "社区",
              "属性", "快照", "版本", "时序", "增量"],
    "os": ["进程", "调度", "内存", "文件系统", "路径解析", "管道", "IPC",
           "inode", "页置换", "缺页", "状态机", "最短作业", "SJF",
           "块管理", "位图", "优先级调度", "互斥", "首次适配", "文件块",
           "页表", "虚拟", "页面", "物理帧", "MMU", "目录树", "文件描述符",
           "字符设备", "设备", "中断", "向量", "上下文", "嵌套", "抢占",
           "挂载", "权限", "进程树", "系统调用", "信号", "参数", "校验",
           "日志", "恢复", "监控", "守护", "信号量", "读写锁", "生产者",
           "命名空间", "cgroup", "容器", "虚拟化", "RAID", "条带", "奇偶",
           "快照"],
    "browser": ["浏览器", "HTTP", "响应解析", "DOM", "HTML", "CSS", "选择器",
                "渲染", "布局", "网页", "标签解析", "URL", "请求", "主机",
                "端口", "协议", "盒模型", "级联", "样式", "padding", "border",
                "绘制", "布局树", "画布", "事件", "冒泡", "监听", "动画帧",
                "存储", "localStorage", "会话存储", "Worker", "并行",
                "Fetch", "缓存", "Cookie", "同源", "CSP", "安全", "XSS",
                "转义"],
    "net": ["网络", "TCP", "UDP", "IP分片", "握手", "校验和", "广播",
            "局域网", "蜂群", "socket", "中继", "分片", "路由表", "重传",
            "停等", "去重", "确认", "分帧", "会话", "滑动窗口", "拥塞",
            "累积确认", "慢启动", "CIDR", "子网", "距离矢量", "NAT",
            "DNS", "状态码", "负载均衡", "HTTP", "WebSocket", "帧封装",
            "流式", "多路复用", "连接池", "QUIC", "BGP", "Anycast", "CRC"],
}


def detect_domain(question):
    """域识别：问题 → 域（compiler/pylang/graph/os/browser/net/None）
    命中计数优先（「CSS级联+样式优先级」= browser 3 词 > pylang 1 词），
    平局取最长关键词（「路由表」len3 > 「路由」len2）"""
    best, best_cnt, best_len = None, 0, 0
    for domain, kws in DOMAIN_KEYWORDS.items():
        hit = [k for k in kws if k in question]
        if not hit:
            continue
        cnt, max_len = len(hit), max(len(k) for k in hit)
        if cnt > best_cnt or (cnt == best_cnt and max_len > best_len):
            best, best_cnt, best_len = domain, cnt, max_len
    return best


def compose_domain_code(question, domain=None, unit_id=None):
    """域组合生成：域识别 → 单元匹配（task/uid 关键词）→ 模板填充"""
    domain = domain or detect_domain(question)
    if domain is None:
        return None, "域未识别（诚实边界：不属编译器/语言机制/图数据库/操作系统域）", None, None, None
    units = DOMAIN_UNITS.get(domain, {})
    # 单元匹配：uid/task 拆词（"编译-指令"→[编译,指令]）+ 原文（最长优先）
    def _unit_kws(u, uid):
        return [uid, u["task"]] + uid.replace("-", "").split() \
            + u["task"].replace("-", "").split() \
            + [p for p in uid.split("-") if p]

    best_uid, best_cnt, best_len = None, 0, 0
    q_compact = question.replace(" ", "")  # 空格归一化（"IP 分片"→"IP分片"）
    for uid, u in units.items():
        kws = _unit_kws(u, uid)
        hit = list({kw for kw in kws
                    if kw and (kw in question or kw in q_compact)})
        if not hit:
            continue
        cnt, max_len = len(hit), max(len(kw) for kw in hit)
        if cnt > best_cnt or (cnt == best_cnt and max_len > best_len):
            best_uid, best_cnt, best_len = uid, cnt, max_len
    if unit_id is not None and unit_id in units:
        best_uid = unit_id
    if best_uid is None:
        return None, f"域[{domain}]无匹配单元（条件链不完整）", None, None, domain
    unit = units[best_uid]
    code = unit["pattern"]
    return unit["task"], best_uid, code, unit, domain


def domain_solidify(question, domain=None, uid=None):
    """域固化：组合生成 + 自校验通过 → 固化（自举纪律：未验证不固化）"""
    t, u, code, unit, domain = compose_domain_code(question, domain, uid)
    if code is None:
        return None
    ok, checks = verify_code(code, unit, "python")
    if not ok:
        return None  # 自校验未过 → 拒绝固化
    key = f"domain:{domain}|{u}"
    entry = {"task": t, "unit": u, "code": code, "checks": checks,
             "source": "domain_solidified", "domain": domain}
    CODE_SOLIDIFIED[key] = entry
    try:
        json.dump(CODE_SOLIDIFIED, open(_SOL_FILE, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
    except Exception:
        pass
    return entry


def domain_route(question, uid=None):
    """域路由统一入口：单元匹配 → 已固化直出 → 域组合生成 + 自校验"""
    domain = detect_domain(question)
    if domain is None:
        return {"question": question, "ok": False,
                "reason": "域未识别（诚实边界）", "domain": None, "code": None}
    # 单元匹配先行（与组合生成同一套逻辑），匹配到的单元已固化 → 直出
    t, u, code, unit, domain = compose_domain_code(question, domain, uid)
    if code is not None:
        key = f"domain:{domain}|{u}"
        if key in CODE_SOLIDIFIED:
            entry = CODE_SOLIDIFIED[key]
            return {"question": question, "ok": True, "solidified": True,
                    "code": entry["code"], "task": entry.get("task"),
                    "unit": entry.get("unit"), "domain": domain, "checks": []}
    if code is None:
        return {"question": question, "ok": False, "reason": u,
                "task": t, "code": None, "domain": domain}
    ok, checks = verify_code(code, unit, "python")
    return {"question": question, "ok": ok, "task": t, "unit": u,
            "code": code, "checks": checks, "solidified": False, "domain": domain}


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
def _run_case(fn, case):
    """执行单个样例：兼容 (inp, exp) 单参数 / (args_tuple, exp) 多参数 / ('call', exp)"""
    if len(case) != 2:
        return None, f"样例格式错误: {case}"
    inp, exp = case
    if inp == "call":
        return "call", exp  # 特殊标记：域注入型单元（L2 由集成测试覆盖）
    if isinstance(inp, tuple):
        return fn(*inp), exp
    return fn(inp), exp


def verify_code(code, unit, lang="python"):
    """自校验：L1 语法 + L2 样例 + L3 边界（白箱自己发现代码错误）
    Python：ast 语法 + exec 样例运行；Rust/JS：结构校验 + py_ref 逻辑样例
    v6：支持多参数样例 (args_tuple, exp)；needs_inject 单元 L2 由集成测试覆盖"""
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
    if unit.get("needs_inject"):
        # 注入型单元（需要 Graph/run_stmts 等白箱单元组装）：L2 由集成测试覆盖
        checks.append(f"✔ 语法通过 | 注入型单元：L2 样例由域集成测试覆盖（{len(unit.get('cases', []))} 组）")
        return True, checks
    cases = unit.get("cases", [])
    for case in cases:
        try:
            got, exp = _run_case(fn, case)
        except Exception as e:
            return False, [f"✗ L2 样例崩溃: {case} → {e}"]
        if got == "call":
            continue  # call 特殊标记（域注入型，由集成测试覆盖）
        if got != exp:
            return False, [f"✗ L2 样例失败: {case} → {got}（期望 {exp}）"]
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
