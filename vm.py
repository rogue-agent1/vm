#!/usr/bin/env python3
"""vm - Stack-based virtual machine with bytecode assembler and disassembler."""

import sys, struct, json

# Opcodes
PUSH, POP, DUP, SWAP, ADD, SUB, MUL, DIV, MOD = range(9)
EQ, LT, GT, NOT, AND, OR = range(9, 15)
JMP, JZ, JNZ, CALL, RET = range(15, 20)
LOAD, STORE, PRINT, HALT, NOP = range(20, 25)
READ, OVER, ROT = range(25, 28)

OP_NAMES = {
    PUSH:'PUSH', POP:'POP', DUP:'DUP', SWAP:'SWAP',
    ADD:'ADD', SUB:'SUB', MUL:'MUL', DIV:'DIV', MOD:'MOD',
    EQ:'EQ', LT:'LT', GT:'GT', NOT:'NOT', AND:'AND', OR:'OR',
    JMP:'JMP', JZ:'JZ', JNZ:'JNZ', CALL:'CALL', RET:'RET',
    LOAD:'LOAD', STORE:'STORE', PRINT:'PRINT', HALT:'HALT', NOP:'NOP',
    READ:'READ', OVER:'OVER', ROT:'ROT',
}
NAME_OPS = {v.lower(): k for k, v in OP_NAMES.items()}
HAS_ARG = {PUSH, JMP, JZ, JNZ, CALL, LOAD, STORE}

class VM:
    def __init__(self, code, mem_size=256):
        self.code = code
        self.stack = []
        self.callstack = []
        self.memory = [0] * mem_size
        self.ip = 0
        self.output = []
        self.steps = 0

    def run(self, max_steps=100000, trace=False):
        while self.ip < len(self.code) and self.steps < max_steps:
            op = self.code[self.ip]
            arg = self.code[self.ip + 1] if op in HAS_ARG and self.ip + 1 < len(self.code) else None
            if trace:
                name = OP_NAMES.get(op, '???')
                astr = f" {arg}" if arg is not None else ""
                print(f"  [{self.ip:04d}] {name}{astr:10s} stack={self.stack[-5:]}")
            self.ip += 2 if op in HAS_ARG else 1
            self.steps += 1

            if op == PUSH: self.stack.append(arg)
            elif op == POP: self.stack.pop()
            elif op == DUP: self.stack.append(self.stack[-1])
            elif op == SWAP: self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]
            elif op == OVER: self.stack.append(self.stack[-2])
            elif op == ROT: a = self.stack.pop(-3); self.stack.append(a)
            elif op == ADD: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a + b)
            elif op == SUB: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a - b)
            elif op == MUL: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a * b)
            elif op == DIV: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a // b)
            elif op == MOD: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a % b)
            elif op == EQ: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(1 if a == b else 0)
            elif op == LT: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(1 if a < b else 0)
            elif op == GT: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(1 if a > b else 0)
            elif op == NOT: self.stack.append(0 if self.stack.pop() else 1)
            elif op == AND: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a & b)
            elif op == OR: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a | b)
            elif op == JMP: self.ip = arg
            elif op == JZ:
                if self.stack.pop() == 0: self.ip = arg
            elif op == JNZ:
                if self.stack.pop() != 0: self.ip = arg
            elif op == CALL: self.callstack.append(self.ip); self.ip = arg
            elif op == RET: self.ip = self.callstack.pop()
            elif op == LOAD: self.stack.append(self.memory[arg])
            elif op == STORE: self.memory[arg] = self.stack.pop()
            elif op == READ: addr = self.stack.pop(); self.stack.append(self.memory[addr])
            elif op == PRINT: self.output.append(str(self.stack.pop()))
            elif op == HALT: break
            elif op == NOP: pass

        return self.output, self.steps

def assemble(source):
    """Assemble text to bytecode."""
    labels = {}
    tokens = []
    # first pass: collect labels
    pos = 0
    for line in source.split('\n'):
        line = line.split(';')[0].strip()
        if not line: continue
        if line.endswith(':'):
            labels[line[:-1]] = pos
            continue
        parts = line.split()
        op = parts[0].lower()
        if op in NAME_OPS:
            pos += 2 if NAME_OPS[op] in HAS_ARG else 1
            tokens.append(parts)
        else:
            tokens.append(parts)
            pos += 2 if NAME_OPS.get(op) in HAS_ARG else 1
    # second pass
    code = []
    for parts in tokens:
        op = NAME_OPS[parts[0].lower()]
        code.append(op)
        if op in HAS_ARG:
            arg = parts[1] if len(parts) > 1 else '0'
            if arg in labels:
                code.append(labels[arg])
            else:
                code.append(int(arg))
    return code

def disassemble(code):
    lines = []
    i = 0
    while i < len(code):
        op = code[i]
        name = OP_NAMES.get(op, f'???({op})')
        if op in HAS_ARG and i + 1 < len(code):
            lines.append(f"  {i:04d}: {name} {code[i+1]}")
            i += 2
        else:
            lines.append(f"  {i:04d}: {name}")
            i += 1
    return '\n'.join(lines)

def cmd_run(args):
    trace = '-t' in args or '--trace' in args
    path = [a for a in args if not a.startswith('-')][0]
    with open(path) as f: source = f.read()
    code = assemble(source)
    vm = VM(code)
    output, steps = vm.run(trace=trace)
    if output: print(' '.join(output))
    print(f"--- {steps} steps, stack: {vm.stack} ---")

def cmd_asm(args):
    path = args[0]
    with open(path) as f: source = f.read()
    code = assemble(source)
    print(f"Bytecode ({len(code)} values):")
    print(disassemble(code))

def cmd_eval(args):
    source = ' '.join(args)
    # convert simple expression to asm
    lines = []
    for token in source.split():
        if token in ('+', '-', '*', '/', '%'):
            m = {'+': 'add', '-': 'sub', '*': 'mul', '/': 'div', '%': 'mod'}
            lines.append(m[token])
        elif token == '.':
            lines.append('print')
        else:
            lines.append(f"push {token}")
    lines.append('halt')
    code = assemble('\n'.join(lines))
    vm = VM(code)
    output, steps = vm.run()
    if output: print(' '.join(output))
    elif vm.stack: print(vm.stack[-1])

def cmd_demo(args):
    programs = {
        'fibonacci': """
; Fibonacci sequence (first 10 numbers)
push 0
print
push 1
print
push 0
store 0
push 1
store 1
push 8
store 2
loop:
load 0
load 1
add
dup
print
load 1
store 0
store 1
load 2
push 1
sub
dup
store 2
jnz loop
halt
""",
        'factorial': """
; Factorial of 10
push 1
store 0
push 10
store 1
loop:
load 0
load 1
mul
store 0
load 1
push 1
sub
dup
store 1
jnz loop
load 0
print
halt
""",
    }
    name = args[0] if args else 'factorial'
    if name not in programs:
        print(f"Available: {', '.join(programs.keys())}"); return
    source = programs[name]
    print(f"=== {name} ===")
    code = assemble(source)
    vm = VM(code)
    output, steps = vm.run()
    print(f"Output: {' '.join(output)}")
    print(f"Steps: {steps}")

CMDS = {
    'run': (cmd_run, 'FILE [-t] — run assembly file'),
    'asm': (cmd_asm, 'FILE — assemble and show bytecode'),
    'eval': (cmd_eval, 'EXPR — RPN expression (e.g., "3 4 + .")'),
    'demo': (cmd_demo, '[fibonacci|factorial] — run demo program'),
}

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print("Usage: vm <command> [args...]")
        print(f"  Opcodes: {', '.join(sorted(NAME_OPS.keys()))}")
        for n, (_, d) in sorted(CMDS.items()):
            print(f"  {n:6s} {d}")
        sys.exit(0)
    cmd = sys.argv[1]
    if cmd not in CMDS: print(f"Unknown: {cmd}", file=sys.stderr); sys.exit(1)
    CMDS[cmd][0](sys.argv[2:])

if __name__ == '__main__':
    main()
