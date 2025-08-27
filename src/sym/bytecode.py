# src/sym/bytecode.py
from enum import IntEnum, auto

class Opcode(IntEnum):
    # Stack and Constants
    PUSH = auto(); DUP = auto(); SWAP = auto(); DROP = auto(); ROT = auto()
    
    # Math and Logic
    ADD = auto(); SUB = auto(); MUL = auto(); DIV = auto(); MOD = auto()
    EQ = auto(); NEQ = auto(); LT = auto(); GT = auto(); LTE = auto(); GTE = auto()
    AND = auto(); OR = auto(); NOT = auto()
    
    # Variables
    STORE_NAME = auto(); LOAD_NAME = auto()
    
    # Control Flow
    JUMP = auto(); JUMP_IF_FALSE = auto()
    
    # Functions
    CALL = auto(); RETURN = auto(); BUILD_CLOSURE = auto()
    
    # Data Structures
    BUILD_LIST = auto(); BUILD_MAP = auto()
    GET_ITEM = auto(); SET_ITEM = auto(); LEN = auto()
    
    # I/O, Debug, and System
    PRINT = auto(); INPUT = auto()
    FFI_CALL = auto(); DBG = auto(); HALT = auto()