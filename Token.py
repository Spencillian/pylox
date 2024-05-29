from TokenType import TokenType
from typing import Any

class Token:
    def __init__(self, 
                 token_type: TokenType, 
                 lexeme: str, 
                 literal: Any, 
                 line: int) -> None:
        self.token_type: TokenType = token_type
        self.lexeme: str = lexeme
        self.literal: Any = literal
        self.line: int = line

    def __str__(self) -> str:
        return f"{self.token_type} {self.lexeme} {self.literal}"

