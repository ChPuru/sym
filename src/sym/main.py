# src/sym/main.py
import argparse
from pathlib import Path
import sys # <-- ADDED THIS LINE
from sym.parser import parse_file
from sym.compiler import Compiler
from sym.vm import VirtualMachine

def main():
    parser = argparse.ArgumentParser(description="Sym Language Engine")
    parser.add_argument("file", help="Sym source file to execute")
    parser.add_argument("--debug", action="store_true", help="Enable the interactive debugger")
    args = parser.parse_args()

    main_file = Path(args.file)
    if not main_file.exists():
        print(f"Error: File not found: {main_file}")
        return

    try:
        # 1. Parse main file and all imports into a single, combined AST
        ast = parse_file(main_file, set())
        
        # 2. Compile the combined AST to bytecode chunks and debug maps
        compiler = Compiler()
        chunks, debug_maps = compiler.compile(ast)
        
        # 3. Execute on the VM
        vm = VirtualMachine(chunks, debug_maps)
        vm.run(debug=args.debug)
        print() # Final newline

    except (FileNotFoundError, NotImplementedError, TypeError) as e:
        print(f"An error occurred during setup: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected Python-level error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()