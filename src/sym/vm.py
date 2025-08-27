# src/sym/vm.py
import sys
import ctypes
from typing import List, Dict, Any, Tuple

from sym.bytecode import Opcode

# --- VM Object Models ---
class Closure:
    def __init__(self, name, params, chunk):
        self.name = name; self.params = params; self.chunk = chunk
    def __repr__(self): return f"<closure {self.name}>"

class Frame:
    def __init__(self, closure: Closure, ip: int, stack_start: int):
        self.closure = closure; self.ip = ip; self.stack_start = stack_start
        self.locals: Dict[str, Any] = {}

# --- The Virtual Machine ---
class VirtualMachine:
    def __init__(self, chunks: Dict, debug_maps: Dict):
        self.chunks = chunks
        self.debug_maps = debug_maps
        self.stack: List[Any] = []
        self.call_stack: List[Frame] = []
        self.ffi_libs = {}
        self.globals: Dict[str, Any] = {} # The global scope dictionary

        # Setup main frame
        main_closure = Closure('__main__', [], chunks['__main__'])
        self.call_stack.append(Frame(main_closure, 0, 0))


    def run(self, debug=False):
        try:
            while self.current_frame().ip < len(self.current_chunk()):
                if debug and self.read_op_for_debug() == Opcode.DBG:
                    self.debugger()

                opcode = self.read_op()
                
                if opcode == Opcode.HALT: break
                elif opcode == Opcode.PUSH: self.stack.append(self.read_operand())
                
                elif opcode in (Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV, Opcode.MOD,
                                Opcode.EQ, Opcode.NEQ, Opcode.LT, Opcode.GT, Opcode.LTE, Opcode.GTE,
                                Opcode.AND, Opcode.OR):
                    b, a = self.stack.pop(), self.stack.pop()
                    if opcode == Opcode.ADD:
                        if isinstance(a, list): self.stack.append(a + (b if isinstance(b, list) else [b]))
                        elif isinstance(a, str): self.stack.append(a + str(b))
                        elif isinstance(a, (int, float)) and isinstance(b, (int, float)): self.stack.append(a + b)
                        else: raise TypeError(f"Unsupported operand types for +: '{type(a).__name__}' and '{type(b).__name__}'")
                    elif opcode == Opcode.SUB: self.stack.append(a - b)
                    elif opcode == Opcode.MUL: self.stack.append(a * b)
                    elif opcode == Opcode.DIV: self.stack.append(a / b if isinstance(a, float) or isinstance(b, float) else a // b)
                    elif opcode == Opcode.MOD: self.stack.append(a % b)
                    elif opcode == Opcode.EQ: self.stack.append(int(a == b))
                    elif opcode == Opcode.NEQ: self.stack.append(int(a != b))
                    elif opcode == Opcode.LT: self.stack.append(int(a < b))
                    elif opcode == Opcode.GT: self.stack.append(int(a > b))
                    elif opcode == Opcode.LTE: self.stack.append(int(a <= b))
                    elif opcode == Opcode.GTE: self.stack.append(int(a >= b))
                    elif opcode == Opcode.AND: self.stack.append(int(a and b))
                    elif opcode == Opcode.OR: self.stack.append(int(a or b))
                
                elif opcode == Opcode.NOT: self.stack.append(int(not self.stack.pop()))
                
                elif opcode == Opcode.DUP: self.stack.append(self.stack[-1])
                elif opcode == Opcode.SWAP: self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]
                elif opcode == Opcode.DROP: self.stack.pop()
                elif opcode == Opcode.ROT: self.stack[-3], self.stack[-2], self.stack[-1] = self.stack[-1], self.stack[-3], self.stack[-2]
                
                elif opcode == Opcode.STORE_NAME:
                    name = self.read_operand()
                    if self.current_frame().closure.name == '__main__':
                        self.globals[name] = self.stack.pop()
                    else:
                        self.current_frame().locals[name] = self.stack.pop()
                
                elif opcode == Opcode.LOAD_NAME:
                    name = self.read_operand()
                    if name in self.current_frame().locals:
                        self.stack.append(self.current_frame().locals[name])
                    elif name in self.globals:
                        self.stack.append(self.globals[name])
                    else:
                        raise NameError(f"name '{name}' is not defined")
                
                elif opcode == Opcode.JUMP: self.current_frame().ip = self.read_operand()
                elif opcode == Opcode.JUMP_IF_FALSE:
                    addr = self.read_operand()
                    if not self.stack.pop(): self.current_frame().ip = addr

                elif opcode == Opcode.BUILD_CLOSURE:
                    func_name = self.read_operand()
                    params, chunk = self.chunks[func_name]
                    self.stack.append(Closure(func_name, params, chunk))

                elif opcode == Opcode.CALL:
                    callee = self.stack.pop()
                    if not isinstance(callee, Closure): raise TypeError(f"Object {callee} is not callable.")
                    
                    frame = Frame(callee, 0, len(self.stack) - len(callee.params))
                    for param_name in reversed(callee.params):
                        if not self.stack: raise IndexError(f"Not enough arguments for function '{callee.name}'")
                        frame.locals[param_name] = self.stack.pop()
                    
                    self.call_stack.append(frame)

                elif opcode == Opcode.RETURN:
                    return_val = self.stack.pop()
                    frame_to_pop = self.call_stack.pop()
                    if not self.call_stack: break
                    self.stack = self.stack[:frame_to_pop.stack_start]
                    self.stack.append(return_val)
                    
                elif opcode == Opcode.BUILD_LIST:
                    num_items = self.read_operand()
                    self.stack.append([self.stack.pop() for _ in range(num_items)][::-1])
                elif opcode == Opcode.BUILD_MAP:
                    num_pairs = self.read_operand()
                    new_map = {}
                    for _ in range(num_pairs):
                        val, key = self.stack.pop(), self.stack.pop()
                        new_map[key].append(val)
                    self.stack.append(new_map)
                elif opcode == Opcode.GET_ITEM: key, obj = self.stack.pop(), self.stack.pop(); self.stack.append(obj[key])
                elif opcode == Opcode.SET_ITEM: val, key, obj = self.stack.pop(), self.stack.pop(); obj[key] = val; self.stack.append(obj)
                elif opcode == Opcode.LEN: self.stack.append(len(self.stack.pop()))

                elif opcode == Opcode.PRINT:
                    print(self.stack.pop(), end="", flush=True)
                
                elif opcode == Opcode.INPUT: self.stack.append(sys.stdin.readline().strip())
                elif opcode == Opcode.FFI_CALL: self.ffi_call()
                elif opcode == Opcode.DBG: pass
        
        except (IndexError, KeyError, TypeError, NameError, ZeroDivisionError, FileNotFoundError) as e:
            self.generate_error_report(e)

    def read_op(self):
        op = self.current_chunk()[self.current_frame().ip]
        self.current_frame().ip += 1
        return op

    def read_op_for_debug(self):
        return self.current_chunk()[self.current_frame().ip]

    def read_operand(self):
        return self.read_op()

    def current_frame(self):
        return self.call_stack[-1]

    def current_chunk(self):
        return self.current_frame().closure.chunk

    def ffi_call(self):
        func_name, lib_path = self.stack.pop(), self.stack.pop()
        if lib_path not in self.ffi_libs:
            self.ffi_libs[lib_path] = ctypes.CDLL(lib_path)
        
        lib = self.ffi_libs[lib_path]
        c_func = getattr(lib, func_name)
        
        num_args = self.stack.pop()
        args = [self.stack.pop() for _ in range(num_args)]
        
        c_func.argtypes = [ctypes.c_double if isinstance(a, float) else ctypes.c_int for a in args]
        c_func.restype = ctypes.c_double
        
        self.stack.append(c_func(*args))

    def generate_error_report(self, e: Exception):
        frame = self.current_frame()
        if frame.closure.name not in self.debug_maps or not self.debug_maps[frame.closure.name]:
            line, col = -1, -1
        else:
            debug_map = self.debug_maps[frame.closure.name]
            ip_for_debug = frame.ip - 1
            if 0 <= ip_for_debug < len(debug_map):
                line, col = debug_map[ip_for_debug]
            else:
                line, col = -2, -2
        
        print("\n--- Sym Runtime Error ---", file=sys.stderr)
        print(f"  Error: {type(e).__name__}: {e}", file=sys.stderr)
        print(f"  Location: function '{frame.closure.name}', line {line}, column {col}", file=sys.stderr)
        print("\n--- Call Stack Trace ---", file=sys.stderr)
        for f in self.call_stack:
            print(f"  - in function '{f.closure.name}'", file=sys.stderr)

    def debugger(self):
        frame = self.current_frame()
        debug_map = self.debug_maps[frame.closure.name]
        ip = frame.ip - 1
        line, col = debug_map[ip]
        print(f"--- Breakpoint @ function '{frame.closure.name}', line {line} ---")
        
        cmd = ""
        while cmd not in ["c", "continue"]:
            cmd = input("(dbg) ")
            if cmd in ["s", "stack"]: print("Stack:", self.stack)
            elif cmd in ["l", "locals"]: print("Locals:", frame.locals)
            elif cmd in ["g", "globals"]: print("Globals:", self.globals)
            elif cmd in ["n", "next"]: break