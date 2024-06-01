from typing import Any, Self
from Token import Token

class Environment:
    def __init__(self, enclosing: Self | None = None) -> None:
        self.values: dict = dict()
        self.enclosing: Environment | None = enclosing

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def ancestor(self, distance: int) -> Self:
        environment: Environment = self

        for i in range(distance):
            if environment.enclosing is None:
                raise Exception(f"Incorrect distance reached {i} in enclosing environments")
            environment = environment.enclosing

        return environment

    def getAt(self, distance: int, name: str) -> None:
        return self.ancestor(distance).values[name]

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values.keys():
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self.values.keys():
            self.values[name.lexeme] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assignAt(self, distance: int, name: Token, value: Any) -> None:
        self.ancestor(distance).values[name.lexeme] = value
