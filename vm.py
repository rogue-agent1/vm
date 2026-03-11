#!/usr/bin/env python3
"""vm — Stack-based virtual machine with bytecode. Zero deps."""

PUSH, POP, ADD, SUB, MUL, DIV, MOD = range(7)
DUP, SWAP, OVER = range(7, 10)
EQ, LT, GT, NOT, AND, OR = range(10, 16)
JMP, JZ, JNZ = range(16, 19)
CALL, RET, HALT, PRINT, READ = range(19, 24)

NAMES = {PUSH:'PUSH',POP:'POP',ADD:'ADD',SUB:'SUB',MUL:'MUL',DIV:'DIV',MOD:'MOD',
         DUP:'DUP',SWAP:'SWAP',OVER:'OVER',EQ:'EQ',LT:'LT',GT:'GT',NOT:'NOT',
         AND:'AND',OR:'OR',JMP:'JMP',JZ:'JZ',JNZ:'JNZ',CALL:'CALL',RET:'RET',
         HALT:'HALT',PRINT:'PRINT',READ:'READ'}

class VM:
    def __init__(self, code, debug=False):
        self.code = code
        self.stack = []
        self.call_stack = []
        self.ip = 0
        self.debug = debug

    def run(self):
        while self.ip < len(self.code):
            op = self.code[self.ip]
            if self.debug:
                print(f"  [{self.ip:03d}] {NAMES.get(op,'?'):6s} stack={self.stack[:8]}")
            self.ip += 1
            if op == PUSH: self.stack.append(self.code[self.ip]); self.ip += 1
            elif op == POP: self.stack.pop()
            elif op == ADD: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a + b)
            elif op == SUB: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a - b)
            elif op == MUL: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a * b)
            elif op == DIV: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a // b)
            elif op == MOD: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a % b)
            elif op == DUP: self.stack.append(self.stack[-1])
            elif op == SWAP: self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]
            elif op == OVER: self.stack.append(self.stack[-2])
            elif op == EQ: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(int(a == b))
            elif op == LT: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(int(a < b))
            elif op == GT: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(int(a > b))
            elif op == NOT: self.stack.append(int(not self.stack.pop()))
            elif op == AND: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(int(a and b))
            elif op == OR: b, a = self.stack.pop(), self.stack.pop(); self.stack.append(int(a or b))
            elif op == JMP: self.ip = self.code[self.ip]
            elif op == JZ:
                addr = self.code[self.ip]; self.ip += 1
                if not self.stack.pop(): self.ip = addr
            elif op == JNZ:
                addr = self.code[self.ip]; self.ip += 1
                if self.stack.pop(): self.ip = addr
            elif op == CALL:
                self.call_stack.append(self.ip + 1)
                self.ip = self.code[self.ip]
            elif op == RET: self.ip = self.call_stack.pop()
            elif op == HALT: return self.stack[-1] if self.stack else None
            elif op == PRINT: print(f"  OUT: {self.stack[-1]}")
        return self.stack[-1] if self.stack else None

def main():
    # Fibonacci(10)
    fib = [
        PUSH, 10,    # n
        PUSH, 0,     # a
        PUSH, 1,     # b
        # loop at ip=6:
        OVER,        # [n, a, b, a]
        ADD,         # [n, a, a+b]
        SWAP,        # [n, a+b, a]
        POP,         # [n, a+b]
        SWAP,        # [a+b, n]
        PUSH, 1, SUB,# [a+b, n-1]
        DUP,         # [a+b, n-1, n-1]
        PUSH, 0, GT, # [a+b, n-1, n-1>0]
        JNZ, 6,      # if n>0 goto 6
        POP,         # [result]
        PRINT,
        HALT
    ]
    print("Fibonacci(10):")
    VM(fib).run()

    # Factorial(7)
    fact = [
        PUSH, 7, PUSH, 1,   # n=7, acc=1
        # loop at ip=4:
        SWAP, DUP, PUSH, 0, GT,  # acc, n, n>0
        JZ, 18,              # if n==0 goto end
        DUP, PUSH, 1, SUB,  # n, n-1
        SWAP, OVER,          # n-1, n, n-1... no
    ]
    # Simpler factorial
    fact2 = [PUSH, 1]  # acc
    for i in range(2, 8):
        fact2 += [PUSH, i, MUL]
    fact2 += [PRINT, HALT]
    print("\nFactorial(7):")
    VM(fact2).run()

if __name__ == "__main__":
    main()
