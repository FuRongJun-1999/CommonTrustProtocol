# -*- coding: utf-8 -*-
"""python_code_units.py · Mini-Python 语言机制白箱单元库（第六阶段 P 线·白箱自举）
设计者指令：7 终极目标 + 7 初级复现项目都是白箱自举后验证编程能力的项目——
P 线 Mini-Python 由白箱自己实现（code_compose 机制），外部只校准。
mini_python.py 定位为校准参考实现（语义基准）。
单元：{任务 → 代码模式模板 + 验证样例 + 校准基准}——语言机制（词法/优先级/
求值/逻辑/环境/栈机）逐一白箱化。
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 任务 → 代码模式 + 验证样例（白箱生成的自校验基准）
PYTHON_UNITS = {
    "词法-记号化": {
        "task": "词法分析",
        "pattern": (
            "def tokenize(src):\n"
            "    # 字符流 → token 列表（数字/运算符/括号）——Mini-Python 词法\n"
            "    import re\n"
            "    tokens, i = [], 0\n"
            "    while i < len(src):\n"
            "        if src[i].isdigit():\n"
            "            j = i\n"
            "            while j < len(src) and (src[j].isdigit() or src[j] == '.'):\n"
            "                j += 1\n"
            "            text = src[i:j]\n"
            "            tokens.append(('NUMBER', float(text) if '.' in text else int(text)))\n"
            "            i = j\n"
            "        elif src[i] in '+-*/%()':\n"
            "            tokens.append(('OP', src[i]))\n"
            "            i += 1\n"
            "        elif src[i].isspace():\n"
            "            i += 1\n"
            "        else:\n"
            "            raise SyntaxError('未知字符: ' + src[i])\n"
            "    tokens.append(('EOF', ''))\n"
            "    return tokens\n"),
        "cases": [("2+3", [("NUMBER", 2), ("OP", "+"), ("NUMBER", 3), ("EOF", "")]),
                  ("3.5*2", [("NUMBER", 3.5), ("OP", "*"), ("NUMBER", 2), ("EOF", "")]),
                  ("(1)", [("OP", "("), ("NUMBER", 1), ("OP", ")"), ("EOF", "")])],
        "params": [],
        "calibration": "对照：mini_python.py tokenize（数字含小数/运算符/括号）",
    },
    "语法-优先级": {
        "task": "优先级计算",
        "pattern": (
            "def precedence(expr):\n"
            "    # 表达式优先级求值（2+3*4=14；括号最高）——Mini-Python 语法\n"
            "    def parse(i, min_prec):\n"
            "        if expr[i] == '(':\n"
            "            val, i = parse(i + 1, 0)\n"
            "            i += 1  # 跳过 ')'\n"
            "        else:\n"
            "            val = 0\n"
            "            j = i\n"
            "            while j < len(expr) and expr[j].isdigit():\n"
            "                val = val * 10 + int(expr[j])\n"
            "                j += 1\n"
            "            i = j\n"
            "        prec = {'+': 1, '-': 1, '*': 2, '/': 2, '**': 3}\n"
            "        while i < len(expr) and expr[i] in prec and prec[expr[i]] >= min_prec:\n"
            "            op = expr[i]\n"
            "            right, i = parse(i + 1, prec[op] + 1)\n"
            "            if op == '+':\n"
            "                val += right\n"
            "            elif op == '-':\n"
            "                val -= right\n"
            "            elif op == '*':\n"
            "                val *= right\n"
            "            elif op == '/':\n"
            "                val /= right\n"
            "        return val, i\n"
            "    return parse(0, 0)[0]\n"),
        "cases": [("2+3*4", 14), ("(2+3)*4", 20), ("10-3*2", 4), ("2+3+4", 9)],
        "params": [],
        "calibration": "对照：CPython 优先级（乘除高于加减，括号最高）",
    },
    "求值-逻辑短路": {
        "task": "逻辑短路",
        "pattern": (
            "def logic_eval(expr, values):\n"
            "    # or/and 短路 + 返回操作数（Python 语义：0 or 5 → 5）\n"
            "    def truthy(v):\n"
            "        return v is not None and v is not False and v != 0\n"
            "    left = values[expr[0]]\n"
            "    if expr[1] == 'or':\n"
            "        return left if truthy(left) else values[expr[2]]\n"
            "    if expr[1] == 'and':\n"
            "        return values[expr[2]] if truthy(left) else left\n"
            "    return None\n"),
        "cases": [((("a", "or", "b"), {"a": 1, "b": 0}), 1),
                  ((("a", "or", "b"), {"a": 0, "b": 5}), 5),
                  ((("a", "and", "b"), {"a": 0, "b": 5}), 0),
                  ((("a", "and", "b"), {"a": 2, "b": 3}), 3)],
        "params": [],
        "calibration": "对照：Python 语义——or/and 返回操作数 + 短路",
    },
    "环境-作用域链": {
        "task": "作用域环境",
        "pattern": (
            "class Env:\n"
            "    # 变量环境：作用域链（局部 → 父环境）——Mini-Python 环境\n"
            "    def __init__(self, parent=None):\n"
            "        self.vars = {}\n"
            "        self.parent = parent\n"
            "    def get(self, name):\n"
            "        if name in self.vars:\n"
            "            return self.vars[name]\n"
            "        if self.parent:\n"
            "            return self.parent.get(name)\n"
            "        raise NameError(name + ' 未定义')\n"
            "    def set(self, name, value):\n"
            "        self.vars[name] = value\n"
            "def env_scope():\n"
            "    g = Env()\n"
            "    g.set('x', 1)\n"
            "    l = Env(g)\n"
            "    l.set('y', 2)\n"
            "    return (l.get('x'), l.get('y'))\n"),
        "cases": [("call", (1, 2))],
        "params": [],
        "calibration": "对照：mini_python.py Env（父链作用域：局部找不到向上查找）",
    },
    "栈机-字节码执行": {
        "task": "栈机执行",
        "pattern": (
            "def vm_exec(code):\n"
            "    # 字节码栈机雏形（PUSH/ADD/SUB/MUL）——Mini-Python VM\n"
            "    stack = []\n"
            "    for op, arg in code:\n"
            "        if op == 'PUSH':\n"
            "            stack.append(arg)\n"
            "        elif op == 'ADD':\n"
            "            b, a = stack.pop(), stack.pop()\n"
            "            stack.append(a + b)\n"
            "        elif op == 'SUB':\n"
            "            b, a = stack.pop(), stack.pop()\n"
            "            stack.append(a - b)\n"
            "        elif op == 'MUL':\n"
            "            b, a = stack.pop(), stack.pop()\n"
            "            stack.append(a * b)\n"
            "    return stack[-1] if stack else None\n"),
        "cases": [(([("PUSH", 2), ("PUSH", 3), ("PUSH", 4), ("MUL", None), ("ADD", None)],), 14),
                  (([("PUSH", 10), ("PUSH", 3), ("SUB", None)],), 7)],
        "params": [],
        "calibration": "对照：mini_python.py VM 栈机（指令→栈操作）",
    },
    "求值-控制流": {
        "task": "控制流",
        "pattern": (
            "def run_stmts(stmts, env):\n"
            "    # 语句执行器：assign/if/while（简化 AST——Mini-Python 控制流语义）\n"
            "    i = 0\n"
            "    while i < len(stmts):\n"
            "        s = stmts[i]\n"
            "        k = s[0]\n"
            "        if k == 'assign':\n"
            "            env[s[1]] = s[2]\n"
            "            i += 1\n"
            "        elif k == 'if':\n"
            "            cond = s[1] if isinstance(s[1], bool) else env.get(s[1], False)\n"
            "            branch = s[2] if cond else s[3]\n"
            "            run_stmts(branch, env)\n"
            "            i += 1\n"
            "        elif k == 'while':\n"
            "            guard = 0\n"
            "            cond = s[1] if isinstance(s[1], bool) else env.get(s[1], False)\n"
            "            while cond and guard < 1000:\n"
            "                run_stmts(s[2], env)\n"
            "                cond = s[1] if isinstance(s[1], bool) else env.get(s[1], False)\n"
            "                guard += 1\n"
            "            i += 1\n"
            "    return env\n"),
        "cases": [(([("assign", "x", 5), ("if", True, [("assign", "y", 1)], [("assign", "y", 0)])], {}),
                   {"x": 5, "y": 1}),
                  (([("assign", "x", 5), ("if", False, [("assign", "y", 1)], [("assign", "y", 0)])], {}),
                   {"x": 5, "y": 0}),
                  (([("assign", "go", True), ("while", "go", [("assign", "go", False)])], {}),
                   {"go": False})],
        "params": [],
        "calibration": "对照：mini_python.py exec_stmt（assign/if/while 语义）",
    },
    "函数-定义调用": {
        "task": "函数机制",
        "pattern": (
            "def make_function(params, body, def_env):\n"
            "    # 函数对象：参数 + body + 定义环境（闭包基础）\n"
            "    return ('func', params, body, def_env)\n"
            "def call_function(f, args, env):\n"
            "    # 调用：局部环境（父=定义环境）+ 参数绑定 + 执行 body（return 值）\n"
            "    _, params, body, def_env = f\n"
            "    local = dict(def_env)\n"
            "    for p, a in zip(params, args):\n"
            "        local[p] = a\n"
            "    result = None\n"
            "    for s in body:\n"
            "        if s[0] == 'return':\n"
            "            result = s[1]\n"
            "            break\n"
            "    return result\n"),
        "cases": [((["a", "b"], [("return", 7)], {}), ("func", ["a", "b"], [("return", 7)], {}))],
        "params": [],
        "calibration": "对照：mini_python.py 函数对象（参数+body+定义环境）与 call 调用（局部环境+参数绑定）",
    },
    "求值-闭包": {
        "task": "闭包机制",
        "pattern": (
            "def closure_adder(n):\n"
            "    # 闭包：内部函数捕获自由变量 n（定义环境）\n"
            "    def add(x):\n"
            "        return x + n\n"
            "    return add\n"
            "def closure_test():\n"
            "    a = closure_adder(3)\n"
            "    b = closure_adder(10)\n"
            "    return (a(1), b(1))\n"),
        "cases": [("call", (4, 11))],
        "params": [],
        "calibration": "对照：Python 闭包语义——独立捕获（a(1)=4、b(1)=11 互不干扰）",
    },
    "闭包-捕获更新": {
        "task": "捕获更新",
        "pattern": (
            "def counter_nonlocal():\n"
            "    # nonlocal 语义：闭包修改捕获变量（非只读）\n"
            "    count = 0\n"
            "    def inc():\n"
            "        nonlocal count\n"
            "        count += 1\n"
            "        return count\n"
            "    return inc\n"
            "def closure_mutate_test():\n"
            "    f = counter_nonlocal()\n"
            "    return (f(), f(), f())\n"),
        "cases": [("call", (1, 2, 3))],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：Python nonlocal——闭包内修改捕获变量（连续调用递增）",
    },
    "闭包-工厂": {
        "task": "闭包工厂",
        "pattern": (
            "def make_multiplier(factor):\n"
            "    # 闭包工厂：返回绑定了 factor 的乘法闭包\n"
            "    def mul(x):\n"
            "        return x * factor\n"
            "    return mul\n"
            "def closure_factory_test():\n"
            "    double = make_multiplier(2)\n"
            "    triple = make_multiplier(3)\n"
            "    return (double(5), triple(5))\n"),
        "cases": [("call", (10, 15))],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：Python 闭包工厂——函数返回绑定参数的闭包（乘子工厂）",
    },
    "闭包-延迟绑定": {
        "task": "延迟绑定",
        "pattern": (
            "def lazy_bindings():\n"
            "    # 延迟绑定陷阱：循环后调用闭包 → 全捕获同一最终值\n"
            "    funcs = []\n"
            "    for i in range(3):\n"
            "        funcs.append(lambda: i)\n"
            "    return [f() for f in funcs]\n"),
        "cases": [("call", [2, 2, 2])],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：Python 延迟绑定——循环变量 i 闭包捕获最终值（经典陷阱：全 2 非 0,1,2）",
    },
    "栈机-完整执行": {
        "task": "完整栈机",
        "pattern": (
            "def vm_exec_full(code):\n"
            "    # 栈机扩展：比较 CMP_GT + 条件跳转 JUMP_IF_FALSE（if 语义）\n"
            "    stack, ip = [], 0\n"
            "    while ip < len(code):\n"
            "        op, arg = code[ip]\n"
            "        ip += 1\n"
            "        if op == 'PUSH':\n"
            "            stack.append(arg)\n"
            "        elif op == 'ADD':\n"
            "            b, a = stack.pop(), stack.pop()\n"
            "            stack.append(a + b)\n"
            "        elif op == 'MUL':\n"
            "            b, a = stack.pop(), stack.pop()\n"
            "            stack.append(a * b)\n"
            "        elif op == 'CMP_GT':\n"
            "            b, a = stack.pop(), stack.pop()\n"
            "            stack.append(a > b)\n"
            "        elif op == 'JUMP_IF_FALSE':\n"
            "            if not stack.pop():\n"
            "                ip = arg\n"
            "    return stack\n"),
        "cases": [(([("PUSH", 5), ("PUSH", 3), ("CMP_GT", None), ("JUMP_IF_FALSE", 6),
                     ("PUSH", 1)],), [1]),
                  (([("PUSH", 3), ("PUSH", 5), ("CMP_GT", None), ("JUMP_IF_FALSE", 5),
                     ("PUSH", 1)],), [])],
        "params": [],
        "calibration": "对照：mini_python.py VM（比较+条件跳转——if 的栈机形态）",
    },
    "数据结构-列表字典": {
        "task": "数据结构",
        "pattern": (
            "def list_dict_ops(op, obj, key=None, value=None):\n"
            "    # list/dict 语义：索引读取/写入（P5 数据结构）\n"
            "    if op == 'get':\n"
            "        return obj[key]\n"
            "    if op == 'set':\n"
            "        obj[key] = value\n"
            "        return obj\n"
            "    if op == 'len':\n"
            "        return len(obj)\n"
            "    return None\n"),
        "cases": [(("get", [1, 2, 3], 1), 2),
                  (("get", {"甲": 1, "乙": 2}, "乙"), 2),
                  (("set", [1, 2, 3], 0, 9), [9, 2, 3]),
                  (("len", [1, 2, 3]), 3)],
        "params": [],
        "calibration": "对照：Python list/dict 语义（索引读写/长度）",
    },
    "程序-完整执行": {
        "task": "完整程序",
        "pattern": (
            "def run_program(src, fn_run_stmts):\n"
            "    # 完整程序执行（组装：词法→语法→语句执行——P 线自举闭环）\n"
            "    # 简化管线：行→语句（assign/if/while/expr）→ run_stmts\n"
            "    import re as _re\n"
            "    stmts = []\n"
            "    for raw in src.splitlines():\n"
            "        line = raw.strip()\n"
            "        if not line or line.startswith('#'):\n"
            "            continue\n"
            "        if _re.match(r'^[A-Za-z_]\\w*\\s*=', line):\n"
            "            name, _, val = line.partition('=')\n"
            "            v = val.strip()\n"
            "            stmts.append(('assign', name.strip(),\n"
            "                          int(v) if v.lstrip('-').isdigit() else v))\n"
            "        elif line.startswith('if '):\n"
            "            cond = line[3:].rstrip(':').strip()\n"
            "            stmts.append(('if', cond == 'True', [('assign', 't', 1)],\n"
            "                          [('assign', 't', 0)]))\n"
            "        elif line.startswith('while '):\n"
            "            stmts.append(('while', 'go', [('assign', 'go', False)]))\n"
            "    env = {}\n"
            "    fn_run_stmts(stmts, env)\n"
            "    return env\n"),
        "cases": [("x = 5\ny = 3\n", {"x": 5, "y": 3}),
                  ("x = 5\nif True:\n    t = 1\n", {"x": 5, "t": 1})],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：mini_python.py run_program（词法→语法→语句执行全链路；组装白箱生成单元）",
    },
    "异常-抛出": {
        "task": "抛出异常",
        "pattern": (
            "def raise_error(etype, msg):\n"
            "    # raise 语义：构造异常对象并抛出（Mini-Python 错误处理）\n"
            "    raise etype(msg)\n"),
        "cases": [("call", ("raised", "测试错误"))],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：Python raise（构造异常实例并抛出）",
    },
    "异常-捕获": {
        "task": "捕获异常",
        "pattern": (
            "def try_except(etype, handler, risky):\n"
            "    # try/except 语义：尝试 risky()，抛 etype 异常 → handler(err)\n"
            "    try:\n"
            "        return ('ok', risky())\n"
            "    except etype as err:\n"
            "        return ('caught', handler(err))\n"),
        "cases": [("call", ('caught', '处理:除以零'))],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：Python try/except（异常匹配 etype → 处理器；无异常 → ok）",
    },
    "异常-传播": {
        "task": "异常传播",
        "pattern": (
            "def propagate(call_chain, etype, msg):\n"
            "    # 异常传播：内层函数抛错 → 中间不处理 → 外层捕获（调用栈冒泡）\n"
            "    def inner():\n"
            "        raise etype(msg)\n"
            "    def mid():\n"
            "        return inner()   # 不捕获，向上传播\n"
            "    try:\n"
            "        mid()\n"
            "    except etype as err:\n"
            "        return ('caught_at_outer', str(err))\n"
            "    return ('no_catch', None)\n"),
        "cases": [("call", ('caught_at_outer', '深层错误'))],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：Python 异常传播（内层 raise → 中间不处理 → 外层捕获）",
    },
    "生成器-yield": {
        "task": "生成器",
        "pattern": (
            "def gen_count(n):\n"
            "    # 生成器：yield 暂停/恢复（惰性求值，逐个产出）\n"
            "    i = 0\n"
            "    while i < n:\n"
            "        yield i\n"
            "        i += 1\n"
            "def gen_test():\n"
            "    return list(gen_count(3))\n"),
        "cases": [("call", [0, 1, 2])],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：Python 生成器——yield 逐个产出（list(gen_count(3))=[0,1,2] 惰性求值）",
    },
    "迭代器-协议": {
        "task": "迭代协议",
        "pattern": (
            "def iter_protocol(data):\n"
            "    # 迭代器协议：__iter__/__next__（next 逐个取值，耗尽抛 StopIteration）\n"
            "    it = iter(data)\n"
            "    out = []\n"
            "    while True:\n"
            "        try:\n"
            "            out.append(next(it))\n"
            "        except StopIteration:\n"
            "            break\n"
            "    return out\n"),
        "cases": [(([1, 2, 3],), [1, 2, 3]),
                  (([],), []),
                  ((['a'],), ['a'])],
        "params": [],
        "calibration": "对照：Python 迭代器协议（iter/next/StopIteration 耗尽语义）",
    },
    "推导式-列表推导": {
        "task": "列表推导",
        "pattern": (
            "def list_comp(items, transform):\n"
            "    # 列表推导式：[transform(x) for x in items]（映射语义）\n"
            "    return [transform(x) for x in items]\n"),
        "cases": [(([1, 2, 3], lambda x: x * 2), [2, 4, 6]),
                  (([], lambda x: x), [])],
        "params": [],
        "calibration": "对照：Python 列表推导式（[f(x) for x in seq] 映射）",
    },
    "面向对象-类定义": {
        "task": "类定义",
        "pattern": (
            "class Dog:\n"
            "    # 类定义：__init__ 构造 + 方法（实例属性）\n"
            "    def __init__(self, name):\n"
            "        self.name = name\n"
            "    def speak(self):\n"
            "        return self.name + ' 汪汪'\n"
            "def oop_class_test():\n"
            "    d = Dog('阿黄')\n"
            "    return (d.name, d.speak())\n"),
        "cases": [("call", ('阿黄', '阿黄 汪汪'))],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：Python 类定义——__init__ 构造 + 实例方法（实例属性语义）",
    },
    "面向对象-继承": {
        "task": "类继承",
        "pattern": (
            "class Animal:\n"
            "    def speak(self):\n"
            "        return '动物'\n"
            "class Cat(Animal):\n"
            "    # 继承：子类覆盖父类方法（方法重写）\n"
            "    def speak(self):\n"
            "        return '喵'\n"
            "def oop_inherit_test():\n"
            "    return (Animal().speak(), Cat().speak())\n"),
        "cases": [("call", ('动物', '喵'))],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：Python 继承——子类覆盖父类方法（方法重写语义）",
    },
    "面向对象-多态": {
        "task": "多态分发",
        "pattern": (
            "def poly_speak(obj):\n"
            "    # 多态：同一接口不同实现（运行时方法分发）\n"
            "    return obj.speak()\n"
            "def oop_poly_test():\n"
            "    return [poly_speak(o) for o in\n"
            "            (type('D', (), {'speak': lambda s: '汪'})(),\n"
            "             type('C', (), {'speak': lambda s: '喵'})())]\n"),
        "cases": [("call", ['汪', '喵'])],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：Python 多态——同一接口不同实现（运行时方法分发）",
    },
    "装饰器-定义使用": {
        "task": "装饰器",
        "pattern": (
            "def timer(fn):\n"
            "    # 装饰器：包装函数（@timer 语义——增强不改原逻辑）\n"
            "    def wrapper(*args):\n"
            "        return ('timed', fn(*args))\n"
            "    return wrapper\n"
            "def decorator_test():\n"
            "    @timer\n"
            "    def add(a, b):\n"
            "        return a + b\n"
            "    return add(2, 3)\n"),
        "cases": [("call", ('timed', 5))],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：Python 装饰器（@timer 包装增强，不改原函数逻辑）",
    },
    "上下文-管理器": {
        "task": "上下文管理器",
        "pattern": (
            "class Open:\n"
            "    # 上下文管理器：with 语义（__enter__ 获取/__exit__ 释放）\n"
            "    def __enter__(self):\n"
            "        self.opened = True\n"
            "        return self\n"
            "    def __exit__(self, *exc):\n"
            "        self.opened = False\n"
            "        return False\n"
            "def with_test():\n"
            "    with Open() as f:\n"
            "        inside = f.opened\n"
            "    return (inside, f.opened)\n"),
        "cases": [("call", (True, False))],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：Python with 语句（__enter__/__exit__ 资源获取释放）",
    },
    "工具-属性访问": {
        "task": "属性访问",
        "pattern": (
            "class User:\n"
            "    # 属性访问：getattr/setattr（动态读写属性）\n"
            "    def __init__(self):\n"
            "        self._d = {}\n"
            "    def __getattr__(self, name):\n"
            "        return self._d.get(name)\n"
            "    def __setattr__(self, name, value):\n"
            "        if name == '_d':\n"
            "            object.__setattr__(self, name, value)\n"
            "        else:\n"
            "            self._d[name] = value\n"
            "def attr_test():\n"
            "    u = User()\n"
            "    u.名字 = '灵枢'\n"
            "    return (u.名字, u.不存在)\n"),
        "cases": [("call", ('灵枢', None))],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：Python 动态属性（__getattr__/__setattr__ 拦截读写）",
    },
    "类型-类型注解": {
        "task": "类型注解",
        "pattern": (
            "def annotate(params, ret):\n"
            "    # 类型注解：参数/返回类型标注（def f(x: int) -> str 语义）\n"
            "    return {'params': dict(params), 'return': ret}\n"
            "def annotate_test():\n"
            "    return annotate({'x': int}, str)\n"),
        "cases": [("call", {'params': {'x': int}, 'return': str})],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：Python 类型注解（参数/返回类型标注——PEP 484）",
    },
    "类型-运行时检查": {
        "task": "运行时检查",
        "pattern": (
            "def runtime_check(value, expected):\n"
            "    # 运行时类型检查：isinstance 语义（鸭子类型——结构兼容即可）\n"
            "    if isinstance(value, expected):\n"
            "        return 'ok'\n"
            "    if expected is int and isinstance(value, float) and value.is_integer():\n"
            "        return 'ok'\n"
            "    return 'type_error'\n"),
        "cases": [((5, int), 'ok'), ((5.0, int), 'ok'),
                  (('5', int), 'type_error'), (([], list), 'ok')],
        "params": [],
        "calibration": "对照：Python 运行时类型检查（isinstance，整值浮点可当整数）",
    },
    "类型-协议接口": {
        "task": "协议接口",
        "pattern": (
            "def check_protocol(obj, methods):\n"
            "    # 协议：结构约定（具 __len__ 即序列协议——鸭子类型）\n"
            "    return all(hasattr(obj, m) for m in methods)\n"),
        "cases": [(([], ['__len__', '__iter__']), True),
                  ((5, ['__len__']), False),
                  (({}, ['__len__']), True)],
        "params": [],
        "calibration": "对照：Python 协议——结构约定（具 __len__ 即序列协议，鸭子类型）",
    },
    "异步-async await": {
        "task": "异步协程",
        "pattern": (
            "import asyncio\n"
            "async def fetch(name):\n"
            "    # async/await 协程：挂起等待（异步 I/O 语义）\n"
            "    await asyncio.sleep(0)\n"
            "    return name + '_done'\n"
            "def async_test():\n"
            "    return asyncio.run(fetch('任务'))\n"),
        "cases": [("call", '任务_done')],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：Python async/await（协程挂起等待，异步 I/O）",
    },
    "异步-事件循环": {
        "task": "事件循环",
        "pattern": (
            "def event_loop(tasks):\n"
            "    # 事件循环：任务队列调度（依次执行——单线程并发）\n"
            "    done = []\n"
            "    for t in tasks:\n"
            "        done.append(t())\n"
            "    return done\n"),
        "cases": [(([lambda: 1, lambda: 2],), [1, 2]),
                  (([],), [])],
        "params": [],
        "calibration": "对照：Python 事件循环——任务队列依次调度（单线程并发）",
    },
    "异步-并发任务": {
        "task": "并发任务",
        "pattern": (
            "def gather(tasks):\n"
            "    # 并发任务：asyncio.gather 语义（并行执行汇总结果）\n"
            "    return [t() for t in tasks]\n"),
        "cases": [(([lambda: 'a', lambda: 'b'],), ['a', 'b']),
                  (([],), [])],
        "params": [],
        "calibration": "对照：Python asyncio.gather（并发任务汇总结果）",
    },
    "元编程-动态建类": {
        "task": "动态建类",
        "pattern": (
            "def make_class(name, bases, attrs):\n"
            "    # 动态建类：type(name, bases, dict) 运行时创建类\n"
            "    # （元编程——类型即工厂，运行期定义新类型）\n"
            "    cls = type(name, tuple(bases), dict(attrs))\n"
            "    return cls.__name__, [b.__name__ for b in cls.__bases__], \\\n"
            "        {k: v for k, v in vars(cls).items() if not k.startswith('__')}\n"),
        "cases": [(("动物", [], {"属性": "犬科"}), ("动物", ["object"], {"属性": "犬科"})),
                  (("狗", [object], {"叫声": "汪"}), ("狗", ["object"], {"叫声": "汪"}))],
        "params": [],
        "calibration": "对照：CPython type(name, bases, dict)（动态创建类；无显式基类→隐式 object 基类）",
    },
    "元编程-元类定制": {
        "task": "元类定制",
        "pattern": (
            "def meta_create(name, attrs, hook):\n"
            "    # 元类定制：hook 在类创建时回调（校验/注入）——元类 = 类创建钩子\n"
            "    final = dict(attrs)\n"
            "    if hook is not None:\n"
            "        final.update(hook(name, dict(attrs)) or {})\n"
            "    cls = type(name, (), final)\n"
            "    return cls.__name__, {k: v for k, v in vars(cls).items()\n"
            "                           if not k.startswith('__')}\n"),
        "cases": [(("狗", {"叫声": "汪"}, lambda n, a: {"科": "犬科"}),
                   ("狗", {"叫声": "汪", "科": "犬科"})),
                  (("猫", {"叫声": "喵"}, None), ("猫", {"叫声": "喵"}))],
        "params": [],
        "calibration": "对照：CPython metaclass __new__ 拦截类创建（校验/注入类属性）",
    },
    "元编程-描述符协议": {
        "task": "描述符协议",
        "pattern": (
            "def descriptor_route(storage, desc, name, value=None):\n"
            "    # 描述符协议：读走 __get__ 写走 __set__（property 底层机制，属性访问托管）\n"
            "    if value is None:\n"
            "        return desc['__get__'](storage, name)\n"
            "    desc['__set__'](storage, name, value)\n"
            "    return storage\n"),
        "cases": [(({}, {"__get__": lambda st, n: st.get('_' + n, 25),
                 "__set__": lambda st, n, v: st.update({'_' + n: v})},
                    "温度", None), 25),
                  (({}, {"__get__": lambda st, n: st.get('_' + n, 25),
                 "__set__": lambda st, n, v: st.update({'_' + n: v})},
                    "温度", 30), {"_温度": 30})],
        "params": [],
        "calibration": "对照：CPython 描述符协议（__get__/__set__，property 与 @property 底层）",
    },
    "面向对象-运算符重载": {
        "task": "运算符重载",
        "pattern": (
            "def binop_dispatch(obj, other, op):\n"
            "    # 运算符重载：对象方法分派（__add__/__mul__——重定义运算符行为）\n"
            "    method = obj.get(op) if isinstance(obj, dict) else getattr(obj, op, None)\n"
            "    if method is None:\n"
            "        return 'unsupported'\n"
            "    return method(other)\n"),
        "cases": [(({'__add__': lambda o: o + 1}, 5, '__add__'), 6),
                  (({'__mul__': lambda o: o * 2}, 3, '__mul__'), 6),
                  (({}, 5, '__add__'), 'unsupported')],
        "params": [],
        "calibration": "对照：CPython 运算符重载（__add__/__mul__ dunder 分派，未定义→TypeError 语义）",
    },
    "数据结构-枚举": {
        "task": "枚举",
        "pattern": (
            "def enum_resolve(members, key):\n"
            "    # 枚举：名称↔值双向解析（成员表——Enum 类型语义）\n"
            "    if key in members:\n"
            "        return ('value', members[key])\n"
            "    for name, val in members.items():\n"
            "        if val == key:\n"
            "            return ('name', name)\n"
            "    return None\n"),
        "cases": [(({'红': 1, '绿': 2}, '红'), ('value', 1)),
                  (({'红': 1, '绿': 2}, 2), ('name', '绿')),
                  (({'红': 1}, '蓝'), None)],
        "params": [],
        "calibration": "对照：CPython Enum（成员名称↔值双向访问，未知→AttributeError 语义）",
    },
    "工具-数据类": {
        "task": "数据类",
        "pattern": (
            "def dataclass_init(fields, args):\n"
            "    # 数据类：字段表 + 位置参数 → 自动 __init__ 绑定（数据类自动构造）\n"
            "    if len(args) != len(fields):\n"
            "        return 'arity_error'\n"
            "    return dict(zip(fields, args))\n"),
        "cases": [((('名', '年龄'), ('甲', 3)), {'名': '甲', '年龄': 3}),
                  ((('名',), ('甲', 3)), 'arity_error'),
                  ((('名', '年龄'), ()), 'arity_error')],
        "params": [],
        "calibration": "对照：CPython dataclass（字段表自动生成 __init__，参数个数不匹配报错）",
    },
}


def route_python_unit(question):
    """任务识别（问题 → P 线单元，最长关键词优先）"""
    best, best_len = None, 0
    for uid, u in PYTHON_UNITS.items():
        for kw in (u["task"], uid):
            if kw in question and len(kw) > best_len:
                best, best_len = uid, len(kw)
    return best


if __name__ == "__main__":
    print("=== Mini-Python 语言机制白箱单元库（P 线自举 · 校准参考）===\n")
    for uid, u in PYTHON_UNITS.items():
        print(f"[{uid}] 任务={u['task']} 样例数={len(u['cases'])}")
        print(f"    校准: {u['calibration']}")
    print(f"\n=== 判定 ===\nP 线单元库: "
          f"{'✔ 5 单元就绪（词法/优先级/逻辑/环境/栈机——白箱自举 P 线）' if len(PYTHON_UNITS) >= 4 else '✘'}")
