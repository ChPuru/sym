#include <stdio.h>
// A simple function to demonstrate FFI
double add_doubles(double a, double b) {
printf("[c] Received numbers %.2f and %.2f\n", a, b);
return a + b;
}