# Sym Language Roadmap

This document outlines the potential future direction for the Sym programming language. These are ideas for improvement and are not guaranteed to be implemented, but they represent the project's long-term vision.

## Short-Term Goals (Foundations)

- [ ] **Create a Comprehensive Test Suite:** Build a full test suite using `pytest` to formalize the behavior of the VM and standard library, preventing future regressions.
- [ ] **Expand the Standard Library:**
  - Add a `string.sym` module for common string manipulation tasks.
  - Add more list utilities to `list.sym` (e.g., `(sort)`, `(reverse)`).
- [ ] **Improve Documentation:** Write a formal language reference that specifies the behavior of every opcode and operator.

## Mid-Term Goals (Ecosystem & Tooling)

- [ ] **Package Manager (`sympkg`):** Design and build a simple command-line tool to manage Sym project dependencies, allowing for easy sharing and versioning of libraries.
- [ ] **Syntax Highlighting:** Create syntax highlighting extensions for popular editors like VS Code and Sublime Text.
- [ ] **Code Formatter (`symfmt`):** A tool that automatically formats Sym code according to a canonical style guide, ensuring consistency across projects.

## Long-Term Vision (The "Holy Grail" Features)

- [ ] **Self-Hosting Compiler:** The ultimate goal for any serious language. Rewrite the Sym compiler from Python into Sym itself. This would prove the language's power and make it fully self-contained.
- [ ] **Language Server Protocol (LSP):** Implement an LSP for Sym to provide modern editor features like autocompletion, go-to-definition, and real-time error checking.
- [ ] **Concurrency:** Explore adding concurrency primitives to the VM, such as threads or goroutines, to allow for parallel execution.
- [ ] **JIT (Just-In-Time) Compilation:** Investigate replacing the bytecode interpreter loop with a JIT compiler (e.g., using `llvmlite`) for a massive performance boost in computation-heavy tasks.
