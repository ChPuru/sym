# src/sym/interpreter.py

import sys
from typing import Any, Dict, List
from sym import ast

class Frame:
    """Represents a single frame on the call stack, holding local variables."""
    def __init__(self):
        self.variables: Dict[str, Any] = {}

class Interpreter:
    """Directly executes the program from the AST, managing state and scope."""
    def __init__(self):
        self.stack: List[Any] = []
        self.functions: Dict[str, ast.FunctionDef] = {}
        # The call stack starts with one global frame
        self.call_stack: List[Frame] = [Frame()]

    def visit(self, node: ast.ASTNode):
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name)
        return visitor(node)

    def run(self, node: ast.ASTNode):
        return self.visit(node)

    def visit_Program(self, node: ast.Program):
        for statement in node.statements:
            self.visit(statement)

    # --- Values & Operators ---
    def visit_Push(self, node: ast.Push): self.stack.append(node.value)
    def visit_Add(self, node: ast.Add): self.stack.append(self.stack.pop() + self.stack.pop())
    def visit_Sub(self, node: ast.Sub): b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a - b)
    def visit_Mul(self, node: ast.Mul): self.stack.append(self.stack.pop() * self.stack.pop())
    def visit_Div(self, node: ast.Div):
        b, a = self.stack.pop(), self.stack.pop()
        if b == 0: raise ZeroDivisionError("Cannot divide by zero.")
        self.stack.append(a / b if isinstance(a, float) or isinstance(b, float) else a // b)
    def visit_Print(self, node: ast.Print):
        val = self.stack.pop(); print(val, end="" if isinstance(val, str) else " ")

    # --- Variables ---
    def visit_Store(self, node: ast.Store):
        if not self.stack: raise IndexError("Store operation requires a value on the stack.")
        self.call_stack[-1].variables[node.name] = self.stack.pop()
    def visit_Load(self, node: ast.Load):
        if node.name not in self.call_stack[-1].variables: raise NameError(f"Variable ':{node.name}' is not defined.")
        self.stack.append(self.call_stack[-1].variables[node.name])

    # --- Stack Ops ---
    def visit_Dup(self, node: ast.Dup): self.stack.append(self.stack[-1])
    def visit_Swap(self, node: ast.Swap): self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]
    def visit_Drop(self, node: ast.Drop): self.stack.pop()
    def visit_Rot(self, node: ast.Rot): self.stack[-1], self.stack[-2], self.stack[-3] = self.stack[-2], self.stack[-3], self.stack[-1]

    # --- Control Flow ---
    def visit_Conditional(self, node: ast.Conditional):
        if self.stack.pop() != 0:
            self.visit(node.then_block)
        elif node.else_block:
            self.visit(node.else_block)

    def visit_WhileLoop(self, node: ast.WhileLoop):
        self.visit(node.condition_block)
        while self.stack.pop() != 0:
            self.visit(node.body_block)
            self.visit(node.condition_block)

    # --- Lists ---
    def visit_ListLiteral(self, node: ast.ListLiteral):
        # Execute the list's program in isolation to generate its items
        list_interpreter = Interpreter()
        list_interpreter.functions = self.functions # Share function definitions
        list_interpreter.call_stack = self.call_stack # Share variable scope
        list_interpreter.run(node.program)
        self.stack.append(list_interpreter.stack)

    def visit_Get(self, node: ast.Get):
        index, L = self.stack.pop(), self.stack.pop(); self.stack.append(L[index])
    def visit_Set(self, node: ast.Set):
        value, index, L = self.stack.pop(), self.stack.pop(), self.stack.pop()
        L[index] = value; self.stack.append(L)
    def visit_Length(self, node: ast.Length): self.stack.append(len(self.stack.pop()))

    # --- Functions ---
    def visit_FunctionDef(self, node: ast.FunctionDef): self.functions[node.name] = node
    def visit_FunctionCall(self, node: ast.FunctionCall):
        if node.name not in self.functions: raise NameError(f"Function '{node.name}' is not defined.")
        func_def = self.functions[node.name]

        # Create a new frame for the function's scope
        new_frame = Frame()
        # Pop args and assign to params in the new frame
        for param_name in reversed(func_def.params):
            if not self.stack: raise IndexError(f"Not enough arguments for function '{node.name}'.")
            new_frame.variables[param_name] = self.stack.pop()

        self.call_stack.append(new_frame)
        self.visit(func_def.body)
        self.call_stack.pop() # Destroy frame on return

    # --- I/O ---
    def visit_Input(self, node: ast.Input): self.stack.append(sys.stdin.readline().strip())