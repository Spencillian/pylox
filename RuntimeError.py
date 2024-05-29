from Token import Token
from TokenType import TokenType

class RuntimeError(Exception):
    def __init__(self, token: Token, message: str) -> None:
        super().__init__(message)
        self.token: Token = token

