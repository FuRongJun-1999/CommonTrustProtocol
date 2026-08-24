"""
compiler.py · 中文源码 → 智能论字节码（第六阶段 C2）
AST（protocol-compiler parser）→ VM 指令（condition_vm）：
  若…则…否则 → JUMP_IF_FALSE + JUMP（条件跳转）
  道德经指令（道/德/自然/无为/止/知足）→ DAO/DE/ZIRAN/WUWEI/ZHI/ZHIZU
  术曰块 → ENTER_SHUYUE/RETURN_STEP（作用域）
  赋值 → STORE_NAME；比较/算术 → CMP_*/ADD/SUB/MUL/DIV
名实校验（NameChecker）为编译期静态检查（以名举实）——C2 智能论语义。
对照 v0.2 codegen 语义：DAO=create_path(条件空间)、DE=accumulate_trust(信任累积)、
若则=if——VM 执行结果与声明语义一致。
"""

from .lexer import tokenize, TokenType
from .parser import parse_tokens, NodeType
from .name_checker import NameChecker
from .condition_vm import Opcode


# 中文比较词 → VM 比较指令（codegen CHINESE_COMP_MAP 同构）
COMP_MAP = {
    "==": Opcode.CMP_EQ, "等于": Opcode.CMP_EQ,
    ">": Opcode.CMP_GT, "大于": Opcode.CMP_GT,
    "<": Opcode.CMP_LT, "小于": Opcode.CMP_LT,
    "!=": Opcode.CMP_NE, "不等于": Opcode.CMP_NE,
    "<=": Opcode.CMP_LE, "不大于": Opcode.CMP_LE,
    ">=": Opcode.CMP_GE, "不小于": Opcode.CMP_GE,
}

# 算术运算符 → VM 指令（含中文算术词）
ARITH_MAP = {"+": Opcode.ADD, "-": Opcode.SUB,
             "*": Opcode.MUL, "/": Opcode.DIV,
             "加": Opcode.ADD, "减": Opcode.SUB,
             "乘": Opcode.MUL, "除": Opcode.DIV}


class Compiler:
    """AST → 字节码（标签回填）"""

    def __init__(self):
        self.code = []
        self.labels = {}
        self.pending = []      # [(index, label)]
        self.zhizu_labels = [] # 知足标签（达标跳程序末尾）
        self.label_count = 0
        self.warnings = []

    def compile(self, ast):
        for stmt in ast.statements:
            self._stmt(stmt)
        # 知足标签 place 到程序末尾（信任达标=满足结束，对齐白箱单元语义）
        for lbl in self.zhizu_labels:
            self._place(lbl)
        self._resolve()
        return self.code

    # ---- 标签 ----
    def _new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def _place(self, label):
        self.labels[label] = len(self.code)

    def _emit(self, op, arg=None):
        self.code.append((op, arg))

    def _resolve(self):
        for idx, label in self.pending:
            if label not in self.labels:
                raise SyntaxError(f"未定义标签 {label}")
            op, arg = self.code[idx]
            if op == Opcode.ZHIZU:
                self.code[idx] = (op, (arg[0], self.labels[label]))
            else:
                self.code[idx] = (op, self.labels[label])

    # ---- 语句 ----
    def _stmt(self, s):
        if s is None:
            return
        if s.type == NodeType.SHUYUE:
            self._emit(Opcode.ENTER_SHUYUE)
            for step in s.steps:
                self._stmt(step.statement)
            self._emit(Opcode.RETURN_STEP)
        elif s.type == NodeType.CONDITION_STMT:
            self._expr(s.condition)
            else_lbl = self._new_label()
            end_lbl = self._new_label()
            self._emit(Opcode.JUMP_IF_FALSE, else_lbl)
            self.pending.append((len(self.code) - 1, else_lbl))
            self._stmt(s.then_body)
            self._emit(Opcode.JUMP, end_lbl)
            self.pending.append((len(self.code) - 1, end_lbl))
            self._place(else_lbl)
            self._stmt(s.else_body)
            self._place(end_lbl)
        elif s.type == NodeType.LOOP_STMT:
            # 当…执行（while 语义）：条件 → JIF 跳出 → 体 → JUMP 回条件
            start_lbl = self._new_label()
            exit_lbl = self._new_label()
            self._place(start_lbl)
            self._expr(s.condition)
            self._emit(Opcode.JUMP_IF_FALSE, exit_lbl)
            self.pending.append((len(self.code) - 1, exit_lbl))
            self._stmt(s.body)
            self._emit(Opcode.JUMP, start_lbl)
            self.pending.append((len(self.code) - 1, start_lbl))
            self._place(exit_lbl)
        elif s.type == NodeType.INSTRUCTION_STMT:
            self._instr(s)
        elif s.type == NodeType.ASSIGN_STMT:
            self._expr(s.value_node)
            self._emit(Opcode.STORE_NAME, s.target)
        elif s.type in (NodeType.WENYUE, NodeType.DAYUE):
            pass  # 注释性结构（问曰/答曰）
        else:
            self.warnings.append(f"L{s.line} 未编译语句类型: {s.type.name}")

    # ---- 道德经指令 ----
    def _instr(self, s):
        op = s.instruction
        operands = s.operands
        val = self._operand_value(operands[0]) if operands else None
        if op == TokenType.DAO:
            self._emit(Opcode.DAO, val if val is not None else "无名路径")
        elif op == TokenType.DE:
            try:
                self._emit(Opcode.DE, float(val) if val is not None else 0.0)
            except (TypeError, ValueError):
                # 以名举实：非数值操作数（未声明标识符）编译期拦截——名实不符
                raise SyntaxError(
                    f"L{s.line} 德 的操作数必须是数值，得到 '{val}'（名实不符）")
        elif op == TokenType.ZIRAN:
            self._emit(Opcode.ZIRAN)
        elif op == TokenType.WUWEI:
            self._emit(Opcode.WUWEI)
        elif op == TokenType.ZHI:
            self._emit(Opcode.ZHI)
        elif op == TokenType.ZHIZU:
            threshold = float(val) if val is not None else 0.0
            lbl = self._new_label()
            self._emit(Opcode.ZHIZU, (threshold, lbl))
            self.pending.append((len(self.code) - 1, lbl))
            self.zhizu_labels.append(lbl)  # 达标跳程序末尾（满足）
        else:
            self.warnings.append(f"L{s.line} 指令 {op.name} 未接入 VM（诚实边界）")

    def _operand_value(self, node):
        if node.type == NodeType.LITERAL:
            return node.literal_value
        if node.type == NodeType.IDENTIFIER:
            return node.name
        return None

    # ---- 表达式 ----
    def _expr(self, e):
        if e is None:
            self._emit(Opcode.PUSH_CONST, None)
            return
        if e.type == NodeType.LITERAL:
            self._emit(Opcode.PUSH_CONST, e.literal_value)
        elif e.type == NodeType.IDENTIFIER:
            self._emit(Opcode.LOAD_NAME, e.name)
        elif e.type == NodeType.COMPARISON:
            self._expr(e.left)
            self._expr(e.right)
            op = COMP_MAP.get(e.op)
            if op is None:
                self.warnings.append(f"L{e.line} 未知比较词 '{e.op}'")
                return
            self._emit(op)
        elif e.type == NodeType.BINARY_EXPR:
            self._expr(e.left)
            self._expr(e.right)
            op = ARITH_MAP.get(e.operator)
            if op is None:
                self.warnings.append(f"L{e.line} 未知运算符 '{e.operator}'")
                return
            self._emit(op)
        else:
            self.warnings.append(f"L{e.line} 未编译表达式: {e.type.name}")


def compile_source(source, strict=True):
    """中文源码 → 字节码（含名实校验静态检查）
    返回 (code, result)：result = {ok, errors, warnings, name_errors}"""
    tokens, lex_errors = tokenize(source)
    errors = list(lex_errors or [])
    ast = parse_tokens(tokens, errors)
    if errors:
        return None, {"ok": False, "errors": errors, "warnings": []}
    # 名实校验（以名举实·静态检查——C2 智能论语义）
    checker = NameChecker()
    name_errors, name_warnings = checker.check(ast)
    if strict and name_errors:
        return None, {"ok": False, "errors": name_errors,
                      "warnings": name_warnings, "name_errors": name_errors}
    compiler = Compiler()
    try:
        code = compiler.compile(ast)
    except SyntaxError as e:
        return None, {"ok": False, "errors": [str(e)],
                      "warnings": [], "name_errors": [str(e)]}
    return code, {"ok": True, "errors": [], "warnings": compiler.warnings}


if __name__ == "__main__":
    print("=== C2：中文源码 → 智能论字节码（对照 v0.2 语义）===\n")
    src = """
问曰：如何验证信任？
答曰：信任值大于0.7。
术曰：
1。道 新信任路径；
2。若 信任值 大于 0.3，则 德 0.5；
3。知足 0.7；
4。止。
"""
    code, result = compile_source(src)
    if not result["ok"]:
        print("编译错误:", result["errors"][:3])
    else:
        print("① 字节码（" + str(len(code)) + " 条指令）：")
        for i, (op, arg) in enumerate(code):
            print(f"   {i:3d} {op.name:14s} {arg}")
        from .condition_vm import ConditionVM
        vm = ConditionVM()
        state = vm.run(code)
        print(f"\n② VM 执行: 信任={state['trust']} 条件空间={state['condition_space']} "
              f"停止={state['halt']}")
        ok = state["trust"] >= 0.7 and state["condition_space"]
        print(f"\n=== 判定 ===\n中文源码原生执行: "
              f"{'✔ 若则/道德经指令/术曰 在 VM 上运行（零 Python 运行时）' if ok else '✘'}")
