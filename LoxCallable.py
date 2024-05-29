from abc import ABC, abstractmethod
from Interpreter import Interpreter
from Return import ReturnException
from Environment import Environment
from Stmt import Function
from typing import Any
from time import time

class LoxCallable(ABC):
    @abstractmethod
    def call(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        ...

    @abstractmethod
    def arity(self) -> int:
        ...

    @abstractmethod
    def __str__(self) -> str:
        ...

class Clock(LoxCallable):
    def call(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        return time()

    def arity(self) -> int:
        return 0

    def __str__(self) -> str:
        return "<fn native clock>"

class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function, 
                 closure: Environment) -> None:
        self.declaration: Function = declaration
        self.closure: Environment = closure
    
    def call(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        environment: Environment = Environment(self.closure)

        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])

        try:
            interpreter.executeBlock(self.declaration.body, environment)
        except ReturnException as returnValue:
            return returnValue.value

    def arity(self) -> int:
        return len(self.declaration.params)

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"
