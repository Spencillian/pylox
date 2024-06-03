from Token import *
from Expr import *
from Stmt import *

class Parser:

    class ParseError(Exception):
        def __init__(self, message) -> None:
            super().__init__(message)

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens: list[Token] = tokens
        self.current: int = 0

    def parse(self) -> list[Stmt]:
        statements: list[Stmt] = []

        while not self.isAtEnd():
            statements.append(self.declaration())

        return statements

    def declaration(self) -> Stmt:
        try:
            if self.match(TokenType.CLASS):
                return self.classDeclaration()
            elif self.match(TokenType.FUN):
                return self.function("function")
            elif self.match(TokenType.VAR):
                return self.varDeclaration()
            return self.statement()
        except self.ParseError:
            self.synchronize()
            return Stmt()

    def classDeclaration(self) -> Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER, "Expect class name.")

        superclass: Variable | None = None
        if self.match(TokenType.LESS):
            self.consume(TokenType.IDENTIFIER, "Expected superclass name.")
            superclass = Variable(self.previous())

        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

        methods: list[Function] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.isAtEnd():
            methods.append(self.function("method"))

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")

        return Class(name, superclass, methods)

    def function(self, kind: str) -> Function:
        name: Token = self.consume(
            TokenType.IDENTIFIER, f"Expected {kind} name.")

        self.consume(
            TokenType.LEFT_PAREN, 
            f"Expected '(' after {kind} name.")

        parameters: list[Token] = []

        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(
                self.consume(
                    TokenType.IDENTIFIER,
                    "Expected parameter name."))

            while self.match(TokenType.COMMA):
                if len(parameters) >= 255:
                    self.error(self.peek(), 
                               "Can't have more than 255 parameters.")

                parameters.append(
                    self.consume(
                        TokenType.IDENTIFIER,
                        "Expected parameter name."))

        self.consume(TokenType.RIGHT_PAREN, 
                     "Expected ')' after parameters.")

        self.consume(TokenType.LEFT_BRACE, 
                     f"Expected '{{' before {kind} body.")

        body: list[Stmt] = self.block()
        return Function(name, parameters, body)

    def varDeclaration(self) -> Stmt:
        name: Token = self.consume(
            TokenType.IDENTIFIER, "Expected variable name.")
        initializer: Expr | None = None

        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(
            TokenType.SEMICOLON, 
            "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def statement(self) -> Stmt:
        if self.match(TokenType.FOR):
            return self.forStatement()
        elif self.match(TokenType.IF):
            return self.ifStatement()
        elif self.match(TokenType.RETURN):
            return self.returnStatement()
        elif self.match(TokenType.PRINT):
            return self.printStatement()
        elif self.match(TokenType.WHILE):
            return self.whileStatement()
        elif self.match(TokenType.LEFT_BRACE):
            return Block(self.block())
        return self.expressionStatement()

    def returnStatement(self) -> Stmt:
        keyword: Token = self.previous()
        value: Expr | None = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()

        self.consume(
            TokenType.SEMICOLON, "Expected ';' after return value")
        return Return(keyword, value)

    def forStatement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'for'.")

        initializer: Stmt | None
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.varDeclaration()
        else:
            initializer = self.expressionStatement()

        condition: Expr | None = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()

        self.consume(
            TokenType.SEMICOLON, "Expected ';' after loop condition.")

        increment: Expr | None = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()

        self.consume(
            TokenType.RIGHT_PAREN, "Expected ')' after for clauses.")
        body: Stmt = self.statement()

        if increment is not None:
            body = Block([body, Expression(increment)])

        if condition is None:
            condition = Literal(True)
        body = While(condition, body)

        if initializer is not None:
            body = Block([initializer, body])

        return body

    def whileStatement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'.")
        condition: Expr = self.expression()
        self.consume(
            TokenType.RIGHT_PAREN, "Expected ')' after condition.")
        body: Stmt = self.statement()

        return While(condition, body)

    def ifStatement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'.")
        condition: Expr = self.expression()
        self.consume(
            TokenType.RIGHT_PAREN, "Expected ')' after 'if' condition.")

        thenBranch: Stmt = self.statement()
        elseBranch: Stmt | None = None
        if self.match(TokenType.ELSE):
            elseBranch = self.statement()

        return If(condition, thenBranch, elseBranch)

    def block(self) -> list[Stmt]:
        statements: list[Stmt] = []

        while (not self.check(TokenType.RIGHT_BRACE) 
               and not self.isAtEnd()):
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after block.")
        return statements

    def printStatement(self) -> Stmt:
        value: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after value.")
        return Print(value)

    def expressionStatement(self) -> Stmt:
        expr: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after value.")
        return Expression(expr)

    def expression(self) -> Expr:
        return self.assignment()

    def assignment(self) -> Expr:
        expr: Expr = self.orExpr()

        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: Expr = self.assignment()

            match expr:
                case Variable():
                    name: Token = expr.name
                    return Assign(name, value)
                case Get():
                    get: Get = expr
                    return Set(get.thing, get.name, value)

            import Lox
            Lox.parse_error(equals, "Invalid assignment target.")

        return expr

    def orExpr(self) -> Expr:
        expr: Expr = self.andExpr()

        while self.match(TokenType.OR):
            operator: Token = self.previous()
            right: Expr = self.andExpr()
            expr = Logical(expr, operator, right)

        return expr

    def andExpr(self) -> Expr:
        expr: Expr = self.equality()

        while self.match(TokenType.AND):
            operator: Token = self.previous()
            right: Expr = self.equality()
            expr = Logical(expr, operator, right)

        return expr

    def equality(self) -> Expr:
        expr: Expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self.previous()
            right: Expr = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr:
        expr: Expr = self.term()

        while self.match(TokenType.GREATER,
                         TokenType.GREATER_EQUAL,
                         TokenType.LESS,
                         TokenType.LESS_EQUAL):
            operator: Token = self.previous()
            right: Expr = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self) -> Expr:
        expr: Expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator: Token = self.previous()
            right: Expr = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def factor(self) -> Expr:
        expr: Expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self.previous()
            right: Expr = self.unary()
            expr = Binary(expr, operator, right)

        return expr

    def unary(self) -> Expr:
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self.previous()
            right: Expr = self.unary()
            return Unary(operator, right)

        return self.call()

    def call(self) -> Expr:
        expr: Expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finishCall(expr)
            elif self.match(TokenType.DOT):
                name: Token = self.consume(
                    TokenType.IDENTIFIER, 
                    "Expected property name after '.'.")
                expr = Get(expr, name)
            else:
                break

        return expr

    def finishCall(self, callee: Expr) -> Expr:
        arguments: list[Expr] = []

        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                if len(arguments) >= 255:
                    self.error(self.peek(), 
                               "Can't have more than 255 arguments.")
                arguments.append(self.expression())

        paren: Token = self.consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments.")

        return Call(callee, paren, arguments)

    def primary(self) -> Expr:
        if self.match(TokenType.FALSE):
            return Literal(False)
        elif self.match(TokenType.TRUE):
            return Literal(True)
        elif self.match(TokenType.NIL):
            return Literal(None)
        elif self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
        elif self.match(TokenType.SUPER):
            keyword: Token = self.previous()
            self.consume(TokenType.DOT, "Expected '.' after 'super'.")
            method: Token = self.consume(TokenType.IDENTIFIER, "Expected superclass method name.")
            return Super(keyword, method)
        elif self.match(TokenType.THIS):
            return This(self.previous())
        elif self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        elif self.match(TokenType.LEFT_PAREN):
            expr: Expr = self.expression()
            self.consume(
                TokenType.RIGHT_PAREN, "Expected ')' after expression.")
            return Group(expr)

        raise self.error(self.peek(), "Expected expression.")

    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()

        raise self.error(self.peek(), message)

    def error(self, token: Token, message: str) -> ParseError:
        import Lox
        Lox.parse_error(token, message)

        return self.ParseError(message)

    def synchronize(self) -> None:
        self.advance()

        while not self.isAtEnd():
            if self.previous().token_type == TokenType.SEMICOLON:
                match self.peek().token_type:
                    case TokenType.CLASS:
                        return
                    case TokenType.FUN:
                        return
                    case TokenType.VAR:
                        return
                    case TokenType.FOR:
                        return
                    case TokenType.IF:
                        return
                    case TokenType.WHILE:
                        return
                    case TokenType.PRINT:
                        return
                    case TokenType.RETURN:
                        return
            self.advance()

    def match(self, *token_types: TokenType) -> bool:
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def check(self, token_type: TokenType) -> bool:
        if self.isAtEnd():
            return False
        return self.peek().token_type == token_type

    def advance(self):
        if not self.isAtEnd():
            self.current += 1
        return self.previous()

    def isAtEnd(self) -> bool:
        return self.peek().token_type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]
