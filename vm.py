#!/usr/bin/env python3
"""Stack-based virtual machine."""
import sys
PUSH,POP,ADD,SUB,MUL,DIV,DUP,SWAP,PRINT,HALT=range(10)
JMP,JZ,JNZ,CMP,CALL,RET,LOAD,STORE=range(10,18)
names={v:k for k,v in locals().items() if isinstance(v,int) and v<18}
def run(program):
    stack,mem,pc,callstack=[],[0]*256,0,[]
    while pc<len(program):
        op=program[pc]; pc+=1
        if op==PUSH: stack.append(program[pc]); pc+=1
        elif op==POP: stack.pop()
        elif op==ADD: b,a=stack.pop(),stack.pop(); stack.append(a+b)
        elif op==SUB: b,a=stack.pop(),stack.pop(); stack.append(a-b)
        elif op==MUL: b,a=stack.pop(),stack.pop(); stack.append(a*b)
        elif op==DIV: b,a=stack.pop(),stack.pop(); stack.append(a//b)
        elif op==DUP: stack.append(stack[-1])
        elif op==SWAP: stack[-1],stack[-2]=stack[-2],stack[-1]
        elif op==PRINT: print(stack.pop())
        elif op==JMP: pc=program[pc]
        elif op==JZ: pc=program[pc] if stack.pop()==0 else pc+1
        elif op==JNZ: pc=program[pc] if stack.pop()!=0 else pc+1
        elif op==CALL: callstack.append(pc+1); pc=program[pc]
        elif op==RET: pc=callstack.pop()
        elif op==LOAD: stack.append(mem[program[pc]]); pc+=1
        elif op==STORE: mem[program[pc]]=stack.pop(); pc+=1
        elif op==HALT: break
    return stack
# Demo: compute 10! iteratively
prog=[PUSH,1,PUSH,10,DUP,PUSH,0,CMP,JZ,22,SWAP,DUP,PUSH,2,SUB,SWAP,MUL,SWAP,PUSH,1,SUB,JMP,4,SWAP,POP,PRINT,HALT]
# Simpler demo: 3+4*2
prog=[PUSH,3,PUSH,4,PUSH,2,MUL,ADD,PRINT,HALT]
print("Program: PUSH 3, PUSH 4, PUSH 2, MUL, ADD, PRINT")
run(prog)
