from Expr import Expr, Token
from abc import ABC

class Stmt(ABC):
    ...

class Expression(Stmt):
    def __init__(self, expression: Expr) -> None:
        self.expression: Expr = expression

class Print(Stmt):
    def __init__(self, expression: Expr) -> None:
        self.expression: Expr = expression

class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr | None) -> None:
        self.name: Token = name
        self.initializer: Expr | None = initializer

class Block(Stmt):
    def __init__(self, statements: list[Stmt]) -> None:
        self.statements: list[Stmt] = statements

class If(Stmt):
    def __init__(self, condition: Expr, 
                 thenBranch: Stmt, elseBranch: Stmt | None) -> None:
        self.condition: Expr = condition
        self.thenBranch: Stmt = thenBranch
        self.elseBranch: Stmt | None = elseBranch

class While(Stmt):
    def __init__(self, condition: Expr, body: Stmt) -> None:
        self.condition: Expr = condition
        self.body: Stmt = body

class Function(Stmt):
    def __init__(self, name: Token, 
                 params: list[Token], body: list[Stmt]) -> None:
        self.name: Token = name
        self.params: list[Token] = params
        self.body: list[Stmt] = body

class Return(Stmt):
    def __init__(self, keyword: Token, value: Expr | None) -> None:
        self.keyword: Token = keyword
        self.value: Expr | None = value
