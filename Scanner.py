from TokenType import *
from Token import Token
from typing import Any

class Scanner:
    keywords = {
        'and': TokenType.AND,
        'class': TokenType.CLASS,
        'else': TokenType.ELSE,
        'false': TokenType.FALSE,
        'for': TokenType.FOR,
        'fun': TokenType.FUN,
        'if': TokenType.IF,
        'nil': TokenType.NIL,
        'or': TokenType.OR,
        'print': TokenType.PRINT,
        'return': TokenType.RETURN,
        'super': TokenType.SUPER,
        'this': TokenType.THIS,
        'true': TokenType.TRUE,
        'var': TokenType.VAR,
        'while': TokenType.WHILE
    }

    @staticmethod
    def keywordToTokenType(key: str) -> TokenType:
        try:
            return Scanner.keywords[key]
        except KeyError:
            return TokenType.IDENTIFIER

    def __init__(self, source: str) -> None:
        self.source: str = source
        self.start: int = 0
        self.current: int = 0
        self.line: int = 1
        self.tokens: list[Token] = []
    
    def scanTokens(self) -> list[Token]:
        while not self.isAtEnd():
            self.start = self.current
            self.scanToken()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def isAtEnd(self) -> bool:
        return self.current >= len(self.source)

    def scanToken(self) -> None:
        c = self.advance()

        match c:
            case '(':
                self.addToken(TokenType.LEFT_PAREN)
            case ')':
                self.addToken(TokenType.RIGHT_PAREN)
            case '{':
                self.addToken(TokenType.LEFT_BRACE)
            case '}':
                self.addToken(TokenType.RIGHT_BRACE)
            case ',':
                self.addToken(TokenType.COMMA)
            case '.':
                self.addToken(TokenType.DOT)
            case '-':
                self.addToken(TokenType.MINUS)
            case '+':
                self.addToken(TokenType.PLUS)
            case ';':
                self.addToken(TokenType.SEMICOLON)
            case '*':
                self.addToken(TokenType.STAR)
            case '!':
                self.addToken(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
            case '=':
                self.addToken(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
            case '<':
                self.addToken(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
            case '>':
                self.addToken(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER_EQUAL)
            case '/':
                if self.match('/'):
                    while self.peek() != '\n' and not self.isAtEnd():
                        self.advance()
                else:
                    self.addToken(TokenType.SLASH)
            case '"':
                self.string()
            case ' ':
                ...
            case '\r':
                ...
            case '\t':
                ...
            case '\n':
                self.line += 1
            case c if self.isDigit(c):
                self.number()
            case c if self.isAlpha(c):
                self.identifier()
            case _:
                import Lox
                Lox.error(self.line, f"Unexpected character: {c}")

    def identifier(self) -> None:
        while self.isAlphaNumeric(self.peek()):
            self.advance()

        text = self.source[self.start:self.current]
        token = Scanner.keywordToTokenType(text)

        self.addToken(token)

    def string(self):
        while self.peek() != '"' and not self.isAtEnd():
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self.isAtEnd():
            import Lox
            Lox.error(self.line, "Unterminated string.");

        self.advance()

        value = self.source[self.start + 1:self.current - 1]
        self.addToken(TokenType.STRING, value)

    def number(self) -> None:
        while self.isDigit(self.peek()):
            self.advance()
        
        if self.peek() == '.' and self.isDigit(self.peekNext()):
            self.advance()

            while self.isDigit(self.peek()):
                self.advance()
        
        self.addToken(TokenType.NUMBER, float(self.source[self.start:self.current]))
    
    def peekNext(self) -> str:
        if self.current + 1 >= len(self.source):
            return str('\x00')
        return self.source[self.current + 1]

    def peek(self) -> str:
        if self.isAtEnd():
            return str('\x00')  # turn Literal[nullbyte] into string
        return self.source[self.current]
    
    def isAlpha(self, c: str) -> bool:
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or (c == '=')

    def isDigit(self, c: str) -> bool:
        return c >= '0' and c <= '9'

    def isAlphaNumeric(self, c: str) -> bool:
        return self.isDigit(c) or self.isAlpha(c)

    def advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]
    
    def addToken(self, token_type: TokenType, literal: Any = None) -> None:
        text = self.source[self.start: self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def match(self, expected: str) -> bool:
        if self.isAtEnd():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True
    

