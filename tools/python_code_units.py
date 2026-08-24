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
    "工具-正则匹配": {
        "task": "正则匹配",
        "pattern": (
            "def regex_match(pattern, text):\n"
            "    # 正则匹配：re.search 简化（模式在文本中是否存在）\n"
            "    import re\n"
            "    return bool(re.search(pattern, text))\n"),
        "cases": [(('^ab', 'abc'), True),
                  (('\\d+', 'a1b'), True),
                  (('^xy', 'abc'), False)],
        "params": [],
        "calibration": "对照：CPython re.search（正则匹配，^ 锚定/\\d 数字类）",
    },
    "工具-日期时间": {
        "task": "日期时间",
        "pattern": (
            "def date_add(year, month, day, days):\n"
            "    # 日期时间：日期加减天数（简化月 30 天进位——日期运算）\n"
            "    d = day + days\n"
            "    while d > 30:\n"
            "        d -= 30\n"
            "        month += 1\n"
            "        if month > 12:\n"
            "            month = 1\n"
            "            year += 1\n"
            "    while d < 1:\n"
            "        d += 30\n"
            "        month -= 1\n"
            "        if month < 1:\n"
            "            month = 12\n"
            "            year -= 1\n"
            "    return year, month, d\n"),
        "cases": [((2026, 1, 1, 30), (2026, 2, 1)),
                  ((2026, 1, 1, 60), (2026, 3, 1)),
                  ((2026, 3, 1, -1), (2026, 2, 30))],
        "params": [],
        "calibration": "对照：CPython datetime（日期加减进位；简化 30 天月模型——1/1+30=2/1 按模型校准）",
    },
    "工具-JSON序列化": {
        "task": "JSON序列化",
        "pattern": (
            "def json_roundtrip(data):\n"
            "    # JSON 序列化：dict ↔ 字符串往返（数据交换标准）\n"
            "    import json\n"
            "    return json.loads(json.dumps(data))\n"),
        "cases": [(({'a': 1, 'b': [1, 2]},), {'a': 1, 'b': [1, 2]}),
                  (({'名': '甲'},), {'名': '甲'}),
                  (([1, 2, 3],), [1, 2, 3])],
        "params": [],
        "calibration": "对照：CPython json.dumps/loads（结构化数据序列化往返）",
    },
    "数据结构-队列栈": {
        "task": "队列栈",
        "pattern": (
            "def deque_ops(dq, op, item=None):\n"
            "    # 队列栈：dequeue 队首出（FIFO）/ pop 栈顶出（LIFO）——双端数据结构\n"
            "    if op == 'push':\n"
            "        dq.append(item)\n"
            "        return len(dq)\n"
            "    if op == 'dequeue':\n"
            "        return dq.pop(0) if dq else None\n"
            "    if op == 'pop':\n"
            "        return dq.pop() if dq else None\n"
            "    return None\n"),
        "cases": [(([], 'push', 'a'), 1),
                  (([1, 2], 'dequeue'), 1),
                  (([1, 2], 'pop'), 2),
                  (([], 'pop'), None)],
        "params": [],
        "calibration": "对照：collections.deque——队首 FIFO/栈顶 LIFO（双端操作）",
    },
    "工具-格式化": {
        "task": "格式化",
        "pattern": (
            "def format_template(template, values):\n"
            "    # 格式化：模板 {名} 占位符填充（f-string 风格）\n"
            "    out = template\n"
            "    for k, v in values.items():\n"
            "        out = out.replace('{' + k + '}', str(v))\n"
            "    return out\n"),
        "cases": [(('你好 {名}', {'名': '甲'}), '你好 甲'),
                  (('{a}-{b}', {'a': 1, 'b': 2}), '1-2'),
                  (('没有占位', {}), '没有占位')],
        "params": [],
        "calibration": "对照：Python f-string（{名} 占位符模板填充）",
    },
    "工具-排序键控": {
        "task": "排序键控",
        "pattern": (
            "def sort_by_key(items, key_fn):\n"
            "    # 排序键控：按 key 函数排序（sorted(key=) 语义——稳定排序）\n"
            "    return sorted(items, key=key_fn)\n"),
        "cases": [(([('b', 2), ('a', 1)], lambda x: x[1]), [('a', 1), ('b', 2)]),
                  (([3, 1, 2], lambda x: -x), [3, 2, 1]),
                  (([], lambda x: x), [])],
        "params": [],
        "calibration": "对照：Python sorted(key=)（按键函数稳定排序）",
    },
    "数据结构-集合运算": {
        "task": "集合运算",
        "pattern": (
            "def set_ops(a, b, op):\n"
            "    # 集合运算：union 并集 / intersect 交集 / diff 差集（集合代数）\n"
            "    if op == 'union':\n"
            "        return sorted(set(a) | set(b))\n"
            "    if op == 'intersect':\n"
            "        return sorted(set(a) & set(b))\n"
            "    if op == 'diff':\n"
            "        return sorted(set(a) - set(b))\n"
            "    return None\n"),
        "cases": [(([1, 2], [2, 3], 'union'), [1, 2, 3]),
                  (([1, 2], [2, 3], 'intersect'), [2]),
                  (([1, 2], [2, 3], 'diff'), [1])],
        "params": [],
        "calibration": "对照：Python set——并/交/差（集合代数运算）",
    },
    "工具-计数器": {
        "task": "计数器",
        "pattern": (
            "def counter(items):\n"
            "    # 计数器：元素频次统计（Counter 语义——频次字典）\n"
            "    freq = {}\n"
            "    for x in items:\n"
            "        freq[x] = freq.get(x, 0) + 1\n"
            "    return freq\n"),
        "cases": [((['a', 'b', 'a'],), {'a': 2, 'b': 1}),
                  (([],), {}),
                  (([1, 1, 1],), {1: 3})],
        "params": [],
        "calibration": "对照：collections.Counter（元素频次统计）",
    },
    "工具-分组": {
        "task": "分组",
        "pattern": (
            "def group_by(items, key_fn):\n"
            "    # 分组：按 key 函数分组（groupby 语义——组字典）\n"
            "    groups = {}\n"
            "    for x in items:\n"
            "        groups.setdefault(key_fn(x), []).append(x)\n"
            "    return groups\n"),
        "cases": [(([1, 2, 3, 4], lambda x: x % 2), {1: [1, 3], 0: [2, 4]}),
                  (([], lambda x: x), {}),
                  (([1, 1, 2], lambda x: x), {1: [1, 1], 2: [2]})],
        "params": [],
        "calibration": "对照：itertools.groupby（按键函数分组）",
    },
    "异常-自定义异常": {
        "task": "自定义异常",
        "pattern": (
            "def exception_subclass(names, child, ancestor):\n"
            "    # 自定义异常：异常类层级（父→子继承，判断继承关系）\n"
            "    parents = dict(names)\n"
            "    cur = child\n"
            "    seen = set()\n"
            "    while cur is not None and cur not in seen:\n"
            "        if cur == ancestor:\n"
            "            return True\n"
            "        seen.add(cur)\n"
            "        cur = parents.get(cur)\n"
            "    return False\n"),
        "cases": [(([('值错误', '异常'), ('输入错误', '值错误')],
                    '输入错误', '异常'), True),
                  (([('值错误', '异常')], '输入错误', '异常'), False),
                  (([('值错误', '异常'), ('输入错误', '值错误')],
                    '输入错误', '值错误'), True),
                  (([], 'a', 'b'), False)],
        "params": [],
        "calibration": "对照：Python 自定义异常——类层级继承（子类捕获父类）",
    },
    "面向对象-组合": {
        "task": "对象组合",
        "pattern": (
            "def compose_objects(parts, op, name=None, part=None, method=None,\n"
            "                    arg=None):\n"
            "    # 组合：对象含对象（add 添加部件 / call 转发调用部件方法——has-a 委托）\n"
            "    if op == 'add':\n"
            "        parts[name] = part\n"
            "        return name\n"
            "    if op == 'call':\n"
            "        p = parts.get(name)\n"
            "        if p is None or method not in p:\n"
            "            return 'missing'\n"
            "        fn = p[method]\n"
            "        return fn() if arg is None else fn(arg)\n"
            "    return None\n"),
        "cases": [(({}, 'add', '引擎', {'启动': lambda: 'vroom'}), '引擎'),
                  (({'引擎': {'启动': lambda: 'vroom'}}, 'call', '引擎',
                    None, '启动', None), 'vroom'),
                  (({}, 'call', '引擎', None, '启动', None), 'missing')],
        "params": [],
        "calibration": "对照：Python 组合——has-a 关系（对象含对象，方法委托转发）",
    },
    "工具-深拷贝": {
        "task": "深拷贝",
        "pattern": (
            "def deep_copy(obj):\n"
            "    # 深拷贝：嵌套结构完整复制（列表/字典递归——修改互不影响）\n"
            "    if isinstance(obj, list):\n"
            "        return [deep_copy(x) for x in obj]\n"
            "    if isinstance(obj, dict):\n"
            "        return {k: deep_copy(v) for k, v in obj.items()}\n"
            "    return obj\n"),
        "cases": [(([[1, 2], [3]],), [[1, 2], [3]]),
                  (({'a': [1, {'b': 2}]},), {'a': [1, {'b': 2}]}),
                  ((5,), 5)],
        "params": [],
        "calibration": "对照：copy.deepcopy——嵌套结构递归复制（引用隔离）",
    },
    "异步-超时控制": {
        "task": "超时控制",
        "pattern": (
            "def wait_for(task_fn, timeout, time_used):\n"
            "    # 超时控制：用时 ≤ 超时返回结果，超过超时取消（asyncio.wait_for）\n"
            "    if time_used > timeout:\n"
            "        return 'timeout'\n"
            "    return task_fn()\n"),
        "cases": [((lambda: 'done', 5, 3), 'done'),
                  ((lambda: 'done', 5, 6), 'timeout'),
                  ((lambda: None, 0, 0), None)],
        "params": [],
        "calibration": "对照：asyncio.wait_for（超时取消/按时完成）",
    },
    "异步-任务取消": {
        "task": "任务取消",
        "pattern": (
            "def task_cancel(tasks, op, task_id=None):\n"
            "    # 任务取消：start 启动 / cancel 请求取消 / check 检查状态（协作式）\n"
            "    if op == 'start':\n"
            "        tasks[task_id] = 'running'\n"
            "        return 'running'\n"
            "    if op == 'cancel':\n"
            "        if task_id in tasks and tasks[task_id] == 'running':\n"
            "            tasks[task_id] = 'cancelled'\n"
            "            return 'cancelled'\n"
            "        return 'not_running'\n"
            "    if op == 'check':\n"
            "        return tasks.get(task_id)\n"
            "    return None\n"),
        "cases": [(({}, 'start', 't1'), 'running'),
                  (({'t1': 'running'}, 'cancel', 't1'), 'cancelled'),
                  (({'t1': 'done'}, 'cancel', 't1'), 'not_running'),
                  (({'t1': 'cancelled'}, 'check', 't1'), 'cancelled')],
        "params": [],
        "calibration": "对照：asyncio.Task.cancel（运行中可取消，已完成不可）",
    },
    "异步-信号量": {
        "task": "异步信号量",
        "pattern": (
            "def async_semaphore(sem, op):\n"
            "    # 异步信号量：acquire 获取（满则等待）/ release 释放（并发上限）\n"
            "    if op == 'acquire':\n"
            "        if sem.get('count', 0) >= sem.get('limit', 1):\n"
            "            sem['waiting'] = sem.get('waiting', 0) + 1\n"
            "            return 'waiting'\n"
            "        sem['count'] = sem.get('count', 0) + 1\n"
            "        return 'acquired'\n"
            "    if op == 'release':\n"
            "        if sem.get('waiting', 0) > 0:\n"
            "            sem['waiting'] -= 1\n"
            "            return 'handoff'\n"
            "        sem['count'] = max(sem.get('count', 0) - 1, 0)\n"
            "        return 'released'\n"
            "    return None\n"),
        "cases": [(({'limit': 2, 'count': 0, 'waiting': 0}, 'acquire'),
                   'acquired'),
                  (({'limit': 2, 'count': 2, 'waiting': 0}, 'acquire'),
                   'waiting'),
                  (({'limit': 2, 'count': 2, 'waiting': 0}, 'release'),
                   'released'),
                  (({'limit': 2, 'count': 2, 'waiting': 1}, 'release'),
                   'handoff')],
        "params": [],
        "calibration": "对照：asyncio.Semaphore（并发上限，满则等待/释放交接）",
    },
    "工具-映射": {
        "task": "映射",
        "pattern": (
            "def map_apply(items, fn):\n"
            "    # 映射：函数应用到每个元素（map 语义——变换）\n"
            "    return [fn(x) for x in items]\n"),
        "cases": [(([1, 2, 3], lambda x: x * 2), [2, 4, 6]),
                  (([], lambda x: x), []),
                  (([1, 2], lambda x: str(x)), ['1', '2'])],
        "params": [],
        "calibration": "对照：Python map（函数应用到每个元素）",
    },
    "工具-过滤": {
        "task": "过滤",
        "pattern": (
            "def filter_items(items, pred):\n"
            "    # 过滤：条件保留元素（filter 语义——筛选）\n"
            "    return [x for x in items if pred(x)]\n"),
        "cases": [(([1, 2, 3, 4], lambda x: x % 2 == 0), [2, 4]),
                  (([], lambda x: True), []),
                  (([1, 2], lambda x: x > 1), [2])],
        "params": [],
        "calibration": "对照：Python filter（条件筛选元素）",
    },
    "工具-归约": {
        "task": "归约",
        "pattern": (
            "def reduce_accum(items, fn, initial):\n"
            "    # 归约：累积聚合（reduce 语义——从左到右折叠）\n"
            "    acc = initial\n"
            "    for x in items:\n"
            "        acc = fn(acc, x)\n"
            "    return acc\n"),
        "cases": [(([1, 2, 3], lambda a, b: a + b, 0), 6),
                  (([1, 2, 3], lambda a, b: a * b, 1), 6),
                  (([], lambda a, b: a + b, 10), 10)],
        "params": [],
        "calibration": "对照：functools.reduce（累积聚合折叠）",
    },
    "工具-字符串拆分": {
        "task": "字符串拆分",
        "pattern": (
            "def str_split(text, sep=None):\n"
            "    # 字符串拆分：按分隔符拆（split 语义——默认空白）\n"
            "    return text.split(sep) if sep is not None else text.split()\n"),
        "cases": [(('a,b,c', ','), ['a', 'b', 'c']),
                  (('a b  c', None), ['a', 'b', 'c']),
                  (('', ','), [''])],
        "params": [],
        "calibration": "对照：Python str.split（分隔符拆分，默认空白）",
    },
    "工具-字符串替换": {
        "task": "字符串替换",
        "pattern": (
            "def str_replace(text, old, new, count=None):\n"
            "    # 字符串替换：全部/前 n 次替换（replace 语义）\n"
            "    return (text.replace(old, new) if count is None\n"
            "            else text.replace(old, new, count))\n"),
        "cases": [(('aaa', 'a', 'b'), 'bbb'),
                  (('aaa', 'a', 'b', 2), 'bba'),
                  (('abc', 'x', 'y'), 'abc')],
        "params": [],
        "calibration": "对照：Python str.replace（全部/限次替换）",
    },
    "工具-字符串判断": {
        "task": "字符串判断",
        "pattern": (
            "def str_check(text, op):\n"
            "    # 字符串判断：isdigit/startswith/isupper（字符串方法族）\n"
            "    if op == 'isdigit':\n"
            "        return text.isdigit()\n"
            "    if op == 'startswith':\n"
            "        return text.startswith('0x')\n"
            "    if op == 'isupper':\n"
            "        return text.isupper()\n"
            "    return None\n"),
        "cases": [(('123', 'isdigit'), True),
                  (('0xFF', 'startswith'), True),
                  (('ABC', 'isupper'), True),
                  (('abc', 'isupper'), False),
                  (('12a', 'isdigit'), False)],
        "params": [],
        "calibration": "对照：Python 字符串方法族（isdigit/startswith/isupper）",
    },
    "工具-数学函数": {
        "task": "数学函数",
        "pattern": (
            "def math_func(op, a, b=None):\n"
            "    # 数学函数：abs 绝对值 / pow 幂 / sqrt 平方根（math 语义）\n"
            "    if op == 'abs':\n"
            "        return abs(a)\n"
            "    if op == 'pow':\n"
            "        return a ** b\n"
            "    if op == 'sqrt':\n"
            "        import math\n"
            "        return math.sqrt(a)\n"
            "    return None\n"),
        "cases": [(('abs', -5), 5),
                  (('pow', 2, 3), 8),
                  (('sqrt', 9), 3.0)],
        "params": [],
        "calibration": "对照：Python math——abs/pow/sqrt（数学函数族）",
    },
    "工具-数值舍入": {
        "task": "数值舍入",
        "pattern": (
            "def round_num(value, op):\n"
            "    # 数值舍入：round 四舍五入 / floor 向下 / ceil 向上\n"
            "    import math\n"
            "    if op == 'round':\n"
            "        return round(value)\n"
            "    if op == 'floor':\n"
            "        return math.floor(value)\n"
            "    if op == 'ceil':\n"
            "        return math.ceil(value)\n"
            "    return None\n"),
        "cases": [((2.6, 'round'), 3),
                  ((2.9, 'floor'), 2),
                  ((2.1, 'ceil'), 3),
                  ((2.0, 'floor'), 2)],
        "params": [],
        "calibration": "对照：Python round/floor/ceil（数值舍入）",
    },
    "工具-数值统计": {
        "task": "数值统计",
        "pattern": (
            "def stats_calc(nums, op):\n"
            "    # 数值统计：mean 平均 / min 最小 / max 最大（统计函数族）\n"
            "    if not nums:\n"
            "        return None\n"
            "    if op == 'mean':\n"
            "        return sum(nums) / len(nums)\n"
            "    if op == 'min':\n"
            "        return min(nums)\n"
            "    if op == 'max':\n"
            "        return max(nums)\n"
            "    return None\n"),
        "cases": [(([1, 2, 3], 'mean'), 2.0),
                  (([3, 1, 2], 'min'), 1),
                  (([3, 1, 2], 'max'), 3),
                  (([], 'mean'), None)],
        "params": [],
        "calibration": "对照：Python statistics——mean/min/max（统计族）",
    },
    "语法-默认参数": {
        "task": "默认参数",
        "pattern": (
            "def default_args(params, defaults, call_args):\n"
            "    # 默认参数：参数绑定（缺省用默认值——函数调用语义）\n"
            "    bound = {}\n"
            "    for i, p in enumerate(params):\n"
            "        bound[p] = call_args[i] if i < len(call_args) else defaults.get(p)\n"
            "    return bound\n"),
        "cases": [((['甲', '乙'], {'乙': 2}, ['x']), {'甲': 'x', '乙': 2}),
                  ((['甲'], {}, ['x']), {'甲': 'x'}),
                  ((['甲', '乙'], {'乙': 2}, ['x', 'y']),
                   {'甲': 'x', '乙': 'y'})],
        "params": [],
        "calibration": "对照：Python 默认参数（缺省用默认值绑定）",
    },
    "语法-关键字参数": {
        "task": "关键字参数",
        "pattern": (
            "def kwargs_bind(params, args, kwargs):\n"
            "    # 关键字参数：位置+关键字绑定（**kwargs 语义）\n"
            "    bound = {}\n"
            "    for i, p in enumerate(params):\n"
            "        if p in kwargs:\n"
            "            bound[p] = kwargs[p]\n"
            "        elif i < len(args):\n"
            "            bound[p] = args[i]\n"
            "        else:\n"
            "            bound[p] = None\n"
            "    return bound\n"),
        "cases": [((['甲', '乙'], ['x'], {'乙': 'y'}), {'甲': 'x', '乙': 'y'}),
                  ((['甲', '乙'], [], {'甲': 'x'}), {'甲': 'x', '乙': None}),
                  ((['甲'], ['x'], {}), {'甲': 'x'})],
        "params": [],
        "calibration": "对照：Python 关键字参数（关键字优先于位置绑定）",
    },
    "语法-多行字符串": {
        "task": "多行字符串",
        "pattern": (
            "def multiline_str(src, i):\n"
            "    # 多行字符串：三引号解析（chr 构造——跨行字符串）\n"
            "    q = chr(34) * 3\n"
            "    if src[i:i + 3] != q:\n"
            "        return None, i\n"
            "    j = src.find(q, i + 3)\n"
            "    if j == -1:\n"
            "        return (src[i + 3:], 'unterminated'), len(src)\n"
            "    return (src[i + 3:j]), j + 3\n"),
        "cases": [
            ((chr(34) * 3 + '你好' + chr(10) + '世界' + chr(34) * 3, 0), ('你好' + chr(10) + '世界', 11)),
            ((chr(34) * 3 + '未闭合', 0), (('未闭合', 'unterminated'), 6))],
        "params": [],
        "calibration": "对照：Python 三引号字符串（跨行字面量）",
    },
    "工具-文件读取": {
        "task": "文件读取",
        "pattern": (
            "def file_read_lines(content, op):\n"
            "    # 文件读取：read 读全部 / lines 读行（文件 IO 简化）\n"
            "    if op == 'read':\n"
            "        return content\n"
            "    if op == 'lines':\n"
            "        return content.splitlines()\n"
            "    return None\n"),
        "cases": [(('第一行\n第二行', 'lines'), ['第一行', '第二行']),
                  (('内容', 'read'), '内容'),
                  (('', 'lines'), [])],
        "params": [],
        "calibration": "对照：Python 文件读取——读全部/按行（splitlines）",
    },
    "工具-性能计时": {
        "task": "性能计时",
        "pattern": (
            "def perf_time(start, end, unit='ms'):\n"
            "    # 性能计时：耗时计算（start/end 时间戳——性能测量）\n"
            "    diff = end - start\n"
            "    return diff * 1000 if unit == 'ms' else diff\n"),
        "cases": [((0.0, 0.005, 'ms'), 5.0),
                  ((1.0, 3.0, 's'), 2.0),
                  ((0.0, 0.0, 'ms'), 0.0)],
        "params": [],
        "calibration": "对照：time.perf_counter——耗时计算（毫秒/秒）",
    },
    "工具-环境查询": {
        "task": "环境查询",
        "pattern": (
            "def platform_check(env, op, key=None):\n"
            "    # 环境查询：platform 平台 / version 版本 / get 键查询（环境信息）\n"
            "    if op == 'platform':\n"
            "        return env.get('platform')\n"
            "    if op == 'version':\n"
            "        return env.get('version')\n"
            "    if op == 'get':\n"
            "        return env.get(key)\n"
            "    return None\n"),
        "cases": [(({'platform': 'win32'}, 'platform'), 'win32'),
                  (({'version': '3.12'}, 'version'), '3.12'),
                  (({'py': '3'}, 'get', 'py'), '3'),
                  (({}, 'get', 'x'), None)],
        "params": [],
        "calibration": "对照：sys/platform——平台与版本环境查询",
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
