#!/usr/bin/env python3.12

import sys
from Scanner import Scanner, TokenType
from Token import Token
from Parser import Parser, Stmt
from RuntimeError import RuntimeError
from Interpreter import Interpreter
from Resolver import Resolver


interpreter = Interpreter()
hadError = False
hadRuntimeError = False
args = sys.argv[1:]

def run(source: str) -> None:
    scanner: Scanner = Scanner(source)
    tokens: list[Token] = scanner.scanTokens()

    parser: Parser = Parser(tokens)
    stmts: list[Stmt] = parser.parse()

    if hadError:
        return

    resolver: Resolver = Resolver(interpreter)
    resolver.resolve(stmts)

    if hadError:
        return

    interpreter.interpret(stmts)

def runFile(path: str) -> None:
    with open(path) as f:
        data = f.read()
        run(data)

    if hadError:
        exit(65)
    if hadRuntimeError:
        exit(70)

def runPrompt() -> None:
    global hadError
    while True:
        try:
            line = input("> ")
        except EOFError:
            exit(0)

        if line == '':
            break
        run(line)

        hadError = False

def error(line: int, message: str) -> None:
    report(line, "", message)

def parse_error(token: Token, message: str) -> None:
    if token.token_type == TokenType.EOF:
        report(token.line, " at end", message)
    else:
        report(token.line, f"at '{token.lexeme}'", message)

def runtime_error(err: RuntimeError) -> None:
    print(f'{err.__str__()}\n[line: {err.token.line}]')
    global hadRuntimeError
    hadRuntimeError = True

def report(line: int, where: str, message: str) -> None:
    print(f"[line {line}] Error {where}: {message}")
    global hadError
    hadError = True

if __name__ == '__main__':
    if len(args) > 1:
        print("Usage: pylox <script>")
        exit(64)
    elif len(args) == 1:
        runFile(args[0])
    else:
        runPrompt()

