# src/sym/compiler.py
from typing import Dict, List, Tuple
from sym import ast, bytecode

class Compiler:
    def __init__(self):
        self.chunks = {}
        self.debug_maps = {}
        self.visiting_chunk = None
        self.visiting_debug_map = None

    def compile(self, program: ast.Program) -> Tuple[Dict, Dict]:
        # Compile functions first
        for stmt in program.statements:
            if isinstance(stmt, ast.FunctionDef):
                self.visit(stmt)
        
        # Compile the main script body
        self.visiting_chunk = []
        self.visiting_debug_map = []
        for stmt in program.statements:
            if not isinstance(stmt, ast.FunctionDef):
                self.visit(stmt)
        
        self.emit(bytecode.Opcode.HALT, node=program)
        self.chunks['__main__'] = self.visiting_chunk
        self.debug_maps['__main__'] = self.visiting_debug_map
        
        return self.chunks, self.debug_maps

    def emit(self, *opcodes, node: ast.ASTNode):
        for _ in opcodes:
            self.visiting_debug_map.append((node.line, node.column))
        self.visiting_chunk.extend(opcodes)
    
    def emit_jump(self, opcode, node):
        self.emit(opcode, 0, node=node)
        return len(self.visiting_chunk) - 1

    def patch_jump(self, jump_addr):
        self.visiting_chunk[jump_addr] = len(self.visiting_chunk)

    def visit(self, node: ast.ASTNode):
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"Compiler cannot visit {type(node).__name__}")

    def visit_Program(self, node: ast.Program):
        for stmt in node.statements: self.visit(stmt)

    def visit_Push(self, node: ast.Push): self.emit(bytecode.Opcode.PUSH, node.value, node=node)
    def visit_Add(self, node: ast.Add): self.emit(bytecode.Opcode.ADD, node=node)
    def visit_Sub(self, node: ast.Sub): self.emit(bytecode.Opcode.SUB, node=node)
    def visit_Mul(self, node: ast.Mul): self.emit(bytecode.Opcode.MUL, node=node)
    def visit_Div(self, node: ast.Div): self.emit(bytecode.Opcode.DIV, node=node)
    def visit_Mod(self, node: ast.Mod): self.emit(bytecode.Opcode.MOD, node=node)
    def visit_Eq(self, node: ast.Eq): self.emit(bytecode.Opcode.EQ, node=node)
    def visit_Neq(self, node: ast.Neq): self.emit(bytecode.Opcode.NEQ, node=node)
    def visit_Lt(self, node: ast.Lt): self.emit(bytecode.Opcode.LT, node=node)
    def visit_Gt(self, node: ast.Gt): self.emit(bytecode.Opcode.GT, node=node)
    def visit_Lte(self, node: ast.Lte): self.emit(bytecode.Opcode.LTE, node=node)
    def visit_Gte(self, node: ast.Gte): self.emit(bytecode.Opcode.GTE, node=node)
    def visit_And(self, node: ast.And): self.emit(bytecode.Opcode.AND, node=node)
    def visit_Or(self, node: ast.Or): self.emit(bytecode.Opcode.OR, node=node)
    def visit_Not(self, node: ast.Not): self.emit(bytecode.Opcode.NOT, node=node)
    
    def visit_Store(self, node: ast.Store): self.emit(bytecode.Opcode.STORE_NAME, node.name, node=node)
    def visit_Load(self, node: ast.Load): self.emit(bytecode.Opcode.LOAD_NAME, node.name, node=node)
    
    def visit_Dup(self, node: ast.Dup): self.emit(bytecode.Opcode.DUP, node=node)
    def visit_Swap(self, node: ast.Swap): self.emit(bytecode.Opcode.SWAP, node=node)
    def visit_Drop(self, node: ast.Drop): self.emit(bytecode.Opcode.DROP, node=node)
    def visit_Rot(self, node: ast.Rot): self.emit(bytecode.Opcode.ROT, node=node)
    
    def visit_Print(self, node: ast.Print): self.emit(bytecode.Opcode.PRINT, node=node)
    def visit_Input(self, node: ast.Input): self.emit(bytecode.Opcode.INPUT, node=node)
    def visit_DebugBreak(self, node: ast.DebugBreak): self.emit(bytecode.Opcode.DBG, node=node)

    def visit_Conditional(self, node: ast.Conditional):
        # The condition value is already on the stack.
        jump_if_false_addr = self.emit_jump(bytecode.Opcode.JUMP_IF_FALSE, node)
        self.visit(node.then_block)
        jump_to_end_addr = 0
        if node.else_block:
            jump_to_end_addr = self.emit_jump(bytecode.Opcode.JUMP, node)
        self.patch_jump(jump_if_false_addr)
        if node.else_block:
            self.visit(node.else_block)
            self.patch_jump(jump_to_end_addr)

    def visit_WhileLoop(self, node: ast.WhileLoop):
        loop_start_addr = len(self.visiting_chunk)
        self.visit(node.condition_block)
        exit_jump_addr = self.emit_jump(bytecode.Opcode.JUMP_IF_FALSE, node)
        self.visit(node.body_block)
        self.emit(bytecode.Opcode.JUMP, loop_start_addr, node=node)
        self.patch_jump(exit_jump_addr)
        
    def visit_ListLiteral(self, node: ast.ListLiteral):
        num_items = len(node.program.statements)
        self.visit(node.program)
        self.emit(bytecode.Opcode.BUILD_LIST, num_items, node=node)

    def visit_MapLiteral(self, node: ast.MapLiteral):
        for key, value_prog in node.pairs:
            self.emit(bytecode.Opcode.PUSH, key, node=node)
            self.visit(value_prog)
        self.emit(bytecode.Opcode.BUILD_MAP, len(node.pairs), node=node)

    def visit_GetItem(self, node: ast.GetItem): self.emit(bytecode.Opcode.GET_ITEM, node=node)
    def visit_SetItem(self, node: ast.SetItem): self.emit(bytecode.Opcode.SET_ITEM, node=node)
    def visit_Length(self, node: ast.Length): self.emit(bytecode.Opcode.LEN, node=node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        original_chunk = self.visiting_chunk
        original_debug_map = self.visiting_debug_map
        
        self.visiting_chunk = []
        self.visiting_debug_map = []
        
        self.visit(node.body)
        self.emit(bytecode.Opcode.RETURN, node=node)
        
        self.chunks[node.name] = (node.params, self.visiting_chunk)
        self.debug_maps[node.name] = self.visiting_debug_map
        
        self.visiting_chunk = original_chunk
        self.visiting_debug_map = original_debug_map
        
    def visit_FunctionRef(self, node: ast.FunctionRef):
        self.emit(bytecode.Opcode.BUILD_CLOSURE, node.name, node=node)
        
    def visit_FunctionCall(self, node: ast.FunctionCall):
        self.emit(bytecode.Opcode.CALL, node=node)
    
    def visit_FfiCall(self, node: ast.FfiCall):
        self.emit(bytecode.Opcode.FFI_CALL, node=node)