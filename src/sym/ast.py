# src/sym/ast.py
from typing import List, Optional, Any, Tuple

class ASTNode:
    """Base class for all AST nodes, stores location info."""
    def __init__(self, meta):
        self.line = getattr(meta, 'line', -1)
        self.column = getattr(meta, 'column', -1)

# --- Base ---
class Program(ASTNode):
    def __init__(self, statements: List[ASTNode], meta=None):
        super().__init__(meta or {})
        self.statements = statements

class ImportStmt(ASTNode):
    def __init__(self, filename: str, meta):
        super().__init__(meta)
        self.filename = filename

# --- Values ---
class Push(ASTNode):
    def __init__(self, value: Any, meta):
        super().__init__(meta)
        self.value = value

# --- Operators ---
class Add(ASTNode): pass
class Sub(ASTNode): pass
class Mul(ASTNode): pass
class Div(ASTNode): pass
class Mod(ASTNode): pass
class Eq(ASTNode): pass
class Neq(ASTNode): pass
class Lt(ASTNode): pass
class Gt(ASTNode): pass
class Lte(ASTNode): pass
class Gte(ASTNode): pass
class And(ASTNode): pass
class Or(ASTNode): pass
class Not(ASTNode): pass

# --- Variables & Stack ---
class Store(ASTNode):
    def __init__(self, name: str, meta):
        super().__init__(meta)
        self.name = name

class Load(ASTNode):
    def __init__(self, name: str, meta):
        super().__init__(meta)
        self.name = name

class Dup(ASTNode): pass
class Swap(ASTNode): pass
class Drop(ASTNode): pass
class Rot(ASTNode): pass

# --- Control Flow ---
class Conditional(ASTNode):
    def __init__(self, then_block: Program, else_block: Optional[Program], meta):
        super().__init__(meta)
        self.then_block = then_block
        self.else_block = else_block

class WhileLoop(ASTNode):
    def __init__(self, condition_block: Program, body_block: Program, meta):
        super().__init__(meta)
        self.condition_block = condition_block
        self.body_block = body_block

# --- Data Structures ---
class ListLiteral(ASTNode):
    def __init__(self, program: Program, meta):
        super().__init__(meta)
        self.program = program

class MapLiteral(ASTNode):
    def __init__(self, pairs: List[Tuple[Any, Program]], meta):
        super().__init__(meta)
        self.pairs = pairs

class GetItem(ASTNode): pass
class SetItem(ASTNode): pass
class Length(ASTNode): pass

# --- Functions ---
class FunctionDef(ASTNode):
    def __init__(self, name: str, params: List[str], body: Program, meta):
        super().__init__(meta)
        self.name = name
        self.params = params
        self.body = body

class FunctionRef(ASTNode):
    def __init__(self, name: str, meta):
        super().__init__(meta)
        self.name = name

class FunctionCall(ASTNode): pass

# --- I/O & Debug ---
class Input(ASTNode): pass
class Print(ASTNode): pass
class FfiCall(ASTNode): pass
class DebugBreak(ASTNode): pass