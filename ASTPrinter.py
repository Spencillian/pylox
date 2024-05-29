from Expr import *
from TokenType import *
from Token import *

'''
In The Interpreter Book the author uses the Visitor Pattern in order to
get around the `expression problem`. Due to the limitations of Python
classes and the lack of interfaces in python, the Visitor Pattern is
a real pain to implement in fully typed Python. I have elected to solve
the `expression problem` here with the use of Python 3.10's match case
syntax. The match case syntax itself originates from functional languages
and Python recognizes and adopts it as one of its many good ideas. I
hope this allows my code to be more pythonic to all those who would
chance upon it.
'''

def paranthesize(name: str, *exprs: Expr) -> str:
    out: str = '('
    out += name

    for expr in exprs:
        out += ' '
        match expr:
            case Binary():
                out += paranthesize(expr.operator.lexeme, expr.left, expr.right)
            case Unary():
                out += paranthesize(expr.operator.lexeme, expr.right)
            case Group():
                out += paranthesize("group", expr.expression)
            case Literal():
                if expr.value is None:
                    out += 'nil'
                else:
                    out += str(expr.value)
            case _:
                print('ERROR: UNKNOWN TOKEN')

    out += ')'
    return out

if __name__ == '__main__':
    expression: Expr = Binary(
            Unary(
                Token(TokenType.MINUS, '-', None, 1),
                Literal(123)),
            Token(TokenType.STAR, '*', None, 1),
            Group(
                Literal(45.67)))

    print(paranthesize('root', expression))

