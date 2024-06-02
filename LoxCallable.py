from __future__ import annotations
from abc import ABC, abstractmethod
from Return import ReturnException
from Environment import Environment
from Stmt import Function
from typing import Any, Self
from time import time
from Token import Token

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Interpreter import Interpreter

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
                 closure: Environment, isInitializer: bool) -> None:
        self.declaration: Function = declaration
        self.closure: Environment = closure
        self.isInitializer: bool = isInitializer

    def call(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        environment: Environment = Environment(self.closure)

        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])

        try:
            interpreter.executeBlock(self.declaration.body, environment)
        except ReturnException as returnValue:
            if self.isInitializer:
                return self.closure.getAt(0, "this")
            return returnValue.value

        if self.isInitializer:
            return self.closure.getAt(0, "this")

    def bind(self, instance: LoxInstance) -> Self:
        environment: Environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, 
                           self.isInitializer)

    def arity(self) -> int:
        return len(self.declaration.params)

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"

class LoxClass(LoxCallable):
    def __init__(self, name: str, methods: dict[str, LoxFunction]) -> None:
        self.name: str = name
        self.methods: dict[str, LoxFunction] = methods

    def call(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        instance: LoxInstance = LoxInstance(self)
        if "init" in self.methods.keys():
            initializer: LoxFunction = self.methods["init"]
            initializer.bind(instance).call(interpreter, arguments)

        return instance

    def arity(self) -> int:
        if "init" in self.methods.keys():
            initializer: LoxFunction = self.methods["init"]
            return initializer.arity()

        return 0

    def __str__(self) -> str:
        return f"<class {self.name}>"


class LoxInstance:
    def __init__(self, loxClass: LoxClass) -> None:
        self.loxClass: LoxClass = loxClass
        self.fields: dict[str, Any] = dict()

    def __str__(self) -> str:
        return f"<class instance {self.loxClass.name}>"

    def getField(self, name: Token) -> Any:
        if name.lexeme in self.fields.keys():
            return self.fields[name.lexeme]

        if name.lexeme in self.loxClass.methods.keys():
            method: LoxFunction = self.loxClass.methods[name.lexeme]
            return method.bind(self)


        raise RuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def setField(self, name: Token, value: Any) -> None:
        self.fields[name.lexeme] = value
