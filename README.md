# Pylox Interpreter
### A Lox interpreter written in Python
Written in accordance with the Crafting Interpreters book.

## Download and Run
1. Install Python 3.12.x
2. ```git clone https://github.com/Spencillian/pylox```
3. ```./Lox.py```

This should drop you into the repl. 

Files can be run by using `./Lox.py <codefile.lox>`

## Examples
### Hello world!
```print "Hello world!";```

### Fibonacci
```
fun fib(n) {
  if (n <= 1) return n;
  return fib(n - 2) + fib(n - 1);
}

for (var i = 0; i < 20; i = i + 1) {
  print fib(i);
}
```

## Features
- Dynamically Typed
- Functions are values
- Classes with OOP Inheritance
- Closures

## Structure
The front end of the interpreter is a hand written tokenizer and recursive descent parser. It also contains a
resolver which can check if variables are being used in the right location at compile time. This information
is packaged into an AST tree of tokens and passed to the backend.

The backend is an AST traverse and eval. It takes the tree and recursively evaluates the leaf nodes until there is nothing left to evaluate.

This is not an incredibly fast way to run this language. The end goal is to use this implementation as a golden model 
to test a faster version written in Zig.

## Grammar
Program
```
program        → declaration* EOF ;
```

Declarations
```
declaration    → classDecl
               | funDecl
               | varDecl
               | statement ;
classDecl      → "class" IDENTIFIER ( "<" IDENTIFIER )?
                 "{" function* "}" ;
funDecl        → "fun" function ;
varDecl        → "var" IDENTIFIER ( "=" expression )? ";" ;
```

Statements
```
statement      → exprStmt
               | forStmt
               | ifStmt
               | printStmt
               | returnStmt
               | whileStmt
               | block ;

exprStmt       → expression ";" ;
forStmt        → "for" "(" ( varDecl | exprStmt | ";" )
                           expression? ";"
                           expression? ")" statement ;
ifStmt         → "if" "(" expression ")" statement
                 ( "else" statement )? ;
printStmt      → "print" expression ";" ;
returnStmt     → "return" expression? ";" ;
whileStmt      → "while" "(" expression ")" statement ;
block          → "{" declaration* "}" ;
```

Expressions
```
expression     → assignment ;

assignment     → ( call "." )? IDENTIFIER "=" assignment
               | logic_or ;

logic_or       → logic_and ( "or" logic_and )* ;
logic_and      → equality ( "and" equality )* ;
equality       → comparison ( ( "!=" | "==" ) comparison )* ;
comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
term           → factor ( ( "-" | "+" ) factor )* ;
factor         → unary ( ( "/" | "*" ) unary )* ;

unary          → ( "!" | "-" ) unary | call ;
call           → primary ( "(" arguments? ")" | "." IDENTIFIER )* ;
primary        → "true" | "false" | "nil" | "this"
               | NUMBER | STRING | IDENTIFIER | "(" expression ")"
               | "super" "." IDENTIFIER ;
```

Functions, Parameters, and Arguments
```
function       → IDENTIFIER "(" parameters? ")" block ;
parameters     → IDENTIFIER ( "," IDENTIFIER )* ;
arguments      → expression ( "," expression )* ;
```

Lexical Grammar
```
NUMBER         → DIGIT+ ( "." DIGIT+ )? ;
STRING         → "\"" <any char except "\"">* "\"" ;
IDENTIFIER     → ALPHA ( ALPHA | DIGIT )* ;
ALPHA          → "a" ... "z" | "A" ... "Z" | "_" ;
DIGIT          → "0" ... "9" ;
```
