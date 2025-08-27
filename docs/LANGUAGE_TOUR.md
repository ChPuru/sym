# A Tour of the Sym Language

Welcome to Sym! This document will guide you through the core concepts of the language.

## 1. The Stack: The Heart of Sym

Everything in Sym happens on a global data stack. Think of it as a stack of plates. You can put new plates on top, or you can take plates off the top.

The `#` operator is used to **push** a literal value onto the stack.

```sym
// This program pushes the number 5, then the number 10.
#5
#10
```

After this program runs, the stack would look like this (bottom to top): [5, 10].

## 2. Arithmetic

Arithmetic operators like `+`, `-`, `*`, and `/` work by popping the top two values from the stack, performing the operation, and pushing the result back.

```sym
#5      // Stack: [5]
#10     // Stack: [5, 10]
+       // Pops 10, then 5. Calculates 5 + 10. Pushes 15.
.       // The '.' operator pops the top value and prints it.
```

**Output:** `15`

## 3. Variables and Scope

You can store the top value from the stack into a named variable.

* `name:` (Store): Pops a value and stores it in `name`.
* `:name` (Load): Pushes the value of `name` onto the stack.

Sym has two scopes:

* **Global:** If you define a variable in the main body of your script, it is global and can be read by any function.
* **Local:** If you define a variable inside a function, it is local to that function call.

```sym
#100 global_var: // This is a global variable

(my_func) {
    #50 local_var: // This is a local variable
    :local_var .    // Prints 50
    :global_var .   // Prints 100
}

&my_func @
```

## 4. Control Flow

Sym supports if/else logic and while loops. They work by popping a value from the stack. If the value is non-zero (true), the block executes.

### If/Else

The `? { ... } ! { ... }` structure provides if/else branching. The `!` (else) block is optional.

```sym
#10 #5 eq ? {
    #"Ten equals five." .
} ! {
    #"Ten does not equal five." .
}
```

**Output:** `Ten does not equal five.`

### While Loops

The `while { <condition> } { <body> }` structure executes the body as long as the condition block leaves a non-zero value on the stack.

```sym
#5 i: // Countdown from 5
while { :i } { // Condition: is i > 0?
    :i .
    :i #1 - i: // Decrement i
}
```

**Output:** `5 4 3 2 1`

## 5. Functions and Closures

Functions are the core of Sym's power.

### Definition and Calling

Functions are defined with `(name params...) { ... }`.

```sym
(add a b) {
    :a :b + // The result is left on the stack
}
```

To call a function, you must first get a reference to it with `&name`, then use the `@` operator to execute it.

```sym
#20 #30 &add @ . // Pushes 20, 30, then the 'add' function, then calls it.
```

**Output:** `50`

### First-Class Functions (Closures)

The `&add` operator creates a **closure**. This is a value that you can store in a variable and pass around, making functions "first-class citizens." This is essential for functional programming.

```sym
&add my_adder: // Store the function in a variable
#70 #80 :my_adder @ . // Load the function from the variable and call it
```

**Output:** `150`

## 6. Data Structures

Sym supports lists and maps.

### Lists

Lists are created with `[...]`. The code inside the brackets is executed to populate the list.

```sym
[ #10 #"hello" #20.5 ] my_list:
:my_list #1 get . // 'get' pops an index, then a list.
```

**Output:** `hello`

### Maps

Maps (dictionaries) are created with `#{ key: value_program, ... }`.

```sym
#{ "name": #"John Doe", "age": #42 } user:
:user #"age" get .
```

**Output:** `42`

## Next Steps

You now know the fundamentals of the Sym language! To see a truly complex and powerful example, check out the Mandelbrot set renderer in **examples/mandelbrot.sym**.

---
