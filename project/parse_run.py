from interp_fun import Add, Sub, Mul, Div, Neg, Lit, Let, Name, Or, Not, And,  Eq, Lt, If,ImgComb, RotImag, LetFun, App, Expr, run

from lark import Lark, Token, ParseTree, Transfomer
from lark.exception import VisitError
from pathlib import Path

#giving the parser the path to lark file and where to start
parser = Lark(Path('expr.lark').read_text(),start='expr',ambiguity='explicit')

#error handling from parser allows for easier debug between interp and parser
class ParserError(Exception):
    pass

#parse function
def parse(s:str)->ParseTree:
    try:
        return parser.parse(s)
    except Exception as e:
        raise ParserError(e)

#ambigious parser error
class AmbigiousParse(Exception):
    pass


#class that transform parser tree into an AST
class toExpr(Transfomer[Token,Expr]):
    pass



#generates the AST
def genAst(t:ParseTree)->Expr:
    ''' Applies the transformer to conver a parse tree into a AST'''
    try:
        return toExpr().transform(t)
    except VisitError as e:
        if isinstance(e.orig_exc,AmbigiousParse):
            raise AmbigiousParse()
        else:
            raise e

#runs parser tree
def driver():
    while True:
        try:
            s = input('expr: ')
            t = parse(s)
            print("raw:", t)    
            print("pretty:")
            print(t.pretty())
            ast = genAST(t)
            print("raw AST:", repr(ast))  # use repr() to avoid str() pretty-printing
            run(ast)                      # pretty-prints and executes the AST
        except AmbiguousParse:
            print("ambiguous parse")                
        except ParseError as e:
            print("parse error:")
            print(e)
        except EOFError:
            break

driver()