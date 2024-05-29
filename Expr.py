from abc import ABC
from Token import Token
from typing import Any

class Expr(ABC):
    ...

class Literal(Expr):
    def __init__(self, value: Any) -> None:
        self.value: Any = value

class Group(Expr):
    def __init__(self, expression: Expr) -> None:
        self.expression: Expr = expression

class Unary(Expr):
    def __init__(self, operator: Token, right: Expr) -> None:
        self.operator: Token = operator
        self.right: Expr = right

class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self.left: Expr = left
        self.operator: Token = operator
        self.right: Expr = right

class Variable(Expr):
    def __init__(self, name: Token) -> None:
        self.name: Token = name

class Assign(Expr):
    def __init__(self, name: Token, value: Expr) -> None:
        self.name: Token = name
        self.value: Expr = value

class Logical(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self.left: Expr = left
        self.operator: Token = operator
        self.right: Expr = right

class Call(Expr):
    def __init__(self, callee: Expr, paren: Token, arguments: list[Expr]) -> None:
        self.callee: Expr = callee
        self.paren: Token = paren
        self.arguments: list[Expr] = arguments
