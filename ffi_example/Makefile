# Simple Makefile for compiling a shared library

# BYPASS THE PATH: Provide the full, absolute path to the compiler.
CC = C:/mingw64/bin/gcc.exe

# Detect OS to set the correct shared library extension
ifeq ($(OS),Windows_NT)
    EXT = .dll
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Linux)
        EXT = .so
    endif
    ifeq ($(UNAME_S),Darwin)
        EXT = .dylib
    endif
endif

TARGET = libexample$(EXT)

all: $(TARGET)

$(TARGET): libexample.c
	$(CC) -shared -o $(TARGET) -fPIC libexample.c

clean:
	rm -f $(TARGET)