from sre_compile import dis
from Expr import *
from LoxCallable import LoxInstance
from Stmt import *
from Environment import Environment
from TokenType import TokenType
from typing import Any
from RuntimeError import RuntimeError
from Return import ReturnException

class Interpreter:
    def __init__(self):
        self.globals: Environment = Environment()
        self.environment: Environment = self.globals
        self.locals: dict[Expr, int] = dict()

        from LoxCallable import Clock
        self.globals.define("clock", Clock())

    def interpret(self, statements: list[Stmt]) -> None:
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeError as error:
            import Lox
            Lox.runtime_error(error)

    def resolve(self, expr: Expr, depth: int) -> None:
        self.locals[expr] = depth

    def execute(self, stmt: Stmt) -> None:
        match stmt:
            case Print():
                self.visitPrintStmt(stmt)
            case Expression():
                self.visitExpressionStmt(stmt)
            case Block():
                self.visitBlockStmt(stmt)
            case Var():
                self.visitVarStmt(stmt)
            case If():
                return self.visitIfStmt(stmt)
            case While():
                return self.visitWhileStmt(stmt)
            case Function():
                return self.visitFunctionStmt(stmt)
            case Return():
                return self.visitReturnStmt(stmt)
            case Class():
                return self.visitClassStmt(stmt)
            case _:
                raise Exception(f"Attempted to execute unmatched stmt type.")

    def evaluate(self, expr: Expr) -> Any:
        match expr:
            case Literal():
                return self.visitLiteralExpr(expr)
            case Group():
                return self.visitGroupExpr(expr)
            case Unary():
                return self.visitUnaryExpr(expr)
            case Binary():
                return self.visitBinaryExpr(expr)
            case Variable():
                return self.visitVariableExpr(expr)
            case Assign():
                return self.visitAssignExpr(expr)
            case Logical():
                return self.visitLogicalExpr(expr)
            case Call():
                return self.visitCallExpr(expr)
            case Get():
                return self.visitGetExpr(expr)
            case Set():
                return self.visitSetExpr(expr)
            case This():
                return self.visitThisExpr(expr)
            case Super():
                return self.visitSuperExpr(expr)
            case _:
                raise Exception(f"Attempted to evaluate unmatched expression type.")

    def stringify(self, object: Any) -> str:
        if object is None:
            return 'nil'
        elif type(object) is float:
            text: str = str(object)
            if len(text) >= 2 and text[-2:] == ".0":
                text = text[:-2]
            return text
        return str(object)

    def executeBlock(self, statements: list[Stmt], environment: Environment) -> None:
        previous: Environment = self.environment

        try:
            self.environment = environment

            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def visitClassStmt(self, stmt: Class) -> None:
        superclass: Any = None
        if stmt.superclass is not None:
            superclass = self.evaluate(stmt.superclass)
            from LoxCallable import LoxClass
            if not (type(superclass) is LoxClass):
                raise RuntimeError(stmt.superclass.name, "Superclass must be a class.")

        self.environment.define(stmt.name.lexeme, None)

        if stmt.superclass is not None:
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass)

        from LoxCallable import LoxFunction
        methods: dict[str, LoxFunction] = dict()
        for method in stmt.methods:
            function: LoxFunction = LoxFunction(
                method, self.environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = function

        from LoxCallable import LoxClass
        loxClass: LoxClass = LoxClass(stmt.name.lexeme, superclass, methods)

        if superclass is not None:
            assert self.environment.enclosing is not None
            self.environment = self.environment.enclosing

        self.environment.assign(stmt.name, loxClass)

    def visitReturnStmt(self, stmt: Return) -> None:
        value: Any = None

        if stmt.value is not None:
            value = self.evaluate(stmt.value)

        raise ReturnException(value)

    def visitFunctionStmt(self, stmt: Function) -> None:
        from LoxCallable import LoxFunction
        function: LoxFunction = LoxFunction(stmt, self.environment, 
                                            False)
        self.environment.define(stmt.name.lexeme, function)

    def visitWhileStmt(self, stmt: While) -> None:
        while self.isTruthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    def visitIfStmt(self, stmt: If) -> None:
        if self.isTruthy(self.evaluate(stmt.condition)):
            self.execute(stmt.thenBranch)
        elif stmt.elseBranch is not None:
            self.execute(stmt.elseBranch)

    def visitBlockStmt(self, stmt: Block) -> None:
        self.executeBlock(stmt.statements, Environment(enclosing=self.environment))

    def visitVarStmt(self, stmt: Var) -> None:
        value: Any = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)

    def visitExpressionStmt(self, stmt: Expression) -> None:
        self.evaluate(stmt.expression)

    def visitPrintStmt(self, stmt: Print) -> None:
        value: Any = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visitSuperExpr(self, expr: Super) -> Any:
        distance: int = self.locals[expr]

        from LoxCallable import LoxClass, LoxInstance, LoxFunction
        superclass: LoxClass = self.environment.getAt(distance, "super")
        thing: LoxInstance = self.environment.getAt(distance - 1, "this")

        method: LoxFunction | None = superclass.findMethod(expr.method.lexeme)

        if method is None:
            raise RuntimeError(expr.method, f"Undefined property '{expr.method.lexeme}'.")

        return method.bind(thing)

    def visitThisExpr(self, expr: This) -> Any:
        return self.lookUpVariable(expr.keyword, expr)

    def visitSetExpr(self, expr: Set) -> Any:
        thing: Any = self.evaluate(expr.thing)

        if not type(thing) is LoxInstance:
            raise RuntimeError(expr.name, "Only instances have fields.")

        value: Any = self.evaluate(expr.value)
        thing.setField(expr.name, value)

    def visitGetExpr(self, expr: Get) -> Any:
        thing: Any = self.evaluate(expr.thing)
        if type(thing) is LoxInstance:
            return thing.getField(expr.name)

        raise RuntimeError(expr.name, "Only instances have properties.")

    def visitCallExpr(self, expr: Call) -> Any:
        callee: Any = self.evaluate(expr.callee)

        arguments: list[Expr] = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        from LoxCallable import LoxCallable
        if not issubclass(type(callee), LoxCallable):
            print(type(callee))
            raise RuntimeError(
                expr.paren, 
                "Can only call functions and classes.")

        function: LoxCallable = callee

        if len(arguments) != function.arity():
            raise RuntimeError(
                expr.paren, 
                f"Expected {function.arity()} arguments but got {len(arguments)}.")

        return function.call(self, arguments)

    def visitLogicalExpr(self, expr: Logical) -> Any:
        left: Any = self.evaluate(expr.left)

        if expr.operator.token_type == TokenType.OR:
            if self.isTruthy(left):
                return left
        else:
            if not self.isTruthy(left):
                return left

        return self.evaluate(expr.right)

    def visitAssignExpr(self, expr: Assign) -> Any:
        value: Any = self.evaluate(expr.value)


        if expr in self.locals.keys():
            distance: int = self.locals[expr]
            return self.environment.assignAt(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)

        return value

    def visitVariableExpr(self, expr: Variable) -> Any:
        return self.lookUpVariable(expr.name, expr)

    def lookUpVariable(self, name: Token, expr: Expr) -> Any:
        if expr in self.locals.keys():
            distance: int = self.locals[expr]
            return self.environment.getAt(distance, name.lexeme)
        else:
            return self.globals.get(name)

    def visitLiteralExpr(self, expr: Literal) -> Any:
        return expr.value

    def visitGroupExpr(self, expr: Group) -> Any:
        return expr.expression

    def visitUnaryExpr(self, expr: Unary) -> Any:
        right: Any = self.evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.MINUS:
                return -float(right)
            case TokenType.BANG:
                return not self.isTruthy(right)

        return None

    def visitBinaryExpr(self, expr: Binary) -> Any:
        left: Any = self.evaluate(expr.left)
        right: Any = self.evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.BANG_EQUAL:
                self.checkNumberOperands(expr.operator, left, right)
                return not self.isEqual(left, right)

            case TokenType.EQUAL_EQUAL:
                self.checkNumberOperands(expr.operator, left, right)
                return self.isEqual(left, right)

            case TokenType.GREATER:
                self.checkNumberOperands(expr.operator, left, right)
                return float(left) > float(right)

            case TokenType.GREATER_EQUAL:
                self.checkNumberOperands(expr.operator, left, right)
                return float(left) >= float(right)

            case TokenType.LESS:
                self.checkNumberOperands(expr.operator, left, right)
                return float(left) < float(right)

            case TokenType.LESS_EQUAL:
                self.checkNumberOperands(expr.operator, left, right)
                return float(left) <= float(right)

            case TokenType.MINUS:
                self.checkNumberOperand(expr.operator, right)
                return float(left) - float(right)

            case TokenType.PLUS:
                if type(left) is float and type(right) is float:
                    return float(left) + float(right)
                elif type(left) is str and type(right) is str:
                    return str(left) + str(right)

                raise RuntimeError(
                    expr.operator,
                    "Operands must both be numbers or strings")

            case TokenType.SLASH:
                self.checkNumberOperands(expr.operator, left, right)
                return float(left) / float(right)

            case TokenType.STAR:
                self.checkNumberOperands(expr.operator, left, right)
                return float(left) * float(right)

    def checkNumberOperand(self, operator: Token, operand: Any) -> None:
        if type(operand) is float:
            return

        raise RuntimeError(operator, "Operand must be a number.")

    def checkNumberOperands(self, operator: Token, left: Any, right: Any) -> None:
        if type(left) is float and type(right) is float:
            return

        raise RuntimeError(operator, "Operands must be numbers.")

    def isEqual(self, left: Any, right: Any) -> bool:
        if left == None and right == None:
            return True
        elif left == None:
            return False
        return left == right

    def isTruthy(self, object: Any) -> bool:
        match object:
            case None:
                return False
            case bool():
                return object
        return True
