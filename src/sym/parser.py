# src/sym/parser.py
import ast as python_ast
from lark import Lark, Transformer, v_args
from pathlib import Path
from sym import ast

@v_args(meta=True)
class ASTTransformer(Transformer):
    # Lark passes children as a single list to each method.
    # We unpack this list as needed.

    def program(self, meta, statements): return ast.Program(statements, meta)
    def import_stmt(self, meta, children): return ast.ImportStmt(children[0], meta)
    
    # --- Values ---
    def push(self, meta, children): return ast.Push(children[0], meta)
    def integer(self, meta, children): return int(children[0].value)
    def float(self, meta, children): return float(children[0].value)
    def string(self, meta, children): return python_ast.literal_eval(children[0].value)
    def value(self, meta, children): return children[0]

    # --- Operators ---
    def add(self, meta, _): return ast.Add(meta)
    def sub(self, meta, _): return ast.Sub(meta)
    def mul(self, meta, _): return ast.Mul(meta)
    def div(self, meta, _): return ast.Div(meta)
    def mod(self, meta, _): return ast.Mod(meta)
    def eq(self, meta, _): return ast.Eq(meta)
    def neq(self, meta, _): return ast.Neq(meta)
    def lt(self, meta, _): return ast.Lt(meta)
    def gt(self, meta, _): return ast.Gt(meta)
    def lte(self, meta, _): return ast.Lte(meta)
    def gte(self, meta, _): return ast.Gte(meta)
    def and_op(self, meta, _): return ast.And(meta)
    def or_op(self, meta, _): return ast.Or(meta)
    def not_op(self, meta, _): return ast.Not(meta)
    
    # --- THIS IS THE CORRECTED SECTION ---
    def store(self, meta, children):
        # The CNAME token is the first and only child.
        return ast.Store(str(children[0].value), meta)
    
    def load(self, meta, children):
        # The CNAME token is the first and only child.
        return ast.Load(str(children[0].value), meta)
    # --- END OF CORRECTION ---

    def dup(self, meta, _): return ast.Dup(meta)
    def swap(self, meta, _): return ast.Swap(meta)
    def drop(self, meta, _): return ast.Drop(meta)
    def rot(self, meta, _): return ast.Rot(meta)

    # --- Control Flow ---
    def conditional(self, meta, children): return ast.Conditional(children[0], children[1] if len(children) > 1 else None, meta)
    def while_loop(self, meta, children): return ast.WhileLoop(children[0], children[1], meta)

    # --- Data Structures ---
    def list_literal(self, meta, children): return ast.ListLiteral(children[0], meta)
    def map_literal(self, meta, pairs): return ast.MapLiteral(pairs, meta)
    def map_pair(self, meta, children): return (children[0], children[1])
    def get_item(self, meta, _): return ast.GetItem(meta)
    def set_item(self, meta, _): return ast.SetItem(meta)
    def length(self, meta, _): return ast.Length(meta)

    # --- Functions ---
    def function_def(self, meta, children):
        name = children[0]
        body = children[-1]
        params = children[1:-1]
        return ast.FunctionDef(str(name), [str(p) for p in params], body, meta)
        
    def function_ref(self, meta, children): return ast.FunctionRef(str(children[0]), meta)
    def function_call(self, meta, _): return ast.FunctionCall(meta)

    # --- I/O & Debug ---
    def input(self, meta, _): return ast.Input(meta)
    def print(self, meta, _): return ast.Print(meta)
    def ffi_call(self, meta, _): return ast.FfiCall(meta)
    def debug_break(self, meta, _): return ast.DebugBreak(meta)

def parse_file(filepath: Path, visited_files: set) -> ast.Program:
    if filepath in visited_files:
        return ast.Program([], meta={'line': 0, 'column': 0})
    visited_files.add(filepath)

    code = filepath.read_text()
    grammar_path = Path(__file__).parent / "grammar.lark"
    
    parser = Lark(grammar_path.read_text(), start='program', parser='lalr')
    tree = parser.parse(code)
    program_ast = ASTTransformer().transform(tree)

    all_statements = []
    temp_program = []
    for stmt in program_ast.statements:
        if isinstance(stmt, ast.ImportStmt):
            import_path = filepath.parent / stmt.filename
            if not import_path.exists():
                stdlib_path = Path(__file__).parent.parent.parent / "stdlib"
                import_path = stdlib_path / stmt.filename
                if not import_path.exists():
                    raise FileNotFoundError(f"Cannot find module '{stmt.filename}' in local directory or in {stdlib_path}")
            
            imported_ast = parse_file(import_path, visited_files)
            temp_program.extend(imported_ast.statements)
    
    temp_program.extend(s for s in program_ast.statements if not isinstance(s, ast.ImportStmt))
    program_ast.statements = temp_program
    
    return program_ast