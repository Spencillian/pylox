from Interpreter import Interpreter
from Stmt import *
from Expr import *
from enum import Enum, auto

class FunType(Enum):
    NONE = auto()
    FUNCTION = auto()

class Resolver:
    def __init__(self, interpreter: Interpreter) -> None:
        self.interpreter: Interpreter = interpreter
        self.scopes: list[dict[str, bool]] = []
        self.currentFunction: FunType = FunType.NONE

    def resolve(self, code: list[Stmt] | Stmt | Expr) -> None:
        match code:
            case list():
                for statement in code:
                    self.resolveStmt(statement)
            case Stmt():
                self.resolveStmt(code)
            case Expr():
                self.resolveExpr(code)

    def beginScope(self) -> None:
        self.scopes.append(dict())

    def endScope(self) -> None:
        self.scopes.pop()

    def declare(self, name: Token) -> None:
        if len(self.scopes) == 0:
            return

        scope: dict[str, bool] = self.scopes[-1]
        if name.lexeme in scope.keys():
            import Lox
            Lox.parse_error(name,
                            "Already a variable with this name in scope.")
        scope[name.lexeme] = False

    def define(self, name: Token) -> None:
        if len(self.scopes) == 0:
            return

        scope: dict[str, bool] = self.scopes[-1]
        scope[name.lexeme] = True

    def resolveStmt(self, stmt: Stmt):
        match stmt:
            case Var():
                self.visitVarStmt(stmt)
            case Function():
                self.visitFunctionStmt(stmt)
            case Expression():
                self.visitExpressionStmt(stmt)
            case If():
                self.visitIfStmt(stmt)
            case Print():
                self.visitPrintStmt(stmt)
            case Return():
                self.visitReturnStmt(stmt)
            case While():
                self.visitWhileStmt(stmt)
            case Block():
                self.visitBlockStmt(stmt)
            case _:
                print(f"Could not resolve stmt of type: {type(stmt)}")

    def resolveExpr(self, expr: Expr):
        match expr:
            case Variable():
                self.visitVariableExpr(expr)
            case Assign():
                self.visitAssignStmt(expr)
            case Binary():
                self.visitBinaryExpr(expr)
            case Call():
                self.visitCallExpr(expr)
            case Group():
                self.visitGroupExpr(expr)
            case Literal():
                ...
            case Logical():
                self.visitLogicalExpr(expr)
            case Unary():
                self.visitUnaryExpr(expr)
            case _:
                print(f"Could not resolve expr of type: {type(expr)}")

    def resolveLocal(self, expr: Expr, name: Token) -> None:
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i].keys():
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return

    def resolveFunction(self, function: Function, 
                        fun_type: FunType) -> None:
        enclosingFunction: FunType = self.currentFunction
        self.currentFunction = fun_type

        self.beginScope()

        for param in function.params:
            self.declare(param)
            self.define(param)

        self.resolve(function.body)
        self.endScope()

        self.currentFunction = enclosingFunction

    def visitFunctionStmt(self, stmt: Function) -> None:
        self.declare(stmt.name)
        self.define(stmt.name)

        self.resolveFunction(stmt, FunType.FUNCTION)

    def visitAssignStmt(self, expr: Assign) -> None:
        self.resolve(expr.value)
        self.resolveLocal(expr, expr.name)

    def visitVarStmt(self, stmt: Var) -> None:
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)

    def visitBlockStmt(self, stmt: Block) -> None:
        self.beginScope()
        self.resolve(stmt.statements)
        self.endScope()

    def visitWhileStmt(self, stmt: While) -> None:
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    def visitReturnStmt(self, stmt: Return) -> None:
        if self.currentFunction == FunType.NONE:
            import Lox
            Lox.parse_error(stmt.keyword, "Can't return from top-level code")

        if stmt.value is not None:
            self.resolve(stmt.value)

    def visitPrintStmt(self, stmt: Print) -> None:
        self.resolve(stmt.expression)

    def visitIfStmt(self, stmt: If) -> None:
        self.resolve(stmt.condition)
        self.resolve(stmt.thenBranch)
        if stmt.elseBranch is not None:
            self.resolve(stmt.elseBranch)

    def visitUnaryExpr(self, expr: Unary) -> None:
        self.resolve(expr.right)

    def visitLogicalExpr(self, expr: Logical) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visitExpressionStmt(self, stmt: Expression) -> None:
        self.resolve(stmt.expression)

    def visitGroupExpr(self, expr: Group) -> None:
        self.resolve(expr.expression)

    def visitCallExpr(self, expr: Call) -> None:
        self.resolve(expr.callee)

        for argument in expr.arguments:
            self.resolve(argument)

    def visitBinaryExpr(self, expr: Binary) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visitVariableExpr(self, expr: Variable) -> None:
        if (len(self.scopes) != 0
                and expr.name.lexeme in self.scopes[-1].keys()
                and self.scopes[-1][expr.name.lexeme] == False):
            import Lox
            Lox.parse_error(expr.name, "Can't read local variable in its own initializer")

        self.resolveLocal(expr, expr.name)
